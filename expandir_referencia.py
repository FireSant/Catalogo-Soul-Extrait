"""
Script para expandir la base de datos de referencia con notas reales de perfumes.
"""

import json
import asyncio
from pathlib import Path
import csv
import modulo_b_ia_extractor as mod_b

REFERENCIA_PATH = Path("data/referencia_notas.json")
LISTA_PERFUMES_PATH = Path("data/lista_perfumes.csv")

def cargar_referencia():
    if REFERENCIA_PATH.exists():
        with open(REFERENCIA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_referencia(ref):
    with open(REFERENCIA_PATH, "w", encoding="utf-8") as f:
        json.dump(ref, f, indent=2, ensure_ascii=False)
    print(f"✅ Referencia guardada: {len(ref)} perfumes")

def cargar_lista_perfumes():
    perfumes = []
    with open(LISTA_PERFUMES_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            perfumes.append({
                "nombre": row["nombre"].strip(),
                "marca": row.get("marca", "").strip()
            })
    return perfumes

async def extraer_notas_perfume(nombre, marca=""):
    """Extrae notas de un perfume usando el módulo B."""
    print(f"  Extrayendo {nombre}...")
    datos = await mod_b.scrape_perfume(nombre, marca)
    if datos:
        return {
            "notas": datos["notas"],
            "genero": datos["genero"],
            "familia_olfativa": datos["familia_olfativa"]
        }
    return None

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Expandir base de datos de referencia")
    parser.add_argument("--todos", action="store_true", help="Extraer todos los perfumes de la lista")
    parser.add_argument("--perfume", type=str, help="Extraer un perfume específico")
    parser.add_argument("--marca", type=str, default="", help="Marca del perfume (opcional)")
    parser.add_argument("--forzar", action="store_true", help="Forzar extracción aunque ya exista en referencia")

    args = parser.parse_args()

    referencia = cargar_referencia()
    perfumes = cargar_lista_perfumes()

    if args.perfume:
        # Extraer un perfume específico
        nombre = args.perfume
        if nombre in referencia and not args.forzar:
            print(f"⚠️  {nombre} ya existe en la referencia. Use --forzar para sobrescribir.")
            return

        datos = await extraer_notas_perfume(nombre, args.marca)
        if datos:
            referencia[nombre] = datos
            guardar_referencia(referencia)
            print(f"✅ Añadido {nombre} a la referencia")
        else:
            print(f"❌ No se pudo extraer {nombre}")

    elif args.todos:
        # Extraer todos los perfumes de la lista
        nuevos = 0
        for p in perfumes:
            nombre = p["nombre"]
            marca = p["marca"]

            if nombre in referencia and not args.forzar:
                print(f"⏭️  {nombre} ya existe (saltando)")
                continue

            datos = await extraer_notas_perfume(nombre, marca)
            if datos:
                referencia[nombre] = datos
                nuevos += 1
                # Guardar progreso cada 5 perfumes
                if nuevos % 5 == 0:
                    guardar_referencia(referencia)
            else:
                print(f"❌ Falló extracción de {nombre}")

        guardar_referencia(referencia)
        print(f"\n✅ Proceso completado. Se añadieron {nuevos} nuevos perfumes.")
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
