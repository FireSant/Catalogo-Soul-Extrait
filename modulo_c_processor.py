"""
Módulo C: Procesador de Datos — Soul Extrait
============================================
Responsabilidades:
  1. Traducir/normalizar notas olfativas (inglés → español)
  2. Aplicar lógica de negocio:
     - Determinar estación dominante (porcentaje > umbral → icono)
     - Determinar momento del día dominante
  3. Formatear el nombre del perfume para el catálogo
  4. Retornar un dict limpio y listo para el Módulo D (PDF)
"""

import json
from pathlib import Path
import math

from loguru import logger

# Cargar base de datos de referencia de notas reales
REFERENCIA_NOTAS_PATH = Path("data/referencia_notas.json")
referencia_notas_c = {}
try:
    if REFERENCIA_NOTAS_PATH.exists():
        with open(REFERENCIA_NOTAS_PATH, "r", encoding="utf-8") as f:
            referencia_notas_c = json.load(f)
        logger.info(f"Módulo C: Cargada referencia de notas para {len(referencia_notas_c)} perfumes")
    else:
        logger.warning(f"Módulo C: Archivo de referencia no encontrado: {REFERENCIA_NOTAS_PATH}")
except Exception as e:
    logger.error(f"Módulo C: Error cargando referencia de notas: {e}")
    referencia_notas_c = {}


def _derivar_colecciones(familia_olfativa: str, genero: str, notas: dict, nombre: str = "", descripcion: str = "") -> list:
    """
    Deriva las colecciones aplicando el sistema de puntuación dinámico.
    
    Parámetros
    ----------
    familia_olfativa : str
        Familia olfativa del perfume
    genero : str
        Género del perfume (Hombre, Mujer, Unisex)
    notas : dict
        Diccionario con notas de salida, corazón y fondo
    nombre : str
        Nombre del perfume (para búsqueda de palabras clave)
    descripcion : str
        Descripción del perfume (para búsqueda de palabras clave)
    
    Retorna
    -------
    Lista de 1 o más colecciones (sin duplicados)
    """
    # Inicializar puntuaciones para las 3 colecciones
    puntuaciones = {
        "Frescura y Vitalidad": 0,
        "Noche y Seducción": 0,
        "Elegancia e Intensidad": 0
    }
    
    # Normalizar todos los textos a minúsculas
    familia_lower = (familia_olfativa or "").lower()
    genero_lower = (genero or "").lower()
    nombre_lower = (nombre or "").lower()
    
    # Aplanar todas las notas en una lista única y normalizar
    todas_notas = []
    for nivel in ["salida", "corazon", "fondo"]:
        notas_nivel = notas.get(nivel, [])
        if isinstance(notas_nivel, list):
            todas_notas.extend([n.lower() if isinstance(n, str) else str(n).lower() for n in notas_nivel])
        elif isinstance(notas_nivel, str):
            todas_notas.append(notas_nivel.lower())
    
    # Normalizar descripción
    descripcion_lower = (descripcion or "").lower()
    
    # ─────────────────────────────────────────────
    # 1. Colección: Frescura y Vitalidad
    # ─────────────────────────────────────────────
    
    # +2 puntos si la familia_olfativa contiene: cítrico, citico, acuático, marino, ozónico o verde,
    # pero NO contiene palabras de Noche/Elegancia (oriental, ámbar, gourmand, amaderado, etc.)
    keywords_familia_frescura = ["cítrico", "citico", "acuático", "marino", "ozónico", "verde"]
    keywords_no_frescura = ["oriental", "ambar", "gourmand", "amaderado", "madera", "chypre", "cuero", "fougere", "especiado"]
    if any(keyword in familia_lower for keyword in keywords_familia_frescura):
        # Solo sumar si la familia no contiene indicadores de Noche/Elegancia
        if not any(keyword in familia_lower for keyword in keywords_no_frescura):
            puntuaciones["Frescura y Vitalidad"] += 2
    
    # +1 punto por cada coincidencia en las notas que contenga: limón, bergamota, menta, naranja o neroli.
    keywords_notas_frescura = ["limón", "limon", "bergamota", "menta", "naranja", "neroli"]
    for nota in todas_notas:
        if any(keyword in nota for keyword in keywords_notas_frescura):
            puntuaciones["Frescura y Vitalidad"] += 1
    
    # +1 punto si la descripción contiene palabras clave de frescura
    keywords_descripcion_frescura = ["fresco", "fresca", "frescura", "vitalidad", "ligero", "ligera", "suave", "acuático", "marino", "verano", "día", "clima cálido", "calor"]
    if any(keyword in descripcion_lower for keyword in keywords_descripcion_frescura):
        puntuaciones["Frescura y Vitalidad"] += 1
    
    # -5 puntos (Penalización) si en cualquier campo de notas aparece: cuero, tabaco u oud.
    keywords_penalizacion = ["cuero", "tabaco", "oud"]
    if any(keyword in nota for nota in todas_notas for keyword in keywords_penalizacion):
        puntuaciones["Frescura y Vitalidad"] -= 5
    
    # -2 puntos (Penalización por contradicción) si la descripción contiene palabras de Noche o Elegancia
    # Esto evita que perfumes intensos/seductores/amaderados aparezcan en Frescura solo por tener una nota cítrica
    keywords_contradiccion_frescura = ["intenso", "intensa", "seductor", "seductora", "seducción", "noche", "nocturno", "amaderado", "especiado", "fondo", "corazón especiado", "misterioso", "oscuro", "fiesta", "evento"]
    if any(keyword in descripcion_lower for keyword in keywords_contradiccion_frescura):
        puntuaciones["Frescura y Vitalidad"] -= 2
    
    # ─────────────────────────────────────────────
    # 2. Colección: Noche y Seducción
    # ─────────────────────────────────────────────
    
    # +2 puntos si la familia_olfativa contiene: oriental, ámbar, ambar, gourmand o especiado.
    keywords_familia_noche = ["oriental", "ámbar", "ambar", "gourmand", "especiado"]
    if any(keyword in familia_lower for keyword in keywords_familia_noche):
        puntuaciones["Noche y Seducción"] += 2
    
    # +1 punto por cada coincidencia en las notas que contenga: vainilla, haba tonka, tonka, caramelo, chocolate, miel o praliné.
    keywords_notas_noche = ["vainilla", "haba tonka", "tonka", "caramelo", "chocolate", "miel", "praliné"]
    for nota in todas_notas:
        if any(keyword in nota for keyword in keywords_notas_noche):
            puntuaciones["Noche y Seducción"] += 1
    
    # +1 punto si el nombre del perfume contiene las palabras: intense, extreme, night, nuit o elixir.
    keywords_nombre_noche = ["intense", "extreme", "night", "nuit", "elixir"]
    if any(keyword in nombre_lower for keyword in keywords_nombre_noche):
        puntuaciones["Noche y Seducción"] += 1
    
    # +1 punto si la descripción contiene palabras clave de noche/seducción
    keywords_descripcion_noche = ["noche", "nocturno", "seductor", "seducción", "misterioso", "intenso", "fiesta", "evento", "cita", "romántico", "romance", "tarde", "evening"]
    if any(keyword in descripcion_lower for keyword in keywords_descripcion_noche):
        puntuaciones["Noche y Seducción"] += 1
    
    # ─────────────────────────────────────────────
    # 3. Colección: Elegancia e Intensidad
    # ─────────────────────────────────────────────
    
    # +2 puntos si la familia_olfativa contiene: amaderado, madera, chypre, cuero o fougere.
    keywords_familia_elegancia = ["amaderado", "madera", "chypre", "cuero", "fougere"]
    if any(keyword in familia_lower for keyword in keywords_familia_elegancia):
        puntuaciones["Elegancia e Intensidad"] += 2
    
    # +1 punto por cada coincidencia en las notas que contenga: sándalo, cedro, oud, incienso, vetiver o pachulí.
    keywords_notas_elegancia = ["sándalo", "cedro", "oud", "incienso", "vetiver", "pachulí"]
    for nota in todas_notas:
        if any(keyword in nota for keyword in keywords_notas_elegancia):
            puntuaciones["Elegancia e Intensidad"] += 1
    
    # +2 puntos (Automático) si la columna genero es exactamente unisex.
    if genero_lower == "unisex":
        puntuaciones["Elegancia e Intensidad"] += 2
    
    # +1 punto si la descripción contiene palabras clave de elegancia/intensidad
    keywords_descripcion_elegancia = ["elegancia", "elegante", "intenso", "intensidad", "sofisticado", "clásico", "premium", "lujo", "poderoso", "fuerte", "duradero", "proyección", "amaderado", "madera", "cuero", "fougere", "oriental", "gourmand", "especiado"]
    if any(keyword in descripcion_lower for keyword in keywords_descripcion_elegancia):
        puntuaciones["Elegancia e Intensidad"] += 1
    
    # ─────────────────────────────────────────────
    # RESOLUCIÓN Y FALLBACK
    # ─────────────────────────────────────────────
    
    # Asignación: El perfume se asigna a toda colección que tenga >= 2 puntos.
    # Esto asegura que solo perfumes con evidencia clara aparezcan en cada colección.
    colecciones_asignadas = [coleccion for coleccion, puntaje in puntuaciones.items() if puntaje >= 2]
    
    # Fallback (Garantía): Si después de sumar todo, ninguna colección llega a 2 puntos,
    # asígnalo a la colección que tenga la puntuación más alta.
    if not colecciones_asignadas:
        coleccion_max = max(puntuaciones.items(), key=lambda x: x[1])[0]
        colecciones_asignadas = [coleccion_max]
    
    # Empate a 0: Si todas las colecciones terminan en 0 puntos (o empatan en puntos bajos),
    # asígnalo por defecto a "Elegancia e Intensidad".
    # Esto se cubre automáticamente con el fallback ya que max() devolverá la primera con 0,
    # pero para ser explícitos, si todas tienen 0, forzamos Elegancia e Intensidad.
    if all(puntaje == 0 for puntaje in puntuaciones.values()):
        colecciones_asignadas = ["Elegancia e Intensidad"]
    
    return list(set(colecciones_asignadas))  # Eliminar duplicados por si acaso


def inferir_familia_olfativa(notas: dict, nombre: str = "", descripcion: str = "", genero: str = "") -> str:
    """
    Infiere la familia olfativa del perfume basándose en sus notas, nombre, descripción y género.
    
    Parámetros
    ----------
    notas : dict
        {"salida": [...], "corazon": [...], "fondo": [...]}
    nombre : str
        Nombre del perfume
    descripcion : str
        Descripción del perfume
    genero : str
        Género (Hombre, Mujer, Unisex)
    
    Retorna
    -------
    str
        Familia olfativa inferida (ej: "Cítrico-Aromático", "Floral-Gourmand", etc.)
    """
    # Aplanar todas las notas en una lista única y normalizar
    todas_notas = []
    for nivel in ["salida", "corazon", "fondo"]:
        notas_nivel = notas.get(nivel, [])
        if isinstance(notas_nivel, list):
            todas_notas.extend([n.lower() if isinstance(n, str) else str(n).lower() for n in notas_nivel])
        elif isinstance(notas_nivel, str):
            todas_notas.append(notas_nivel.lower())
    
    # Normalizar textos
    nombre_lower = (nombre or "").lower()
    descripcion_lower = (descripcion or "").lower()
    genero_lower = (genero or "").lower()
    
    # Sistema de puntuación por familia
    puntuaciones = {
        "Cítrico": 0,
        "Aromático": 0,
        "Floral": 0,
        "Frutal": 0,
        "Oriental": 0,
        "Gourmand": 0,
        "Amaderado": 0,
        "Acuático": 0,
        "Verde": 0,
        "Chypre": 0,
        "Fougère": 0,
        "Cuero": 0,
    }
    
    # ─────────────────────────────────────────────
    # 1. CÍTRICO
    # ─────────────────────────────────────────────
    keywords_citrico = ["limón", "limon", "bergamota", "naranja", "mandarina", "pomelo", "toronja", "yuzu", "citrus", "neroli", "petitgrain"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_citrico):
            puntuaciones["Cítrico"] += 2
    
    # ─────────────────────────────────────────────
    # 2. AROMÁTICO (lavanda, romero, hierbas frescas)
    # ─────────────────────────────────────────────
    keywords_aromatico = ["lavanda", "romero", "salvia", "menta", "albahaca", "hierbabuena", "tomillo", "estragón", "artemisa", "pimienta"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_aromatico):
            puntuaciones["Aromático"] += 2
    
    # ─────────────────────────────────────────────
    # 3. FLORAL
    # ─────────────────────────────────────────────
    keywords_floral = ["rosa", "jazmín", "lirio", "peonía", "magnolia", "gardenia", "tuberosa", "ylang-ylang", "violeta", "iris", "freesia", "azucena", "clavel", "margarita"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_floral):
            puntuaciones["Floral"] += 2
    
    # ─────────────────────────────────────────────
    # 4. FRUTAL (frutas no cítricas)
    # ─────────────────────────────────────────────
    keywords_frutal = ["manzana", "pera", "melocotón", "cereza", "frambuesa", "fresa", "mango", "litchi", "maracuyá", "higo", "ciruela", "durazno", "frutilla"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_frutal):
            puntuaciones["Frutal"] += 2
    
    # ─────────────────────────────────────────────
    # 5. ORIENTAL (ámbar, especias, misterio)
    # ─────────────────────────────────────────────
    keywords_oriental = ["ámbar", "ambar", "vainilla", "benjuí", "benzoin", "mirra", "olíbano", "incienso", "bálsamo", "labdanum"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_oriental):
            puntuaciones["Oriental"] += 2
    
    # ─────────────────────────────────────────────
    # 6. GOURMAND (comida, dulce, postre)
    # ─────────────────────────────────────────────
    keywords_gourmand = ["caramelo", "chocolate", "café", "miel", "praliné", "haba tonka", "tonka", "crema", "nata", "leche", "azúcar", "cacao", "marshmallow", "algodón de azúcar"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_gourmand):
            puntuaciones["Gourmand"] += 2
    
    # ─────────────────────────────────────────────
    # 7. AMADERADO (maderas)
    # ─────────────────────────────────────────────
    keywords_amaderado = ["sándalo", "cedro", "vetiver", "pachulí", "roble", "pino", "abeto", "guayaco", "agarwood", "oud", "cashmeran", "maderas", "madera"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_amaderado):
            puntuaciones["Amaderado"] += 2
    
    # ─────────────────────────────────────────────
    # 8. ACUÁTICO / MARINO
    # ─────────────────────────────────────────────
    keywords_acuatico = ["marina", "marino", "acuático", "oceano", "oceánica", "sal marina", "algas", "agua", "water", "ocean", "sea", "jazmín de agua"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_acuatico):
            puntuaciones["Acuático"] += 2
    
    # ─────────────────────────────────────────────
    # 9. VERDE (hojas, hierbas, vegetación)
    # ─────────────────────────────────────────────
    keywords_verde = ["verde", "hoja", "hojas", "hierba", "césped", "prado", "jardín", "botánica", "planta", "tallo", "foliage"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_verde):
            puntuaciones["Verde"] += 1
    
    # ─────────────────────────────────────────────
    # 10. CHYPRE (nota de roble-musgo-ámbar)
    # ─────────────────────────────────────────────
    keywords_chypre = ["musgo de roble", "roble", "moss", "oakmoss", "patchouli", "labdanum", "ámbar", "cedro", "verde", "floral", "cítrico"]
    # Chypre es una combinación, dar puntos si hay múltiples elementos
    chypre_count = sum(1 for nota in todas_notas if any(kw in nota for kw in ["musgo", "roble", "patchouli", "labdanum"]))
    if chypre_count >= 2:
        puntuaciones["Chypre"] += 3
    else:
        for nota in todas_notas:
            if any(kw in nota for kw in keywords_chypre):
                puntuaciones["Chypre"] += 1
    
    # ─────────────────────────────────────────────
    # 11. FOUGÈRE (aromático + amaderado + geranio/roble)
    # ─────────────────────────────────────────────
    keywords_fougere = ["lavanda", "roble", "geranio", "coumarin", "cumarina", "fougère"]
    fougere_count = sum(1 for nota in todas_notas if any(kw in nota for kw in keywords_fougere))
    if fougere_count >= 2:
        puntuaciones["Fougère"] += 3
    else:
        for nota in todas_notas:
            if any(kw in nota for kw in keywords_fougere):
                puntuaciones["Fougère"] += 1
    
    # ─────────────────────────────────────────────
    # 12. CUERO
    # ─────────────────────────────────────────────
    keywords_cuero = ["cuero", "leather", "tabaco", "tabaco", "birch", "abedul", "humo", "smoke", "incienso", "mirra"]
    for nota in todas_notas:
        if any(kw in nota for kw in keywords_cuero):
            puntuaciones["Cuero"] += 2
    
    # ─────────────────────────────────────────────
    # BONIFICACIONES ADICIONALES
    # ─────────────────────────────────────────────
    
    # Si el nombre contiene palabras clave de familia
    if "aqua" in nombre_lower or "acqua" in nombre_lower or "water" in nombre_lower:
        puntuaciones["Acuático"] += 3
    
    if "blue" in nombre_lower:
        puntuaciones["Cítrico"] += 1
        puntuaciones["Acuático"] += 1
    
    if "rose" in nombre_lower or "rosa" in nombre_lower:
        puntuaciones["Floral"] += 2
    
    if "vanilla" in nombre_lower or "vainilla" in nombre_lower:
        puntuaciones["Gourmand"] += 2
        puntuaciones["Oriental"] += 1
    
    if "wood" in nombre_lower or "madera" in nombre_lower or "bois" in nombre_lower:
        puntuaciones["Amaderado"] += 2
    
    # Si la descripción contiene palabras clave
    if "fresco" in descripcion_lower or "fresh" in descripcion_lower:
        puntuaciones["Cítrico"] += 1
        puntuaciones["Acuático"] += 1
        puntuaciones["Verde"] += 1
    
    if "intenso" in descripcion_lower or "intense" in descripcion_lower:
        puntuaciones["Oriental"] += 1
        puntuaciones["Amaderado"] += 1
    
    if "seductor" in descripcion_lower or "seductive" in descripcion_lower:
        puntuaciones["Oriental"] += 1
        puntuaciones["Gourmand"] += 1
    
    # ─────────────────────────────────────────────
    # DETECCIÓN DE COMBINACIONES ESPECÍFICAS
    # ─────────────────────────────────────────────
    
    # Detectar "Amaderado-Aromático" (común en fragancias masculinas)
    # Requiere al menos 2 notas amaderadas Y 1 aromática
    amaderado_count = sum(1 for nota in todas_notas if any(kw in nota for kw in ["sándalo", "cedro", "vetiver", "pachulí", "roble", "pino", "guayaco", "agarwood", "oud", "cashmeran"]))
    aromatico_count = sum(1 for nota in todas_notas if any(kw in nota for kw in ["lavanda", "romero", "salvia", "menta", "albahaca", "hierbabuena", "tomillo", "pimienta"]))
    if amaderado_count >= 2 and aromatico_count >= 1:
        puntuaciones["Amaderado"] += 1
        puntuaciones["Aromático"] += 1
    
    # Detectar "Floral-Gourmand" (común en fragancias femeninas)
    # Requiere al menos 2 notas florales Y 1 gourmand
    floral_count = sum(1 for nota in todas_notas if any(kw in nota for kw in ["rosa", "jazmín", "lirio", "peonía", "magnolia", "gardenia", "tuberosa", "ylang-ylang"]))
    gourmand_count = sum(1 for nota in todas_notas if any(kw in nota for kw in ["vainilla", "caramelo", "chocolate", "café", "miel"]))
    if floral_count >= 2 and gourmand_count >= 1:
        puntuaciones["Floral"] += 1
        puntuaciones["Gourmand"] += 1
    
    # Detectar "Cítrico-Acuático" (frescura marina)
    citrico_count = sum(1 for nota in todas_notas if any(kw in nota for kw in ["limón", "bergamota", "naranja", "mandarina", "pomelo", "toronja"]))
    acuatico_count = sum(1 for nota in todas_notas if any(kw in nota for kw in ["marina", "marino", "acuático", "sal marina", "agua", "jazmín de agua"]))
    if citrico_count >= 1 and acuatico_count >= 1:
        puntuaciones["Cítrico"] += 1
        puntuaciones["Acuático"] += 1
    
    # ─────────────────────────────────────────────
    # SELECCIÓN DE FAMILIAS
    # ─────────────────────────────────────────────
    
    # Ordenar por puntuación descendente
    familias_ordenadas = sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)
    
    # Tomar las 2 familias con mayor puntuación (si tienen al menos 2 puntos cada una)
    resultado = []
    for familia, puntaje in familias_ordenadas:
        if puntaje >= 2 and len(resultado) < 2:
            resultado.append(familia)
    
    # Fallback: si no hay ninguna con 2 puntos, tomar la de mayor puntaje
    if not resultado and familias_ordenadas and familias_ordenadas[0][1] > 0:
        resultado = [familias_ordenadas[0][0]]
    
    # Si todas tienen 0 puntos, asignar basado en género
    if not resultado:
        if "hombre" in genero_lower:
            resultado = ["Aromático", "Amaderado"]
        elif "mujer" in genero_lower:
            resultado = ["Floral", "Oriental"]
        else:
            resultado = ["Aromático", "Floral"]
    
    # Formato: "Familia1-Familia2" o solo la primera si es única
    return "-".join(resultado) if len(resultado) > 1 else resultado[0]


def _normalizar_valor(valor) -> str:
    """
    Normaliza un valor para asegurar que sea un string válido.
    Convierte NaN, None, y otros valores no string a string vacío.
    """
    if valor is None:
        return ""
    if isinstance(valor, float) and math.isnan(valor):
        return ""
    if isinstance(valor, (int, float)):
        return str(int(valor)) if valor == int(valor) else str(valor)
    if not isinstance(valor, str):
        return str(valor)
    return valor.strip()


# ─────────────────────────────────────────────
#   DICCIONARIO DE TRADUCCIÓN DE NOTAS
# ─────────────────────────────────────────────

NOTAS_TRADUCCION: dict[str, str] = {
    # Cítricas
    "bergamot": "Bergamota",       "lemon": "Limón",
    "orange": "Naranja",           "grapefruit": "Pomelo",
    "mandarin": "Mandarina",       "lime": "Lima",
    "yuzu": "Yuzu",                "orange blossom": "Flor de Naranja",

    # Florales
    "rose": "Rosa",                "jasmine": "Jazmín",
    "peony": "Peonía",             "iris": "Iris",
    "lily": "Lirio",               "violet": "Violeta",
    "gardenia": "Gardenia",        "tuberose": "Tuberosa",
    "magnolia": "Magnolia",        "freesia": "Fresia",
    "ylang-ylang": "Ylang-Ylang",  "lavender": "Lavanda",
    "neroli": "Neroli",

    # Frutales
    "peach": "Melocotón",          "apple": "Manzana",
    "pear": "Pera",                "plum": "Ciruela",
    "raspberry": "Frambuesa",      "strawberry": "Fresa",
    "cherry": "Cereza",            "blackcurrant": "Grosella Negra",
    "lychee": "Lichi",             "mango": "Mango",
    "passion fruit": "Maracuyá",   "fig": "Higo",

    # Orientales / Amaderadas
    "sandalwood": "Sándalo",       "cedarwood": "Cedro",
    "cedar": "Cedro",              "oud": "Oud",
    "amber": "Ámbar",              "patchouli": "Pachulí",
    "vetiver": "Vetiver",          "musk": "Almizcle",
    "benzoin": "Benjuí",           "incense": "Incienso",
    "frankincense": "Olíbano",     "myrrh": "Mirra",

    # Especias
    "vanilla": "Vainilla",         "cinnamon": "Canela",
    "cardamom": "Cardamomo",       "pepper": "Pimienta",
    "ginger": "Jengibre",          "clove": "Clavo",
    "saffron": "Azafrán",          "nutmeg": "Nuez Moscada",

    # Gourmand / Dulce
    "caramel": "Caramelo",         "chocolate": "Chocolate",
    "coffee": "Café",              "honey": "Miel",
    "praline": "Praliné",          "tonka bean": "Haba de Tonka",
    "heliotrope": "Heliotropo",

    # Acuáticas / Frescas
    "sea salt": "Sal Marina",      "marine": "Marina",
    "aquatic": "Acuática",         "cucumber": "Pepino",
    "mint": "Menta",               "green tea": "Té Verde",

    # Amaderadas adicionales
    "oak": "Roble",                "pine": "Pino",
    "birch": "Abedul",             "guaiac wood": "Guayaco",
    "agarwood": "Agarwood",        "cashmeran": "Cashmeran",

    # Musgo / Tierra
    "oakmoss": "Musgo de Roble",   "moss": "Musgo",
    "earth": "Tierra",             "leather": "Cuero",
    "smoke": "Ahumado",            "tobacco": "Tabaco",
}


def traducir_nota(nota: str) -> str:
    """
    Traduce una nota olfativa del inglés al español.
    Si no tiene traducción, retorna la nota original en minúsculas
    (conservando la nota exacta de la IA sin filtrar).
    """
    nota_lower = nota.strip().lower()
    return NOTAS_TRADUCCION.get(nota_lower, nota_lower)


def traducir_texto(texto: str) -> str:
    """
    Traduce un texto al español palabra por palabra usando el diccionario de notas.
    Si una palabra no está en el diccionario, la deja en su forma original.
    """
    if not texto:
        return texto
    
    texto_stripped = texto.strip()
    if not texto_stripped:
        return texto_stripped
    
    # Dividir en palabras y traducir cada una
    palabras = texto_stripped.split()
    palabras_traducidas = []
    
    for palabra in palabras:
        # Limpiar puntuación de la palabra
        palabra_limpia = palabra.strip(".,!?;:()[]{}'\"")
        palabra_lower = palabra_limpia.lower()
        
        if palabra_lower in NOTAS_TRADUCCION:
            traduccion = NOTAS_TRADUCCION[palabra_lower]
            # Mantener mayúscula inicial si la palabra original la tenía
            if palabra[0].isupper():
                traduccion = traduccion.capitalize()
            palabras_traducidas.append(traduccion)
        else:
            # Mantener la palabra original
            palabras_traducidas.append(palabra)
    
    # Reconstruir la frase
    resultado = " ".join(palabras_traducidas)
    
    # Capitalizar la primera letra de la frase completa
    if resultado:
        resultado = resultado[0].upper() + resultado[1:]
    
    return resultado


def traducir_notas(notas: dict) -> dict:
    """
    Traduce todas las notas de la pirámide.

    Parámetros
    ----------
    notas : dict
        {"salida": [...], "corazon": [...], "fondo": [...]}

    Retorna
    -------
    dict con las mismas claves y notas traducidas.
    """
    return {
        nivel: [traducir_nota(n) for n in lista]
        for nivel, lista in notas.items()
    }


def traducir_lista_ocasiones(ocasiones: list) -> list:
    """
    Traduce la lista de ocasiones de uso al español.

    Parámetros
    ----------
    ocasiones : list
        Lista de strings en inglés

    Retorna
    -------
    Lista con ocasiones traducidas al español
    """
    traducciones = {
        "day": "Día",
        "night": "Noche",
        "spring": "Primavera",
        "summer": "Verano",
        "autumn": "Otoño",
        "fall": "Otoño",
        "winter": "Invierno",
        "casual": "Casual",
        "formal": "Formal",
        "business": "Negocios",
        "romantic": "Romántico",
        "evening": "Tarde/Noche",
        "office": "Oficina",
        "weekend": "Fin de semana",
        "special occasion": "Ocasión especial",
    }
    
    resultado = []
    for ocasion in ocasiones:
        ocasion_lower = ocasion.strip().lower()
        if ocasion_lower in traducciones:
            resultado.append(traducciones[ocasion_lower])
        else:
            # Si no se encuentra, capitalizar
            resultado.append(ocasion.strip().title())
    
    return resultado


# ─────────────────────────────────────────────
#   INFERENCIA DE OCASIONES (BASADA EN NOTAS Y DESCRIPCIÓN)
# ─────────────────────────────────────────────

def inferir_ocasiones(notas: dict, descripcion: str = "", familia_olfativa: str = "", genero: str = "") -> list:
    """
    Infiere 2-3 ocasiones de uso basándose en las notas, descripción y familia olfativa.
    Usa conocimiento de perfumería para hacer recomendaciones inteligentes.
    
    Parámetros
    ----------
    notas : dict
        {"salida": [...], "corazon": [...], "fondo": [...]}
    descripcion : str
        Descripción del perfume (puede contener pistas sobre el contexto de uso)
    familia_olfativa : str
        Familia olfativa del perfume
    genero : str
        Género (Hombre, Mujer, Unisex)
    
    Retorna
    -------
    Lista de 2-3 ocasiones en español: ["Citas", "Oficina", "Fin de semana"]
    """
    # Aplanar todas las notas
    todas_notas = []
    for nivel in ["salida", "corazon", "fondo"]:
        notas_nivel = notas.get(nivel, [])
        if isinstance(notas_nivel, list):
            todas_notas.extend([n.lower() if isinstance(n, str) else str(n).lower() for n in notas_nivel])
        elif isinstance(notas_nivel, str):
            todas_notas.append(notas_nivel.lower())
    
    # Normalizar textos
    descripcion_lower = (descripcion or "").lower()
    familia_lower = (familia_olfativa or "").lower()
    genero_lower = (genero or "").lower()
    
    # Sistema de puntuación por ocasión
    puntuaciones = {
        "Citas": 0,
        "Oficina": 0,
        "Gimnasio": 0,
        "Evento Formal": 0,
        "Fin de Semana": 0,
        "Playa": 0,
        "Invierno": 0,
        "Noche": 0,
    }
    
    # ─────────────────────────────────────────────
    # 1. Citas Románticas
    # ─────────────────────────────────────────────
    # Notas dulces, gourmand, florales intensos, vainilla, chocolate
    keywords_citas = [
        "vainilla", "chocolate", "miel", "caramelo", "praliné", "haba tonka", "tonka",
        "rosa", "jazmín", "tuberosa", "gardenia", "ylang-ylang",  # florales intensos
        "ámbar", "musk", "almizcle", "oriental", "gourmand",
        "noche", "romántico", "seductor", "cita", "romance"
    ]
    for keyword in keywords_citas:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Citas"] += 2
        if keyword in descripcion_lower:
            puntuaciones["Citas"] += 1
    if "floral" in familia_lower and "mujer" in genero_lower:
        puntuaciones["Citas"] += 1
    
    # ─────────────────────────────────────────────
    # 2. Oficina/Negocios
    # ─────────────────────────────────────────────
    # Aromáticos cítricos, fougère, notas limpias, proyección moderada
    keywords_oficina = [
        "bergamota", "limón", "naranja", "mandarina", "pimienta",  # cítricos/aromáticos
        "lavanda", "romero", "salvia", "mint", "menta",  # hierbas frescas
        "cedro", "sándalo",  # amaderados limpios
        "fougère", "aromático", "fresh", "clean", "profesional", "oficina", "negocios"
    ]
    for keyword in keywords_oficina:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Oficina"] += 2
        if keyword in descripcion_lower:
            puntuaciones["Oficina"] += 1
    if "aromático" in familia_lower or "fougère" in familia_lower:
        puntuaciones["Oficina"] += 2
    
    # ─────────────────────────────────────────────
    # 3. Gimnasio/Deporte
    # ─────────────────────────────────────────────
    # Frescos acuáticos, cítricos, alta vitalidad
    keywords_gimnasio = [
        "acuático", "marine", "sea salt", "agua", "ducharse", "deporte",
        "menta", "pepino", "green tea", "té verde", "limón", "bergamota",
        "fresco", "energético", "deportivo", "activo"
    ]
    for keyword in keywords_gimnasio:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Gimnasio"] += 2
        if keyword in descripcion_lower:
            puntuaciones["Gimnasio"] += 1
    
    # ─────────────────────────────────────────────
    # 4. Evento Formal
    # ─────────────────────────────────────────────
    # Amaderados intensos, orientales, cuero, proyección fuerte
    keywords_formal = [
        "cuero", "tabaco", "oud", "incienso", "benzoin", "mirra",
        "ámbar", "oriental", "chypre", "amaderado intenso",
        "formal", "elegancia", "gala", "evento", "ceremonia", "traje"
    ]
    for keyword in keywords_formal:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Evento Formal"] += 2
        if keyword in descripcion_lower:
            puntuaciones["Evento Formal"] += 1
    if "oriental" in familia_lower or "chypre" in familia_lower:
        puntuaciones["Evento Formal"] += 2
    
    # ─────────────────────────────────────────────
    # 5. Fin de Semana/Casual
    # ─────────────────────────────────────────────
    # Versátiles, frescos, gourmand ligeros
    keywords_casual = [
        "casual", "relajado", "fin de semana", "weekend", "diario",
        "manzana", "pera", "melocotón", "frutal", "verano",
        "versátil", "todo el día", "everyday"
    ]
    for keyword in keywords_casual:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Fin de Semana"] += 1
        if keyword in descripcion_lower:
            puntuaciones["Fin de Semana"] += 2
    if "fruity" in familia_lower or "fresh" in familia_lower:
        puntuaciones["Fin de Semana"] += 1
    
    # ─────────────────────────────────────────────
    # 6. Playa/Verano
    # ─────────────────────────────────────────────
    # Acuáticos, cítricos, sal marina, calor extremo
    keywords_playa = [
        "acuático", "marine", "sea salt", "oceano", "playa", "verano",
        "limón", "bergamota", "naranja", "mandarina", "cítrico",
        "tropical", "sol", "calor", "refrescante"
    ]
    for keyword in keywords_playa:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Playa"] += 2
        if keyword in descripcion_lower:
            puntuaciones["Playa"] += 1
    
    # ─────────────────────────────────────────────
    # 7. Invierno (estación fría)
    # ─────────────────────────────────────────────
    # Gourmand, amaderados pesados, especias fuertes
    keywords_invierno = [
        "vainilla", "caramelo", "chocolate", "miel", "haba tonka",
        "tabaco", "cuero", "oud", "incienso", "sándalo", "cedro",
        "especiado", "canela", "clavo", "nuez moscada", "jengibre",
        "invierno", "frío", "abrigo", "navidad"
    ]
    for keyword in keywords_invierno:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Invierno"] += 2
        if keyword in descripcion_lower:
            puntuaciones["Invierno"] += 1
    
    # ─────────────────────────────────────────────
    # 8. Noche
    # ─────────────────────────────────────────────
    # Orientales, gourmand, proyección fuerte, misterio
    keywords_noche = [
        "oriental", "gourmand", "ámbar", "vainilla", "musk",
        "noche", "night", "nocturno", "evening", "tarde", "oscuro",
        "intenso", "deep", "seductor", "misterioso"
    ]
    for keyword in keywords_noche:
        if any(keyword in nota for nota in todas_notas):
            puntuaciones["Noche"] += 2
        if keyword in descripcion_lower:
            puntuaciones["Noche"] += 1
    
    # ─────────────────────────────────────────────
    # SELECCIÓN FINAL
    # ─────────────────────────────────────────────
    # Ordenar por puntuación descendente
    ocasiones_ordenadas = sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)
    
    # Tomar las 2 o 3 con mayor puntuación (si tienen al menos 2 puntos)
    resultado = []
    for ocasion, puntaje in ocasiones_ordenadas:
        if puntaje >= 2 and len(resultado) < 3:
            resultado.append(ocasion)
    
    # Fallback: si ninguna tiene 2 puntos, tomar las 2 con más puntaje
    if not resultado and ocasiones_ordenadas:
        resultado = [ocasiones_ordenadas[0][0]]
        if len(ocasiones_ordenadas) > 1 and ocasiones_ordenadas[1][1] > 0:
            resultado.append(ocasiones_ordenadas[1][0])
    
    return resultado


# ─────────────────────────────────────────────
#   LÓGICA DE NEGOCIO: ICONOS DE ESTACIÓN
# ─────────────────────────────────────────────

UMBRAL_DOMINANTE = 20  # % mínimo para considerar una estación dominante (bajado de 40 a 20)

ICONOS_ESTACION = {
    "verano":    "☀️",
    "primavera": "🌸",
    "otono":     "🍂",
    "invierno":  "❄️",
    "dia":       "🌤️",
    "noche":     "🌙",
}

NOMBRES_ESTACION = {
    "verano":    "Verano",
    "primavera": "Primavera",
    "otono":     "Otono",
    "invierno":  "Invierno",
    "dia":       "Dia",
    "noche":     "Noche",
}

# Bonificaciones por notas para ajuste de estaciones (conocimiento de perfumería)
BONIFICACIONES_NOTAS = {
    "verano": {
        "bergamota", "limón", "naranja", "mandarina", "lime", "yuzu",  # cítricos
        "menta", "pepino", "green tea", "té verde",  # frescos
        "sea salt", "marine", "acuático", "agua",  # acuáticos
        "albahaca", "hierbabuena", "lavanda",  # hierbas frescas
    },
    "primavera": {
        "bergamota", "limón", "naranja", "mandarina",  # cítricos
        "rosa", "jazmín", "lirio", "peonía", "magnolia",  # florales ligeros
        "manzana", "pera", "frambuesa",  # frutales frescos
        "hiedra", "musgo", "verde",  # notas verdes
    },
    "otono": {
        "canela", "cardamomo", "pimienta", "jengibre",  # especias
        "sándalo", "cedro", "vetiver",  # amaderados secos
        "tabaco", "cuero", "oud",  # notas intensas
        "hoja seca", "maderas", "tierra",  # notas terrosas
    },
    "invierno": {
        "vainilla", "haba tonka", "tonka", "caramelo", "chocolate", "miel",  # gourmand
        "ámbar", "almizcle", "musk",  # notas cálidas
        "sándalo", "cedro", "incienso", "benzoin",  # amaderados/ resinados
        "especiado", "clavo", "nuez moscada",  # especias fuertes
    },
}

def _calcular_ajuste_estacional_por_notas(notas: dict) -> dict:
    """
    Calcula bonificaciones de porcentaje para estaciones basadas en las notas del perfume.
    Aplica conocimiento de perfumería: ciertas notas son indicadoras de estaciones.
    
    Retorna un diccionario con ajustes: {"verano": 15, "invierno": 10, ...}
    """
    # Aplanar todas las notas
    todas_notas = []
    for nivel in ["salida", "corazon", "fondo"]:
        notas_nivel = notas.get(nivel, [])
        if isinstance(notas_nivel, list):
            todas_notas.extend([n.lower() if isinstance(n, str) else str(n).lower() for n in notas_nivel])
        elif isinstance(notas_nivel, str):
            todas_notas.append(notas_nivel.lower())
    
    ajustes = {"verano": 0, "primavera": 0, "otono": 0, "invierno": 0}
    
    for nota in todas_notas:
        for estacion, keywords in BONIFICACIONES_NOTAS.items():
            if any(keyword in nota for keyword in keywords):
                # Bonificación: +15 puntos por nota coincidente
                ajustes[estacion] += 15
    
    return ajustes


def determinar_estaciones(clima: dict, notas: dict = None) -> list[dict]:
    """
    Determina las estaciones y momentos del día dominantes.
    
    Incorpora lógica mejorada:
    1. Usa los porcentajes de la IA como base
    2. Aplica bonificaciones basadas en notas olfativas (conocimiento de perfumería)
    3. Umbral reducido al 20% para mayor sensibilidad
    4. Si ninguna supera el umbral, toma las 2 con mayor porcentaje
    
    Retorna
    -------
    Lista de dicts: [{"nombre": "Verano", "icono": "☀️", "porcentaje": 65}, ...]
    Ordenada de mayor a menor porcentaje.
    """
    estaciones = {k: v for k, v in clima.items() if k in ("verano", "primavera", "otono", "invierno")}
    momentos   = {k: v for k, v in clima.items() if k in ("dia", "noche")}
    
    # Aplicar bonificaciones por notas si están disponibles
    if notas:
        ajustes = _calcular_ajuste_estacional_por_notas(notas)
        for estacion in estaciones:
            estaciones[estacion] = min(100, estaciones[estacion] + ajustes.get(estacion, 0))

    resultado = []

    def _procesar_grupo(grupo: dict):
        if not any(grupo.values()):
            return  # Sin datos

        # Ordenar de mayor a menor
        items_ordenados = sorted(grupo.items(), key=lambda x: x[1], reverse=True)
        
        # Tomar las 2 estaciones con mayor porcentaje (si superan el umbral o son las máximas)
        dominantes = []
        for key, valor in items_ordenados:
            if valor >= UMBRAL_DOMINANTE:
                dominantes.append(key)
            # Si no hay ninguna con umbral, tomar las 2 primeras
            if not dominantes and len(dominantes) < 2 and valor > 0:
                dominantes.append(key)
                if len(dominantes) >= 2:
                    break
        
        # Limitar a máximo 2 estaciones/momentos
        dominantes = dominantes[:2]
        
        for key in dominantes:
            resultado.append({
                "nombre":     NOMBRES_ESTACION[key],
                "icono":      ICONOS_ESTACION[key],
                "porcentaje": grupo[key],
            })

    _procesar_grupo(estaciones)
    _procesar_grupo(momentos)

    resultado.sort(key=lambda x: x["porcentaje"], reverse=True)
    return resultado


# ─────────────────────────────────────────────
#   FORMATEO DEL NOMBRE
# ─────────────────────────────────────────────

def formatear_nombre(nombre: str, marca: str = "") -> dict:
    """
    Formatea el nombre para el catálogo.

    Retorna
    -------
    dict con:
        - "titulo":    nombre del perfume (capitalizado)
        - "subtitulo": nombre de la marca (si existe)
        - "completo":  "Nombre — Marca" o solo "Nombre"
    """
    titulo = nombre.strip().title()
    subtitulo = marca.strip().title() if marca else ""
    completo = f"{titulo} - {subtitulo}" if subtitulo else titulo

    return {"titulo": titulo, "subtitulo": subtitulo, "completo": completo}


# ─────────────────────────────────────────────
#   FUNCIÓN PRINCIPAL DEL MÓDULO
# ─────────────────────────────────────────────

def procesar(resultado_scraping: dict, info_lista: dict | None = None) -> dict:
    """
    Función principal. Recibe el dict del Módulo B y devuelve
    un dict limpio y enriquecido listo para el Módulo D (PDF).

    Parámetros
    ----------
    resultado_scraping : dict
        Salida de modulo_b_ia_extractor.scrape_perfume()
    info_lista : dict | None
        Datos extra del CSV (ml, marca) del Módulo A

    Retorna
    -------
    {
        "nombre":      dict  (titulo, subtitulo, completo),
        "notas":       dict  (salida, corazon, fondo) — traducidas,
        "estaciones":  list  (dominantes con icono y %),
        "imagen_path": Path | None,
        "url":         str,
        "ml":          str,
    }
    """
    info = info_lista or {}
    nombre_raw = _normalizar_valor(resultado_scraping.get("nombre", ""))
    marca_raw  = _normalizar_valor(info.get("marca", ""))
    nombre_clave = nombre_raw.strip()

    nombre_fmt  = formatear_nombre(nombre_raw, marca_raw)
    
    # Traducir descripción al español (se necesita para inferir familia)
    descripcion_raw = _normalizar_valor(resultado_scraping.get("descripcion", resultado_scraping.get("descripcion_corta", "")))
    descripcion_trad = traducir_texto(descripcion_raw) if descripcion_raw else ""
    
    # Si existe referencia, usar las notas, género y familia directamente
    ref = referencia_notas_c.get(nombre_clave)
    if ref:
        logger.info(f"Módulo C: Usando datos de referencia para {nombre_clave}")
        notas_trad = ref["notas"]
        # Usar género y familia de la referencia para clasificación correcta
        genero_ref = ref.get("genero", "")
        familia_ref = ref.get("familia_olfativa", "")
        # Si la referencia tiene datos, usarlos; si no, mantener los del scraping
        genero = genero_ref if genero_ref else _normalizar_valor(resultado_scraping.get("genero", "Unisex"))
        familia_olfativa = familia_ref if familia_ref else _normalizar_valor(resultado_scraping.get("familia_olfativa", ""))
        # Si no hay familia olfativa (ni de referencia ni de scraping), inferirla
        if not familia_olfativa:
            familia_olfativa = inferir_familia_olfativa(notas_trad, nombre_raw, descripcion_trad, genero)
            logger.info(f"Módulo C: Familia olfativa inferida para '{nombre_clave}': {familia_olfativa}")
    else:
        notas_trad  = traducir_notas(resultado_scraping.get("notas", {"salida": [], "corazon": [], "fondo": []}))
        # PRIORIZAR género del CSV (info_lista) sobre el scraping, si existe
        genero_csv = info.get("genero", "")
        if genero_csv and genero_csv.strip():
            genero = _normalizar_valor(genero_csv)
        else:
            genero = _normalizar_valor(resultado_scraping.get("genero", "Unisex"))
        familia_olfativa = _normalizar_valor(resultado_scraping.get("familia_olfativa", ""))
        # Si no hay familia olfativa, inferirla basándonos en las notas
        if not familia_olfativa:
            familia_olfativa = inferir_familia_olfativa(notas_trad, nombre_raw, descripcion_trad, genero)
            logger.info(f"Módulo C: Familia olfativa inferida para '{nombre_clave}': {familia_olfativa}")
    
    # Determinar estaciones con bonificaciones por notas
    estaciones  = determinar_estaciones(resultado_scraping.get("clima", {}), notas_trad)
    img_path    = resultado_scraping.get("imagen_path")
    
    # Inferir ocasiones basadas en notas, descripción, familia y género (sistema inteligente)
    # Si la IA proporcionó ocasiones, las usamos como base; si no, inferimos desde cero
    ocasiones_raw = resultado_scraping.get("ocasiones", resultado_scraping.get("ocasiones_de_uso", []))
    if ocasiones_raw:
        # Traducir ocasiones de la IA
        ocasiones_trad = traducir_lista_ocasiones(ocasiones_raw)
        # Complementar con inferencia si hay menos de 2
        if len(ocasiones_trad) < 2:
            ocasiones_inferidas = inferir_ocasiones(notas_trad, descripcion_trad, familia_olfativa, genero)
            # Añadir ocasiones inferidas que no estén ya presentes
            for oc in ocasiones_inferidas:
                if oc not in ocasiones_trad:
                    ocasiones_trad.append(oc)
            # Limitar a máximo 3
            ocasiones_trad = ocasiones_trad[:3]
    else:
        # No hay ocasiones de la IA, inferir completamente
        ocasiones_trad = inferir_ocasiones(notas_trad, descripcion_trad, familia_olfativa, genero)
    
    # Derivar colecciones automáticamente para asegurar clasificación correcta
    colecciones_derivadas = _derivar_colecciones(familia_olfativa, genero, notas_trad, nombre_raw, descripcion_trad)
    
    # Normalizar género para consistencia (capitalizar primera letra)
    genero_norm = genero.capitalize() if genero else "Unisex"
    
    dato_limpio = {
        "nombre":      nombre_fmt,
        "notas":       notas_trad,
        "genero":      genero_norm,
        "familia_olfativa": familia_olfativa,
        "descripcion": descripcion_trad,
        "ocasiones":   ocasiones_trad,
        "estaciones":  estaciones,
        "imagen_path": Path(img_path) if img_path else None,
        "url":         _normalizar_valor(resultado_scraping.get("url", "")),
        "ml":          _normalizar_valor(info.get("ml", "")),
        "colecciones": colecciones_derivadas,
    }

    logger.debug(
        f"Procesado '{nombre_fmt['completo']}' → "
        f"{sum(len(v) for v in notas_trad.values())} notas | "
        f"{len(estaciones)} estaciones"
    )
    return dato_limpio


# ─────────────────────────────────────────────
#   PRUEBA STAND-ALONE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    fake_scraping = {
        "nombre": "Good Girl",
        "url": "https://www.fragrantica.es/perfumes/carolina-herrera/good-girl-29298.html",
        "notas": {
            "salida":  ["almond", "coffee", "bergamot"],
            "corazon": ["rose", "jasmine", "tuberose"],
            "fondo":   ["sandalwood", "vanilla", "musk", "cocoa"],
        },
        "clima": {
            "primavera": 20, "verano": 15, "otono": 45, "invierno": 60,
            "dia": 30, "noche": 70,
        },
        "imagen_path": None,
    }

    fake_info = {"marca": "Carolina Herrera", "ml": "80"}

    resultado = procesar(fake_scraping, fake_info)

    # Serializar Path para JSON
    resultado["imagen_path"] = str(resultado["imagen_path"] or "")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
