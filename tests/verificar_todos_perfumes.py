#!/usr/bin/env python3
"""
Verificación completa de búsqueda de imágenes para todos los perfumes del CSV.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import csv
from modulo_d_pdf import encontrar_imagen_perfume

def verificar_todos():
    """Probar la búsqueda de imágenes para todos los perfumes del CSV."""
    csv_path = Path("data/lista_perfumes.csv")

    if not csv_path.exists():
        print(f"Error: No se encuentra {csv_path}")
        return

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        perfumes = list(reader)

    print("=" * 80)
    print("VERIFICACIÓN DE IMÁGENES PARA TODOS LOS PERFUMES DEL CSV")
    print("=" * 80)
    print(f"Total de perfumes: {len(perfumes)}")
    print()

    resultados = []
    for perfume in perfumes:
        nombre = perfume["nombre"]
        marca = perfume["marca"]
        genero = perfume["genero"]

        img_path = encontrar_imagen_perfume(nombre, marca, genero, 'imagenes_temp')

        if img_path:
            resultados.append({
                'nombre': nombre,
                'marca': marca,
                'genero': genero,
                'imagen': img_path.name,
                'ok': True
            })
        else:
            resultados.append({
                'nombre': nombre,
                'marca': marca,
                'genero': genero,
                'imagen': 'NO ENCONTRADO',
                'ok': False
            })

    # Mostrar resumen
    encontrados = sum(1 for r in resultados if r['ok'])
    no_encontrados = len(resultados) - encontrados

    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Encontrados: {encontrados}/{len(resultados)}")
    print(f"No encontrados: {no_encontrados}/{len(resultados)}")
    print()

    # Mostrar detalles
    print("\nDETALLES:")
    print("-" * 80)

    # Ordenar por nombre
    resultados.sort(key=lambda x: x['nombre'])

    for r in resultados:
        status = "✓" if r['ok'] else "✗"
        print(f"{status} {r['nombre'][:30]:30} | {r['marca'][:20]:20} | {r['genero'][:10]:10} → {r['imagen'][:40]}")

    # Guardar log en archivo
    log_path = Path("log_verificacion_imagenes.txt")
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write("VERIFICACIÓN DE IMÁGENES\n")
        log.write(f"Total: {len(resultados)}\n")
        log.write(f"Encontrados: {encontrados}\n")
        log.write(f"No encontrados: {no_encontrados}\n\n")
        for r in resultados:
            log.write(f"{r['nombre']},{r['marca']},{r['genero']},{r['imagen']}\n")

    print(f"\nLog guardado en: {log_path}")

if __name__ == "__main__":
    verificar_todos()
