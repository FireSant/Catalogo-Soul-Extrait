#!/usr/bin/env python
"""
Prueba de extracción de datos con OpenRouter (sin imágenes)
"""
import asyncio
import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from modulo_b_ia_extractor import scrape_perfume

async def probar_extraccion():
    """Prueba con perfumes famosos para extraer fichas técnicas"""

    # Lista de perfumes famosos
    perfumes_test = [
        ("Chanel No. 5", "Chanel"),
        ("Dior J'adore", "Dior"),
        ("Flower by Kenzo", "Kenzo"),
        ("Lancôme La Vie Est Belle", "Lancôme"),
        ("Gucci Bloom", "Gucci"),
    ]

    print("=" * 60)
    print("PRUEBA DE EXTRACCIÓN DE DATOS (OpenRouter)")
    print("=" * 60)

    resultados = []

    for nombre, marca in perfumes_test:
        print(f"\nProbando: {nombre} ({marca})")
        print("-" * 60)

        resultado = await scrape_perfume(nombre, marca)

        if resultado:
            print(f"OK Ficha extraida: {nombre}")
            print(f"   Género: {resultado.get('genero')}")
            print(f"   Imagen path: {resultado.get('imagen_path')} (será asignado manualmente)")
            print(f"   URL: {resultado.get('url', '')[:80] if resultado.get('url') else 'N/A'}")

            # Verificar descripción en español
            descripcion = resultado.get('descripcion_corta', '')
            if descripcion:
                print(f"   Descripción: {descripcion[:100]}...")
                # Detectar si contiene caracteres españoles
                tiene_acentos = any(c in descripcion for c in 'áéíóúüñÁÉÍÓÚÜÑ')
                if not tiene_acentos:
                    print(f"   WARNING: Descripción podría no estar en español (sin acentos)")
            else:
                print("   WARNING: No hay descripción")

            # Verificar notas
            notas = resultado.get('notas', {})
            total_notas = sum(len(notas.get(nivel, [])) for nivel in ('salida', 'corazon', 'fondo'))
            print(f"   Notas totales: {total_notas}")

            resultados.append({
                'nombre': nombre,
                'marca': marca,
                'genero': resultado.get('genero'),
                'descripcion': bool(descripcion),
                'notas': total_notas,
            })
        else:
            print(f"ERROR extrayendo datos de {nombre}")
            resultados.append({
                'nombre': nombre,
                'marca': marca,
                'genero': False,
                'descripcion': False,
                'notas': 0,
            })

    print("\n" + "=" * 60)
    print("ESTADÍSTICAS")
    print("=" * 60)
    total = len(resultados)
    con_datos = sum(1 for r in resultados if r['descripcion'] and r['notas'] > 0)
    print(f"Perfumes probados: {total}")
    print(f"Con datos completos (descripción + notas): {con_datos}/{total}")

    if con_datos == 0:
        print("\nERROR CRÍTICO: No se extrajo ningún dato completo!")
        print("Posibles causas:")
        print("  - OpenRouter API no configurada (OPENROUTER_API_KEY)")
        print("  - Problemas de red o cuota agotada")
    else:
        print("\nÉXITO: El sistema de extracción está funcionando correctamente.")

    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(probar_extraccion())
