#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de generación de PDF con las nuevas ocasiones inferidas
"""

import modulo_c_processor as mod_c
import modulo_d_pdf as mod_d
from pathlib import Path

# Crear datos de prueba con diferentes tipos de perfumes
perfumes_test = [
    {
        'nombre': 'Citrus Splash',
        'marca': 'Test',
        'ml': '100',
        'notas': {
            'salida': ['Bergamota', 'Limón', 'Naranja'],
            'corazon': ['Lavanda', 'Jazmín'],
            'fondo': ['Sándalo', 'Musk']
        },
        'clima': {'primavera': 60, 'verano': 90, 'otono': 20, 'invierno': 5, 'dia': 85, 'noche': 15},
        'descripcion_corta': 'A fresh citrus fragrance perfect for the office and gym',
        'ocasiones_de_uso': ['day', 'casual']
    },
    {
        'nombre': 'Vanilla Dream',
        'marca': 'Sweet',
        'ml': '80',
        'notas': {
            'salida': ['Pera', 'Naranja'],
            'corazon': ['Vainilla', 'Jazmín', 'Chocolate'],
            'fondo': ['Vainilla', 'Caramelo', 'Miel']
        },
        'clima': {'primavera': 10, 'verano': 15, 'otono': 60, 'invierno': 85, 'dia': 25, 'noche': 90},
        'descripcion_corta': 'A sweet gourmand scent for romantic dates and cozy winter nights',
        'ocasiones_de_uso': ['night', 'romantic']
    },
    {
        'nombre': 'Leather Elite',
        'marca': 'Luxury',
        'ml': '100',
        'notas': {
            'salida': ['Cardamomo', 'Pimienta'],
            'corazon': ['Cuero', 'Tabaco', 'Oud'],
            'fondo': ['Cuero', 'Incienso', 'Sándalo']
        },
        'clima': {'primavera': 15, 'verano': 5, 'otono': 80, 'invierno': 75, 'dia': 30, 'noche': 85},
        'descripcion_corta': 'A sophisticated leather fragrance for formal events and elegant evenings',
        'ocasiones_de_uso': ['evening', 'formal']
    }
]

# Procesar los perfumes
resultados = []
for perfume in perfumes_test:
    fake_scraping = {
        'nombre': perfume['nombre'],
        'url': '',
        'notas': perfume['notas'],
        'clima': perfume['clima'],
        'imagen_path': None,
        'descripcion_corta': perfume['descripcion_corta'],
        'ocasiones_de_uso': perfume['ocasiones_de_uso']
    }
    fake_info = {'marca': perfume['marca'], 'ml': perfume['ml']}

    resultado = mod_c.procesar(fake_scraping, fake_info)
    resultados.append(resultado)

    print(f"\n{perfume['nombre']} - {perfume['marca']}")
    print(f"  Ocasiones: {resultado['ocasiones']}")
    print(f"  Estaciones: {[e['nombre'] for e in resultado['estaciones']]}")

# Generar PDF
output_path = Path("output/test_ocasiones_nuevas.pdf")
gen = mod_d.GeneradorCatalog(str(output_path))
gen.crear_portada()
gen.crear_indice(resultados)

for i, datos in enumerate(resultados):
    gen.agregar_perfume(datos, gen.items_indice[i])

gen.guardar()

print(f"\n✅ PDF generado: {output_path.absolute()}")
print(f"   El PDF muestra las nuevas ocasiones inferidas por el sistema mejorado")
