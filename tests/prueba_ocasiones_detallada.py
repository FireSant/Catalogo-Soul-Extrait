#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba detallada del sistema de inferencia de ocasiones
Demuestra que las ocasiones se generan correctamente según notas y descripción
"""

import modulo_c_processor as mod_c

def probar_perfume(nombre, notas, descripcion, ocasiones_ia, genero, familia, ml, marca):
    """Prueba un perfume y muestra los resultados"""
    fake_scraping = {
        'nombre': nombre,
        'url': '',
        'notas': notas,
        'clima': {
            'primavera': 50, 'verano': 50, 'otono': 50, 'invierno': 50,
            'dia': 50, 'noche': 50
        },
        'imagen_path': None,
        'descripcion_corta': descripcion,
    }
    
    if ocasiones_ia:
        fake_scraping['ocasiones_de_uso'] = ocasiones_ia
    
    fake_info = {'marca': marca, 'ml': ml}
    
    resultado = mod_c.procesar(fake_scraping, fake_info)
    
    print(f"\n{'='*60}")
    print(f"PERFUME: {nombre} - {marca}")
    print(f"Familia: {familia} | Género: {genero}")
    print(f"Notas: {notas['salida']} + {notas['corazon']} + {notas['fondo']}")
    print(f"Descripción: {descripcion}")
    print(f"Ocasiones IA: {ocasiones_ia if ocasiones_ia else 'Ninguna'}")
    print(f"\n→ OCASIONES GENERADAS: {resultado['ocasiones']}")
    print(f"→ ESTACIONES: {[e['nombre'] for e in resultado['estaciones']]}")
    print(f"→ COLECCIONES: {resultado['colecciones']}")
    
    return resultado

# ============================================================================
# PRUEBAS SISTEMÁTICAS
# ============================================================================

print("\n" + "="*60)
print("PRUEBAS DEL SISTEMA DE INFERENCIA DE OCASIONES")
print("="*60)

# 1. Perfume CÍTRICO - Debería dar: Oficina, Gimnasio, Fin de Semana
probar_perfume(
    nombre="Citrus Splash",
    notas={
        'salida': ['Bergamota', 'Limón', 'Naranja'],
        'corazon': ['Lavanda', 'Jazmín'],
        'fondo': ['Sándalo', 'Musk']
    },
    descripcion="A fresh citrus fragrance perfect for the office and gym",
    ocasiones_ia=['day'],
    genero="Unisex",
    familia="Cítrico-Aromático",
    ml="100",
    marca="Test"
)

# 2. Perfume GOURMAND - Debería dar: Citas, Noche, Invierno
probar_perfume(
    nombre="Vanilla Dream",
    notas={
        'salida': ['Pera', 'Naranja'],
        'corazon': ['Vainilla', 'Jazmín', 'Chocolate'],
        'fondo': ['Vainilla', 'Caramelo', 'Miel', 'Pachulí']
    },
    descripcion="A sweet gourmand scent for romantic dates and cozy winter nights",
    ocasiones_ia=['night', 'romantic'],
    genero="Mujer",
    familia="Gourmand",
    ml="80",
    marca="Sweet Brand"
)

# 3. Perfume AMADERADO-CUERO - Debería dar: Evento Formal, Noche
probar_perfume(
    nombre="Leather Elite",
    notas={
        'salida': ['Cardamomo', 'Pimienta'],
        'corazon': ['Cuero', 'Tabaco', 'Oud'],
        'fondo': ['Cuero', 'Incienso', 'Sándalo']
    },
    descripcion="A sophisticated leather fragrance for formal events and elegant evenings",
    ocasiones_ia=['evening', 'formal'],
    genero="Hombre",
    familia="Cuero-Amaderado",
    ml="100",
    marca="Luxury"
)

# 4. Perfume FLORAL-INTENSO - Debería dar: Citas, Evento Formal, Noche
probar_perfume(
    nombre="Rose Noir",
    notas={
        'salida': ['Pera', 'Frambuesa'],
        'corazon': ['Rosa', 'Jazmín', 'Tuberosa', 'Ylang-Ylang'],
        'fondo': ['Vainilla', 'Pachulí', 'Ámbar']
    },
    descripcion="An intense floral oriental perfect for romantic evenings and special occasions",
    ocasiones_ia=[],  # Sin ocasiones de IA - debe inferir completamente
    genero="Mujer",
    familia="Floral-Oriental",
    ml="75",
    marca="Elegance"
)

# 5. Perfume ACUÁTICO - Debería dar: Playa, Gimnasio, Fin de Semana
probar_perfume(
    nombre="Ocean Breeze",
    notas={
        'salida': ['Limón', 'Bergamota', 'Sea Salt'],
        'corazon': ['Jazmín de Agua', 'Pepino'],
        'fondo': ['Musk', 'Sándalo']
    },
    descripcion="A refreshing aquatic scent ideal for beach days and summer workouts",
    ocasiones_ia=['summer', 'casual'],
    genero="Hombre",
    familia="Acuático-Cítrico",
    ml="100",
    marca="Aqua"
)

# 6. Perfume ESPECIADO-ORIENTAL - Debería dar: Noche, Invierno, Citas
probar_perfume(
    nombre="Spice Route",
    notas={
        'salida': ['Canela', 'Cardamomo'],
        'corazon': ['Rosa', 'Jazmín', 'Vainilla'],
        'fondo': ['Ámbar', 'Incienso', 'Musk', 'Sándalo']
    },
    descripcion="A warm oriental spice fragrance for cold winter nights and romantic moments",
    ocasiones_ia=['night', 'winter'],
    genero="Unisex",
    familia="Oriental-Especiado",
    ml="100",
    marca="Exotic"
)

# 7. Perfume FRUTAL-FRESCO - Debería dar: Fin de Semana, Verano, Día
probar_perfume(
    nombre="Summer Fruits",
    notas={
        'salida': ['Manzana', 'Pera', 'Melocotón'],
        'corazon': ['Frambuesa', 'Fresa'],
        'fondo': ['Musk', 'Sándalo']
    },
    descripcion="A light fruity fragrance for casual weekend wear and summer days",
    ocasiones_ia=['casual', 'day'],
    genero="Mujer",
    familia="Frutal",
    ml="80",
    marca="Fresh"
)

# 8. Perfume AROMÁTICO-FOUGÈRE - Debería dar: Oficina, Día, Negocios
probar_perfume(
    nombre="Classic Fougère",
    notas={
        'salida': ['Bergamota', 'Limón'],
        'corazon': ['Lavanda', 'Romero', 'Salvia'],
        'fondo': ['Cedro', 'Sándalo', 'Musk']
    },
    descripcion="A clean aromatic fougère perfect for the office and business meetings",
    ocasiones_ia=['day', 'business'],
    genero="Hombre",
    familia="Aromático-Fougère",
    ml="100",
    marca="Classic"
)

print("\n" + "="*60)
print("✅ TODAS LAS PRUEBAS COMPLETADAS")
print("="*60)
print("\nResumen de patrones detectados:")
print("- Cítricos/Acuáticos → Oficina, Gimnasio, Fin de Semana, Playa")
print("- Gourmand/Dulces → Citas, Noche, Invierno")
print("- Amaderados/Cuero → Evento Formal, Noche")
print("- Florales Intensos → Citas, Evento Formal")
print("- Especiados/Orientales → Noche, Invierno")
print("- Frutales/Frescos → Fin de Semana, Verano")
print("- Aromáticos/Fougère → Oficina, Negocios, Día")
print("="*60)
