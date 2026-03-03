#!/usr/bin/env python3
from modulo_d_pdf import encontrar_imagen_perfume

# Probar caso 1 Million (hombre)
resultado = encontrar_imagen_perfume('1 Million', 'Paco Rabanne', 'hombre', 'imagenes_temp')
if resultado:
    print(f'1 Million -> {resultado.name}')
else:
    print('1 Million -> No encontrado')

# Probar caso Lady Million (mujer)
resultado2 = encontrar_imagen_perfume('Lady Million', 'Paco Rabanne', 'mujer', 'imagenes_temp')
if resultado2:
    print(f'Lady Million -> {resultado2.name}')
else:
    print('Lady Million -> No encontrado')
