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

from pathlib import Path

from loguru import logger

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
    Si no tiene traducción, retorna la nota original capitalizada.
    """
    nota_lower = nota.strip().lower()
    return NOTAS_TRADUCCION.get(nota_lower, nota.strip().title())


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
#   LÓGICA DE NEGOCIO: ICONOS DE ESTACIÓN
# ─────────────────────────────────────────────

UMBRAL_DOMINANTE = 40  # % mínimo para considerar una estación dominante

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


def determinar_estaciones(clima: dict) -> list[dict]:
    """
    Determina las estaciones y momentos del día dominantes.

    Lógica:
    - Si ninguna estación supera el umbral, se toma la de mayor porcentaje.
    - Si hay empate, se incluyen ambas.

    Retorna
    -------
    Lista de dicts: [{"nombre": "Verano", "icono": "☀️", "porcentaje": 65}, ...]
    Ordenada de mayor a menor porcentaje.
    """
    estaciones = {k: v for k, v in clima.items() if k in ("verano", "primavera", "otono", "invierno")}
    momentos   = {k: v for k, v in clima.items() if k in ("dia", "noche")}

    resultado = []

    def _procesar_grupo(grupo: dict):
        if not any(grupo.values()):
            return  # Sin datos

        max_val = max(grupo.values())
        dominantes = [k for k, v in grupo.items() if v >= UMBRAL_DOMINANTE]

        if not dominantes:
            dominantes = [k for k, v in grupo.items() if v == max_val]

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
        Datos extra del CSV (precio, ml, marca) del Módulo A

    Retorna
    -------
    {
        "nombre":      dict  (titulo, subtitulo, completo),
        "notas":       dict  (salida, corazon, fondo) — traducidas,
        "estaciones":  list  (dominantes con icono y %),
        "imagen_path": Path | None,
        "url":         str,
        "precio":      str,
        "ml":          str,
    }
    """
    info = info_lista or {}
    nombre_raw = resultado_scraping.get("nombre", "")
    marca_raw  = info.get("marca", "")

    nombre_fmt  = formatear_nombre(nombre_raw, marca_raw)
    notas_trad  = traducir_notas(resultado_scraping.get("notas", {"salida": [], "corazon": [], "fondo": []}))
    estaciones  = determinar_estaciones(resultado_scraping.get("clima", {}))
    img_path    = resultado_scraping.get("imagen_path")

    # Traducir descripción y ocasiones al español
    descripcion_raw = resultado_scraping.get("descripcion", resultado_scraping.get("descripcion_corta", ""))
    descripcion_trad = traducir_texto(descripcion_raw) if descripcion_raw else ""
    
    ocasiones_raw = resultado_scraping.get("ocasiones", resultado_scraping.get("ocasiones_de_uso", []))
    ocasiones_trad = traducir_lista_ocasiones(ocasiones_raw)

    dato_limpio = {
        "nombre":      nombre_fmt,
        "notas":       notas_trad,
        "genero":      resultado_scraping.get("genero", "Unisex"),
        "descripcion": descripcion_trad,
        "ocasiones":   ocasiones_trad,
        "estaciones":  estaciones,
        "imagen_path": Path(img_path) if img_path else None,
        "url":         resultado_scraping.get("url", ""),
        "precio":      info.get("precio", ""),
        "ml":          info.get("ml", ""),
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

    fake_info = {"marca": "Carolina Herrera", "precio": "89990", "ml": "80"}

    resultado = procesar(fake_scraping, fake_info)

    # Serializar Path para JSON
    resultado["imagen_path"] = str(resultado["imagen_path"] or "")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
