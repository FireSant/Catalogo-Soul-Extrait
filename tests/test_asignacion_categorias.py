#!/usr/bin/env python3
"""
Test para verificar la asignación de colecciones (categorías) y sus puntuaciones
para todos los perfumes en lista_perfumes.csv utilizando referencia_notas.json.
"""

import sys
from pathlib import Path
import csv
import json

# Agregar el directorio raíz al path para importar módulos
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from modulo_c_processor import _derivar_colecciones

def calcular_puntuaciones(familia_olfativa: str, genero: str, notas: dict, nombre: str = "", descripcion: str = "") -> dict:
    """
    Copia exacta de la lógica de puntuación de _derivar_colecciones para poder ver los puntajes.
    """
    puntuaciones = {
        "Frescura y Vitalidad": 0,
        "Noche y Seducción": 0,
        "Elegancia e Intensidad": 0
    }
    
    familia_lower = (familia_olfativa or "").lower()
    genero_lower = (genero or "").lower()
    nombre_lower = (nombre or "").lower()
    
    todas_notas = []
    for nivel in ["salida", "corazon", "fondo"]:
        notas_nivel = notas.get(nivel, [])
        if isinstance(notas_nivel, list):
            todas_notas.extend([n.lower() if isinstance(n, str) else str(n).lower() for n in notas_nivel])
        elif isinstance(notas_nivel, str):
            todas_notas.append(notas_nivel.lower())
    
    descripcion_lower = (descripcion or "").lower()
    
    # 1. Frescura y Vitalidad
    keywords_familia_frescura = ["cítrico", "citico", "acuático", "marino", "ozónico", "verde", "frutal", "aromático"]
    keywords_no_frescura = ["oriental", "ambar", "gourmand", "chypre", "cuero", "fougere", "especiado"]
    if any(keyword in familia_lower for keyword in keywords_familia_frescura):
        if not any(keyword in familia_lower for keyword in keywords_no_frescura):
            puntuaciones["Frescura y Vitalidad"] += 2
            
    keywords_notas_frescura = ["limón", "limon", "bergamota", "menta", "naranja", "neroli", "pomelo", "mandarina", "toronja", "yuzu", "marina", "marinas", "marino", "acuático", "acuáticas", "verde", "verdes", "manzana", "sal marina"]
    for nota in todas_notas:
        if any(keyword in nota for keyword in keywords_notas_frescura):
            puntuaciones["Frescura y Vitalidad"] += 1
            
    keywords_descripcion_frescura = ["fresco", "fresca", "frescura", "vitalidad", "ligero", "ligera", "suave", "acuático", "marino", "verano", "día", "clima cálido", "calor"]
    if any(keyword in descripcion_lower for keyword in keywords_descripcion_frescura):
        puntuaciones["Frescura y Vitalidad"] += 1
        
    keywords_penalizacion = ["cuero", "tabaco", "oud"]
    if any(keyword in nota for nota in todas_notas for keyword in keywords_penalizacion):
        puntuaciones["Frescura y Vitalidad"] -= 5
        
    keywords_contradiccion_frescura = ["intenso", "intensa", "seductor", "seductora", "seducción", "noche", "nocturno", "corazón especiado", "misterioso", "oscuro", "fiesta", "evento"]
    if any(keyword in descripcion_lower for keyword in keywords_contradiccion_frescura):
        puntuaciones["Frescura y Vitalidad"] -= 2
        
    # 2. Noche y Seducción
    keywords_familia_noche = ["oriental", "ámbar", "ambar", "gourmand", "especiado"]
    if any(keyword in familia_lower for keyword in keywords_familia_noche):
        puntuaciones["Noche y Seducción"] += 2
        
    keywords_notas_noche = ["vainilla", "haba tonka", "tonka", "caramelo", "chocolate", "miel", "praliné"]
    for nota in todas_notas:
        if any(keyword in nota for keyword in keywords_notas_noche):
            puntuaciones["Noche y Seducción"] += 1
            
    keywords_nombre_noche = ["intense", "extreme", "night", "nuit", "elixir"]
    if any(keyword in nombre_lower for keyword in keywords_nombre_noche):
        puntuaciones["Noche y Seducción"] += 1
        
    keywords_descripcion_noche = ["noche", "nocturno", "seductor", "seducción", "misterioso", "intenso", "fiesta", "evento", "cita", "romántico", "romance", "tarde", "evening"]
    if any(keyword in descripcion_lower for keyword in keywords_descripcion_noche):
        puntuaciones["Noche y Seducción"] += 1
        
    # 3. Elegancia e Intensidad
    keywords_familia_elegancia = ["amaderado", "madera", "chypre", "cuero", "fougere"]
    if any(keyword in familia_lower for keyword in keywords_familia_elegancia):
        puntuaciones["Elegancia e Intensidad"] += 2
        
    keywords_notas_elegancia = ["sándalo", "cedro", "oud", "incienso", "vetiver", "pachulí", "patchouli", "musgo de roble", "musgo", "gaiac", "guayaco"]
    for nota in todas_notas:
        if any(keyword in nota for keyword in keywords_notas_elegancia):
            puntuaciones["Elegancia e Intensidad"] += 1
            
    if genero_lower == "unisex":
        puntuaciones["Elegancia e Intensidad"] += 2
        
    keywords_descripcion_elegancia = ["elegancia", "elegante", "intenso", "intensidad", "sofisticado", "clásico", "premium", "lujo", "poderoso", "fuerte", "duradero", "proyección", "amaderado", "madera", "cuero", "fougere", "oriental", "gourmand", "especiado"]
    if any(keyword in descripcion_lower for keyword in keywords_descripcion_elegancia):
        puntuaciones["Elegancia e Intensidad"] += 1

    return puntuaciones


def verificar_categorias():
    csv_path = Path("data/cache_scrapeados.csv")

    if not csv_path.exists():
        print(f"Error: No se encuentra {csv_path}")
        return

    # Cargar lista de perfumes scrapeados reales
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        perfumes = list(reader)

    print("=" * 100)
    print("VERIFICACIÓN DE ASIGNACIÓN DE CATEGORÍAS (COLECCIONES) CON CACHE SCRAPEADO")
    print("=" * 100)
    print(f"Total de perfumes en cache: {len(perfumes)}")
    print()

    resultados = []

    for perfume in perfumes:
        nombre = perfume.get("nombre", "")
        genero = perfume.get("genero", "")
        familia_olfativa = perfume.get("familia_olfativa", "")
        descripcion = perfume.get("descripcion", "")
        
        # Parseamos las notas desde el string extraido por el scraper
        notas = {
            "salida": perfume.get("notas_salida", "").split("|") if perfume.get("notas_salida") else [],
            "corazon": perfume.get("notas_corazon", "").split("|") if perfume.get("notas_corazon") else [],
            "fondo": perfume.get("notas_fondo", "").split("|") if perfume.get("notas_fondo") else []
        }
            
        puntuaciones = calcular_puntuaciones(
            familia_olfativa=familia_olfativa,
            genero=genero,
            notas=notas,
            nombre=nombre,
            descripcion=descripcion
        )
        
        colecciones_finales = _derivar_colecciones(
            familia_olfativa=familia_olfativa,
            genero=genero,
            notas=notas,
            nombre=nombre,
            descripcion=descripcion
        )
        
        resultados.append({
            "nombre": nombre,
            "genero": genero,
            "familia": familia_olfativa,
            "puntuaciones": puntuaciones,
            "asignacion": colecciones_finales
        })

    # Mostrar resumen por consola
    print(f"{'PERFUME':<30} | {'FRES/VIT':<8} | {'NOCH/SED':<8} | {'ELEG/INT':<8} | ASIGNACIÓN FINAL")
    print("-" * 100)
    
    for r in resultados:
        pts = r['puntuaciones']
        asig = ", ".join(r['asignacion'])
        print(f"{r['nombre'][:30]:<30} | {pts['Frescura y Vitalidad']:<8} | {pts['Noche y Seducción']:<8} | {pts['Elegancia e Intensidad']:<8} | {asig}")

    # Guardar log en archivo
    log_path = Path("log_verificacion_categorias.txt")
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write("VERIFICACIÓN DE ASIGNACIÓN DE CATEGORÍAS\n")
        log.write("=" * 80 + "\n")
        for r in resultados:
            pts = r['puntuaciones']
            log.write(f"\nPerfume: {r['nombre']} ({r['genero']})\n")
            log.write(f"Familia Olfativa: {r['familia']}\n")
            log.write(f"Puntuaciones:\n")
            log.write(f"  - Frescura y Vitalidad: {pts['Frescura y Vitalidad']}\n")
            log.write(f"  - Noche y Seducción: {pts['Noche y Seducción']}\n")
            log.write(f"  - Elegancia e Intensidad: {pts['Elegancia e Intensidad']}\n")
            log.write(f"Asignación Final: {', '.join(r['asignacion'])}\n")
            
    print(f"\nLog detallado guardado en: {log_path}")

if __name__ == "__main__":
    verificar_categorias()
