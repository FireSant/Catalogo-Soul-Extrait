"""
Script para verificar que las notas de los perfumes coincidan con la referencia.
"""

import json
from pathlib import Path
import modulo_b_ia_extractor as mod_b
import modulo_c_processor as mod_c

REFERENCIA_PATH = Path("data/referencia_notas.json")
LISTA_PERFUMES_PATH = Path("data/lista_perfumes.csv")

def cargar_referencia():
    with open(REFERENCIA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_lista_perfumes():
    import csv
    perfumes = []
    with open(LISTA_PERFUMES_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            perfumes.append({
                "nombre": row["nombre"].strip(),
                "marca": row.get("marca", "").strip()
            })
    return perfumes

async def verificar_perfume(nombre, marca=""):
    """Extrae datos de un perfume y compara con la referencia."""
    print(f"\n{'='*60}")
    print(f"Verificando: {nombre} ({marca})")
    print(f"{'='*60}")

    # Extraer con IA
    datos = await mod_b.scrape_perfume(nombre, marca)
    if not datos:
        print("❌ No se pudo extraer datos")
        return None

    # Procesar con módulo C
    datos_procesados = mod_c.procesar(datos, {"marca": marca})

    # Cargar referencia
    referencia = cargar_referencia()
    ref = referencia.get(nombre)

    if not ref:
        print(f"⚠️  No hay referencia para {nombre}")
        return datos_procesados

    # Comparar notas
    notas_extraidas = datos_procesados["notas"]
    notas_referencia = ref["notas"]

    print("\n📋 NOTAS EXTRAÍDAS:")
    print(f"  Salida: {', '.join(notas_extraidas['salida'])}")
    print(f"  Corazón: {', '.join(notas_extraidas['corazon'])}")
    print(f"  Fondo: {', '.join(notas_extraidas['fondo'])}")

    print("\n📋 NOTAS DE REFERENCIA:")
    print(f"  Salida: {', '.join(notas_referencia['salida'])}")
    print(f"  Corazón: {', '.join(notas_referencia['corazon'])}")
    print(f"  Fondo: {', '.join(notas_referencia['fondo'])}")

    # Verificar coincidencia
    coinciden = (
        set(notas_extraidas["salida"]) == set(notas_referencia["salida"]) and
        set(notas_extraidas["corazon"]) == set(notas_referencia["corazon"]) and
        set(notas_extraidas["fondo"]) == set(notas_referencia["fondo"])
    )

    if coinciden:
        print("\n✅ NOTAS COINCIDEN EXACTAMENTE")
    else:
        print("\n❌ NOTAS NO COINCIDEN")
        # Mostrar diferencias
        for nivel in ["salida", "corazon", "fondo"]:
            extraidas = set(notas_extraidas[nivel])
            ref_set = set(notas_referencia[nivel])
            if extraidas != ref_set:
                faltan = ref_set - extraidas
                sobran = extraidas - ref_set
                if faltan:
                    print(f"  - Faltan en extraídas ({nivel}): {', '.join(faltan)}")
                if sobran:
                    print(f"  - Sobran en extraídas ({nivel}): {', '.join(sobran)}")

    print(f"\n📝 Descripción: {datos_procesados.get('descripcion', '')[:100]}...")
    print(f"🎯 Género: {datos_procesados.get('genero', '')}")
    print(f"🏷️  Familia: {datos_procesados.get('familia_olfativa', '')}")

    return datos_procesados

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Verificar notas de perfumes contra referencia")
    parser.add_argument("--todos", action="store_true", help="Verificar todos los perfumes de la lista")
    parser.add_argument("--perfume", type=str, help="Verificar un perfume específico")
    parser.add_argument("--marca", type=str, default="", help="Marca del perfume (opcional)")

    args = parser.parse_args()

    if args.perfume:
        await verificar_perfume(args.perfume, args.marca)
    elif args.todos:
        perfumes = cargar_lista_perfumes()
        resultados = []
        for p in perfumes:
            try:
                datos = await verificar_perfume(p["nombre"], p["marca"])
                if datos:
                    coinciden = "✅" if p["nombre"] in cargar_referencia() else "⚠️"
                    resultados.append((p["nombre"], coinciden))
            except Exception as e:
                print(f"❌ Error verificando {p['nombre']}: {e}")
                resultados.append((p["nombre"], "❌"))

        print(f"\n{'='*60}")
        print("RESUMEN")
        print(f"{'='*60}")
        for nombre, estado in resultados:
            print(f"{estado} {nombre}")
    else:
        parser.print_help()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
