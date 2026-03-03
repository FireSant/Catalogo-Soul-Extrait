#!/usr/bin/env python3
from modulo_d_pdf import encontrar_imagen_perfume

# Probar búsqueda de "Y" con marca "YSL"
resultado = encontrar_imagen_perfume('Y', 'YSL', 'mujer', 'imagenes_temp')
if resultado:
    print(f'Y + YSL -> {resultado.name}')
else:
    print('Y + YSL -> No encontrado')
