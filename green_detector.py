import cv2
import numpy as np
import serial
import json
import os

# --- CONFIGURAÇÕES GERAIS ---
ball_lower = np.array([58, 80, 33])       # HSV inferior da bola
ball_upper = np.array([119, 243, 113])     # HSV superior da bola

mesa_x_mm = 225
mesa_y_mm = 173

calibration_file = "calibracao.json"

# --- CARREGAMENTO DA CALIBRAÇÃO ---
if not os.path.exists(calibration_file):
    print("[ERRO] Arquivo de calibração não encontrado.")
    exit()

with open(calibration_file, "r") as f:
    data = json.load(f)
    xmin, ymin, xmax, ymax = data["xmin"], data["ymin"], data["xmax"], data["ymax"]
    print("[INFO] Calibração carregada:", (xmin, ymin, xmax, ymax))

# --- INICIALIZA A CÂMERA ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)

# --- INICIALIZA SERIAL COM A ESP32 ---
try:
    ser = serial.Serial('COM3', 115200, timeout=1)
    print("[INFO] Porta serial aberta com sucesso.")
except Exception as e:
    print("[ERRO] Não foi possível abrir a porta serial:", e)
    ser = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.blur(frame, (1, 10))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    ball_mask = cv2.inRange(hsv, ball_lower, ball_upper)
    ball_mask = cv2.morphologyEx(ball_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ball_mask = cv2.morphologyEx(ball_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > 50:
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Normalização
                cx_norm = (cx - xmin) / (xmax - xmin)
                cy_norm = (cy - ymin) / (ymax - ymin)

                # Conversão (Y invertido)
                real_x = cx_norm * mesa_x_mm
                real_y = (1.0 - cy_norm) * mesa_y_mm  # Inversão do Y

                # Envia para ESP32
                if ser and ser.is_open:
                    mensagem = f"{real_x:.1f},{real_y:.1f}\n"
                    ser.write(mensagem.encode())
                    print(f"[ENVIO] {mensagem.strip()}")

                # Exibição
                cv2.circle(frame, (cx, cy), 10, (0, 0, 255), -1)
                cv2.putText(frame, f"({cx},{cy})", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(frame, f"{real_x:.1f} mm, {real_y:.1f} mm", (cx + 10, cy + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Desenha área calibrada
    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
    cv2.putText(frame, "AREA CALIBRADA", (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Ball Mask", ball_mask)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# --- FINALIZAÇÃO ---
cap.release()
cv2.destroyAllWindows()
if ser and ser.is_open:
    ser.close()
