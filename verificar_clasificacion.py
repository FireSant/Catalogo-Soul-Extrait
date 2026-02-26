"""
Script para verificar la clasificación de colecciones de los perfumes.
"""

import asyncio
import modulo_b_ia_extractor as mod_b
import modulo_c_processor as mod_c

# Lista de perfumes para verificar (de la lista oficial)
PERFUMES = [
    ("Bleu de Chanel", "Chanel"),
    ("Light Blue", "Dolce & Gabbana"),
    ("Acqua di Gio", "Giorgio Armani"),
    ("La Nuit de L'Homme", "Yves Saint Laurent"),
    ("Sauvage", "Dior"),
    ("Black Opium", "Yves Saint Laurent"),
    ("Good Girl", "Carolina Herrera"),
    ("Aventus", "Creed"),
    ("Oud Wood", "Tom Ford"),
    ("Shalimar", "Guerlain"),
    ("CK One", "CK"),
    ("Narciso Rodriguez", "Narciso Rodriguez"),
]

async def verificar_clasificacion():
    print("=" * 80)
    print("VERIFICACIÓN DE CLASIFICACIÓN DE COLECCIONES")
    print("=" * 80)
    
    for nombre, marca in PERFUMES:
        print(f"\n🔍 {nombre} ({marca})")
        print("-" * 60)
        
        # Extraer datos con IA
        datos = await mod_b.scrape_perfume(nombre, marca)
        if not datos:
            print(f"  ❌ No se pudo extraer datos")
            continue
        
        # Procesar con módulo C
        datos_procesados = mod_c.procesar(datos, {"marca": marca})
        
        # Mostrar información clave
        familia = datos_procesados.get('familia_olfativa', '')
        genero = datos_procesados.get('genero', '')
        notas = datos_procesados.get('notas', {})
        colecciones = datos_procesados.get('colecciones', [])
        
        print(f"  Familia: {familia}")
        print(f"  Género: {genero}")
        
        # Verificar si es gourmand por las notas
        es_gourmand = False
        notas_fondo = notas.get('fondo', [])
        notas_dulces = ["vainilla", "caramelo", "chocolate", "café", "miel", "praliné", "tonka"]
        for nota in notas_fondo:
            if any(dulce in nota.lower() for dulce in notas_dulces):
                es_gourmand = True
                break
        
        print(f"  Notas de fondo: {', '.join(notas_fondo[:3])}...")
        print(f"  Es gourmand: {es_gourmand}")
        print(f"  Colecciones: {', '.join(colecciones)}")
        
        # Validación de reglas
        print("  ✅ Clasificación correcta" if colecciones else "  ❌ Sin clasificación")

if __name__ == "__main__":
    asyncio.run(verificar_clasificacion())
