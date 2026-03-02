#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba del sistema mejorado de estaciones y ocasiones
"""

import modulo_c_processor as mod_c
import json

# Prueba 1: Perfume cítrico-fresco (debería dar Verano/Primavera + Citas/Oficina/Gimnasio)
fake_scraping1 = {
    'nombre': 'Aqua di Gio',
    'url': '',
    'notas': {
        'salida': ['Bergamota', 'Naranja', 'Limón'],
        'corazon': ['Jazmín', 'Lavanda'],
        'fondo': ['Sándalo', 'Musk']
    },
    'clima': {
        'primavera': 60, 'verano': 90, 'otono': 20, 'invierno': 5,
        'dia': 85, 'noche': 15
    },
    'imagen_path': None,
    'descripcion_corta': 'A fresh and elegant citrus fragrance perfect for daily wear',
    'ocasiones_de_uso': ['day', 'casual']
}

fake_info1 = {'marca': 'Armani', 'ml': '100'}

resultado1 = mod_c.procesar(fake_scraping1, fake_info1)

print('=== PRUEBA 1: Perfume Cítrico-Fresco ===')
print(f'Estaciones: {resultado1["estaciones"]}')
print(f'Ocasiones: {resultado1["ocasiones"]}')
print(f'Colecciones: {resultado1["colecciones"]}')
print()

# Prueba 2: Perfume gourmand-oriental (debería dar Invierno/Noche + Citas/Evento Formal)
fake_scraping2 = {
    'nombre': 'Black Opium',
    'url': '',
    'notas': {
        'salida': ['Pera', 'Naranja', 'Café'],
        'corazon': ['Jazmín', 'Rosa', 'Vainilla'],
        'fondo': ['Vainilla', 'Pachulí', 'Chocolate', 'Miel']
    },
    'clima': {
        'primavera': 10, 'verano': 15, 'otono': 60, 'invierno': 85,
        'dia': 25, 'noche': 90
    },
    'imagen_path': None,
    'descripcion_corta': 'An intense oriental gourmand fragrance for romantic evenings',
    'ocasiones_de_uso': ['night', 'romantic']
}

fake_info2 = {'marca': 'YSL', 'ml': '90'}

resultado2 = mod_c.procesar(fake_scraping2, fake_info2)

print('=== PRUEBA 2: Perfume Gourmand-Oriental ===')
print(f'Estaciones: {resultado2["estaciones"]}')
print(f'Ocasiones: {resultado2["ocasiones"]}')
print(f'Colecciones: {resultado2["colecciones"]}')
print()

# Prueba 3: Perfume amaderado-cuero (debería dar Otoño/Invierno + Evento Formal)
fake_scraping3 = {
    'nombre': 'Tom Ford Ombré Leather',
    'url': '',
    'notas': {
        'salida': ['Cardamomo', 'Jazmín'],
        'corazon': ['Cuero', 'Flor de Azahar'],
        'fondo': ['Cuero', 'Vainilla', 'Ámbar']
    },
    'clima': {
        'primavera': 15, 'verano': 5, 'otono': 80, 'invierno': 75,
        'dia': 30, 'noche': 85
    },
    'imagen_path': None,
    'descripcion_corta': 'A sophisticated leather fragrance for formal events',
    'ocasiones_de_uso': ['evening', 'formal']
}

fake_info3 = {'marca': 'Tom Ford', 'ml': '100'}

resultado3 = mod_c.procesar(fake_scraping3, fake_info3)

print('=== PRUEBA 3: Perfume Amaderado-Cuero ===')
print(f'Estaciones: {resultado3["estaciones"]}')
print(f'Ocasiones: {resultado3["ocasiones"]}')
print(f'Colecciones: {resultado3["colecciones"]}')
print()

# Prueba 4: Perfume sin ocasiones de IA (debería inferir completamente)
fake_scraping4 = {
    'nombre': 'Test Perfume',
    'url': '',
    'notas': {
        'salida': ['Bergamota'],
        'corazon': ['Rosa'],
        'fondo': ['Vainilla']
    },
    'clima': {
        'primavera': 80, 'verano': 90, 'otono': 40, 'invierno': 10,
        'dia': 95, 'noche': 20
    },
    'imagen_path': None,
    'descripcion_corta': 'Una fragancia fresca y elegante',
}

fake_info4 = {'marca': 'Test Brand', 'ml': '100'}

resultado4 = mod_c.procesar(fake_scraping4, fake_info4)

print('=== PRUEBA 4: Perfume sin Ocasiones de IA (inferencia completa) ===')
print(f'Estaciones: {resultado4["estaciones"]}')
print(f'Ocasiones: {resultado4["ocasiones"]}')
print(f'Colecciones: {resultado4["colecciones"]}')
print()

print('✅ Todas las pruebas completadas exitosamente')
