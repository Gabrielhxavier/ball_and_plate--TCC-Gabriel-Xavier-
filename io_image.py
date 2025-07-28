import os
import cv2

# Caminho do arquivo com formato correto
image_path = os.path.join('C:\\Users\Gabriel\\Desktop\\TCC Ball and Beam\\Open CV curso\\Data','teste.png')

img = cv2.imread(image_path)

k_size = 7
img_blur = cv2.blur(img, (k_size, k_size))
img_gaussian_blur = cv2.GaussianBlur(img, (k_size, k_size), 5)
img_median_blur = cv2.medianBlur(img, k_size)

cv2.imshow('img', img)
cv2.imshow('img_blur', img_blur)
cv2.imshow('img_gaussian_blur', img_gaussian_blur)
cv2.imshow('img_median_blur', img_median_blur)
cv2.waitKey(0)