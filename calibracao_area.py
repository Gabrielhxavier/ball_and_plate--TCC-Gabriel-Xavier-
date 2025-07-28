import cv2

# Inicializa a câmera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)

print("[INFO] Clique com o botão esquerdo nos cantos da área útil da mesa.")
print("[INFO] Pressione ESC para sair.")

# Callback de clique
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordenada clicada: ({x}, {y})")

# Cria janela e associa função de clique
cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Mostra a imagem ao vivo
    cv2.imshow("Frame", frame)

    # Sai com tecla ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Libera recursos
cap.release()
cv2.destroyAllWindows()
