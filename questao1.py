import numpy as np
import cv2
import glob
import copy
import os

from rgb_ycbcr import rgb_para_ycbcr
from ycbcr_rgb import ycbcr_para_rgb
from pixel_vizinho import pega_pixel

# o endereço do meu diretório de imagens
path="C:\\Users\\Guilherme Braga\\Desktop\\ipi2\\*.bmp"

# leio todas as imagens
array_imagens = [cv2.imread(file) for file in glob.glob(path)]
numero_imagens = len(array_imagens)

# apenas para checar
print("Imagens lidas: ")
print(numero_imagens)

altura, largura, channels = array_imagens[0].shape
imagem_mediana = np.zeros((altura, largura), dtype = np.uint16)

# -------------------------------------------Y-------------------------------------------
# Gaussian Noise

for imagem in array_imagens:
    rgb_para_ycbcr(imagem)
    # acumulo os valores dos pixels em Y
    imagem_mediana = imagem_mediana + imagem[:, :, 0]

imagem_mediana = imagem_mediana/numero_imagens
cv2.imwrite("imagem_media_em_Y.bmp", imagem_mediana)

# colocamos esses novos Y junto do Cb e Cr que lemos, assim voltaremos a poder ter uma imagem RGB
media_colorida = array_imagens[0]
media_colorida[:, :, 0] = imagem_mediana

# auxiliar que sera juntado com as outras correcoes de imagens
aux_imagem = array_imagens[0]
aux_imagem[:, :, 0] = imagem_mediana

ycbcr_para_rgb(media_colorida)
cv2.imwrite("imagem_colorida_com_Y_medio.bmp", media_colorida)

# -------------------------------------------Cr-------------------------------------------
# corrigir ---> Crominance
# Salt and Pepper
auxiliar_com_borda = np.full((altura+2,largura+2), 255, dtype = np.uint8)
auxiliar_com_borda[1:-1, 1:-1] = aux_imagem[:, :, 2]

# molde com preto em volta para passar a mascara
# tem borda para possibilitar processamento
# se "K" é a nossa imagem e queremos passar um filtro 3x3,
# entao invadiremos a parte demarcada por "x", que agora existe arbitrariamente
# "Imagem"
#           xxx
#          xxxx
#         xxKKKKK   ...
#         xxKKKKK   ...
#         xxKKKKK   ...

for i in range(1, largura):
    for j in range(1, altura):
        pix_medio = pega_pixel(auxiliar_com_borda, i, j)
        pix_medio.sort()
        auxiliar_com_borda[i, j] = pix_medio[4]

imagem_mediana_CR = auxiliar_com_borda[1:-1, 1:-1]
cv2.imwrite("imagem_corrigida_em_Cr.bmp", imagem_mediana_CR)

# update do auxiliar
aux_imagem[:, :, 2] = imagem_mediana_CR

aux_imagem_Cr = copy.copy(aux_imagem)
ycbcr_para_rgb(aux_imagem_Cr)
cv2.imwrite("imagem_colorida_com_Cr_corrigido.bmp", aux_imagem_Cr)

# -------------------------------------------Cb-------------------------------------------
# corrigir ---> Crominance
# Frequencia indesejada
