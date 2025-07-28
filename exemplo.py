import os
import cv2
import numpy as np

# Caminho do diretório de saída
output_dir = 'C:\\Users\\Gabriel\\Desktop\\TCC Ball and Beam\\Open CV curso\\Data1'
image_path = os.path.join(output_dir, 'exemplo.png')

# Carrega imagem
img = cv2.imread(image_path)
overlay = img.copy()

# Etapa 1: Conversão para HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imwrite(os.path.join(output_dir, 'etapa1_hsv_visualizacao.png'), cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))  # visualização

# Etapa 2: Segmentação do branco
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 40, 255])
mask = cv2.inRange(hsv, lower_white, upper_white)
cv2.imwrite(os.path.join(output_dir, 'etapa2_mascara_branca.png'), mask)

# Etapa 2B (NOVO): Sobreposição da máscara com a imagem original
mask_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
highlight = np.zeros_like(mask_color)
highlight[np.where(mask == 255)] = (255, 200, 100)  # azul claro
sobreposicao = cv2.addWeighted(img, 0.7, highlight, 0.3, 0)
cv2.imwrite(os.path.join(output_dir, 'etapa2b_mascara_sobreposta.png'), sobreposicao)

# Etapa 3: Morfologia
kernel = np.ones((11, 11), np.uint8)
mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
cv2.imwrite(os.path.join(output_dir, 'etapa3_morfologia.png'), mask_clean)

# Etapa 4: Contornos e retângulo
contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

contornos_validos = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    area = cv2.contourArea(cnt)
    if area > 500 and h > w * 1.5:
        contornos_validos.append(cnt)

if contornos_validos:
    pontos = np.vstack(contornos_validos)
    rect = cv2.minAreaRect(pontos)
    box = cv2.boxPoints(rect)
    box = np.intp(box)

    # Preenche suavemente o retângulo rotacionado
    cv2.drawContours(overlay, [box], 0, (255, 200, 100), -1)
    resultado = cv2.addWeighted(overlay, 0.3, img, 0.7, 0)

    # Desenha contorno
    cv2.drawContours(resultado, [box], 0, (255, 200, 100), 2)
else:
    resultado = img.copy()

# Etapa 5: Resultado final
cv2.imwrite(os.path.join(output_dir, 'etapa4_resultado_final.png'), resultado)

# Exibe imagem final
cv2.imshow("Faixa com retângulo rotacionado", resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()
