"""
Módulo B: Motor de Extracción IA — Soul Extrait
Con scraping web integrado
"""

import asyncio
import json
import os
import re
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from openrouter import OpenRouter

load_dotenv()

# Importar módulos adicionales
try:
    import modulo_descripciones_variadas as desc_var
    DESC_VAR_DISPONIBLE = True
except ImportError:
    DESC_VAR_DISPONIBLE = False
    logger.warning("Módulo de descripciones variadas no disponible")

try:
    import modulo_web_scraper_sync as web_scraper
    SCRAPER_DISPONIBLE = True
except ImportError:
    SCRAPER_DISPONIBLE = False
    logger.warning("Módulo de web scraper síncrono no disponible")

# Cargar base de datos de referencia de notas reales
REFERENCIA_NOTAS_PATH = Path("data/referencia_notas.json")
referencia_notas = {}
try:
    if REFERENCIA_NOTAS_PATH.exists():
        with open(REFERENCIA_NOTAS_PATH, "r", encoding="utf-8") as f:
            referencia_notas = json.load(f)
        logger.info(f"Cargada referencia de notas para {len(referencia_notas)} perfumes")
    else:
        logger.warning(f"Archivo de referencia no encontrado: {REFERENCIA_NOTAS_PATH}")
except Exception as e:
    logger.error(f"Error cargando referencia de notas: {e}")
    referencia_notas = {}

# Configuración
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL_TEXT = "meta-llama/llama-3.1-8b-instruct"

openrouter_client = OpenRouter(api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None


def _slug(nombre: str) -> str:
    s = re.sub(r"[^\w\s-]", "", unicodedata.normalize("NFD", nombre).encode("ascii", "ignore").decode()).strip().lower()
    return re.sub(r"\s+", "_", s)


def _derivar_colecciones(familia_olfativa: str, genero: str, notas: dict) -> list:
    """
    Deriva las colecciones aplicando las reglas de clasificación.
    
    Reglas:
    - Sensación de Frescura: Solo si es CÍTRICO y NO es dulce/gourmand
    - Noche y Seducción: Para DULCES/GOURMAND, AMADERADOS intensos, ORIENTALES, o NOCHE/INVIERNO
    - Fuerza y Elegancia: Para ALTA GAMA (lujo), INTENSOS, eventos FORMALES
    
    Retorna
    -------
    Lista de 1 o más colecciones (sin duplicados)
    """
    colecciones = set()
    familia_lower = familia_olfativa.lower() if familia_olfativa else ""
    
    # Detectar si es gourmand/dulce por las notas
    es_gourmand = False
    notas_fondo = notas.get("fondo", [])
    notas_dulces = ["vainilla", "caramelo", "chocolate", "café", "miel", "praliné", "tonka"]
    for nota in notas_fondo:
        if any(dulce in nota.lower() for dulce in notas_dulces):
            es_gourmand = True
            break
    
    # 1. Sensación de Frescura: Solo CÍTRICO (o que contenga "cítrico") y NO gourmand
    if ("cítrico" in familia_lower or "citrico" in familia_lower) and not es_gourmand:
        colecciones.add("Sensación de Frescura")
    
    # 2. Noche y Seducción: Gourmand, Amaderados intensos, Orientales, o Noche/Invierno
    if es_gourmand:
        colecciones.add("Noche y Seducción")
    elif "amaderado" in familia_lower or "oriental" in familia_lower:
        colecciones.add("Noche y Seducción")
    
    # 3. Fuerza y Elegancia: Por defecto para alta gama, intensos, formales
    # Si no se asignó a las otras, o si es Unisex (suele ser más formal)
    if not colecciones or genero == "Unisex":
        colecciones.add("Fuerza y Elegancia")
    
    # Si no hay ninguna (caso extremo), asignar Fuerza y Elegancia
    if not colecciones:
        colecciones.add("Fuerza y Elegancia")
    
    return list(colecciones)


# ─────────────────────────────────────────────
#   ORGANIZACIÓN CON IA (POST-SCRAPING)
# ─────────────────────────────────────────────

def _organizar_con_ia_sync(nombre: str, marca: str, genero: str, datos_web: dict, ref: dict = None) -> dict:
    """Organiza y completa datos extraídos de la web usando OpenRouter."""
    if not openrouter_client:
        logger.error("OpenRouter no configurado")
        return {}

    # Construir sección de referencia
    ref_notas_text = ""
    if ref:
        salida = ', '.join(ref['notas']['salida'])
        corazon = ', '.join(ref['notas']['corazon'])
        fondo = ', '.join(ref['notas']['fondo'])
        ref_notas_text = f"\n\nREFERENCIA DE NOTAS CONFIRMADAS (usar EXACTAMENTE estas):\n- Salida: {salida}\n- Corazón: {corazon}\n- Fondo: {fondo}\n"

    # Construir sección de notas web
    notas_web = datos_web.get("notas", {})
    salida_web = ', '.join(notas_web.get('salida', []))
    corazon_web = ', '.join(notas_web.get('corazon', []))
    fondo_web = ', '.join(notas_web.get('fondo', []))
    notas_web_text = f"\n\nNOTAS OBTENIDAS DE LA WEB (Fragrantica) - USAR ESTAS COMO BASE:\n- Salida: {salida_web}\n- Corazón: {corazon_web}\n- Fondo: {fondo_web}\n\nIMPORTANTE: Estas notas son de fuentes reales. Úsalas EXACTAMENTE como están.\nSi la referencia anterior existe, prioriza la referencia (es más confiable).\n"

    # Construir prompt usando concatenación para evitar problemas con llaves
    marca_part = f" (Marca: {marca})" if marca else ""
    genero_part = f" (Género: {genero})" if genero else ""
    prompt = (
        "Eres un experto en perfumería español con conocimiento profundo de fragancias de todas las marcas. Tu única lengua es el español.\n\n"
        "INSTRUCCIÓN ABSOLUTA: Debes responder ÚNICAMENTE con un objeto JSON válido. No escribas explicaciones, notas, ni texto adicional antes o después del JSON.\n\n"
        f"Tarea: Organiza y completa la ficha técnica para el perfume: \"{nombre}\"{marca_part}{genero_part}.\n"
        f"{ref_notas_text}{notas_web_text}"
        "ESQUEMA JSON REQUERIDO:\n"
        "{\n"
        '    "familia_olfativa": "Cítrico - Madera",\n'
        '    "genero": "Hombre",\n'
        '    "descripcion_corta": "Una fragancia fresca y elegante con notas cítricas y amaderadas, perfecta para el día.",\n'
        '    "ocasiones_de_uso": ["Día", "Verano", "Oficina"],\n'
        '    "notas": {\n'
        '        "salida": ["Bergamota", "Limón"],\n'
        '        "corazon": ["Rosa", "Jazmín"],\n'
        '        "fondo": ["Sándalo", "Vainilla"]\n'
        '    },\n'
        '    "clima": {\n'
        '        "primavera": 80,\n'
        '        "verano": 90,\n'
        '        "otono": 40,\n'
        '        "invierno": 10,\n'
        '        "dia": 95,\n'
        '        "noche": 20\n'
        '    },\n'
        '    "colecciones": ["Sensación de Frescura"]\n'
        "}\n\n"
        "REGLAS CRÍTICAS:\n\n"
        "1. Todo el contenido debe estar en español. Prohibido usar inglés.\n\n"
        "2. \"descripcion_corta\":\n"
        "   - Máximo 2 líneas (una oración completa, o dos cortas).\n"
        "   - DEBE ser ÚNICA y ESPECÍFICA para este perfume. NUNCA uses descripciones genéricas.\n"
        "   - CRÍTICO: Si el perfume es CÍTRICO, NO uses siempre \"fresca y elegante\". Varía con: vibrante, radiante, chispeante, luminosa, revitalizante, optimista, etc.\n"
        "   - CRÍTICO: Si el perfume es FLORAL, NO uses siempre \"elegante y sofisticada\". Varía con: poética, romántica, exuberante, delicada, primaveral, etc.\n"
        "   - CRÍTICO: Si el perfume es AMADERADO, NO uses siempre \"profundidad y elegancia\". Varía con: terroso, ahumado, noble, intenso, sereno, etc.\n"
        "   - CRÍTICO: Si el perfume es GOURMAND, NO uses siempre \"dulce y tentadora\". Varía con: golosa, comestible, azucarada, reconfortante, etc.\n"
        "   - CRÍTICO: Si el perfume es ORIENTAL, NO uses siempre \"misteriosa y sensual\". Varía con: opulenta, embriagadora, exótica, nocturna, etc.\n"
        "   - Describe la esencia, personalidad o inspiración de la fragancia de forma ÚNICA.\n"
        "   - Usa metáforas variadas: viajes, momentos del día, estaciones, emociones, lugares, obras de arte.\n"
        "   - EVITA repetir estructuras: no empieces siempre con \"Una\" o \"Composición\".\n\n"
        "3. \"ocasiones_de_uso\": lista con 3-5 palabras del conjunto: Día, Noche, Verano, Invierno, Primavera, Otoño, Oficina, Casual, Formal, Romántico, Fin de semana.\n\n"
        "4. \"notas\":\n"
        "   ⚠️  CRÍTICO: Si hay \"NOTAS OBTENIDAS DE LA WEB\" arriba, USA ESAS NOTAS EXACTAMENTE.\n"
        "   - No cambies, no añadas, no quites notas. Usa la lista proporcionada.\n"
        "   - Si también hay \"REFERENCIA DE NOTAS CONFIRMADAS\", prioriza la referencia.\n"
        "   - Solo si no hay notas de web ni referencia, entonces inventa notas basándote en el nombre.\n\n"
        "5. \"clima\": porcentajes del 0 al 100. Ajusta según la personalidad real del perfume.\n\n"
        "6. \"genero\": \"Hombre\", \"Mujer\" o \"Unisex\". Usa el género de la referencia si existe.\n\n"
        "7. \"familia_olfativa\": Usa familias precisas. Usa la de la referencia si existe.\n\n"
        "8. \"colecciones\": array con 1 o más de estas 3 colecciones EXACTAS (no inventes otras):\n"
        "   - \"Sensación de Frescura\": Solo si es CÍTRICO Y NO es dulce/gourmand.\n"
        "   - \"Noche y Seducción\": Para DULCES/GOURMAND, AMADERADOS intensos, ORIENTALES, o NOCHE/INVIERNO.\n"
        "   - \"Fuerza y Elegancia\": Para ALTA GAMA (lujo), INTENSOS, eventos FORMALES.\n"
        "   REGLA DECISIVA: Si el perfume es DULCE o GOURMAND (tiene vainilla, caramelo, chocolate, café, miel en el fondo), debe estar en \"Noche y Seducción\" y NO en \"Sensación de Frescura\".\n\n"
        "IMPORTANTE: Responde SOLO con el JSON. Sin markdown, sin ```json, sin explicaciones."
    )

    try:
        logger.info(f"Organizando datos de web para '{nombre}' con OpenRouter")
        temp = 0.2 if ref else 0.3
        resp = openrouter_client.chat.send(
            messages=[{"role": "user", "content": prompt}],
            model=OPENROUTER_MODEL_TEXT,
            temperature=temp,
            max_tokens=2048,
        )
        texto = resp.choices[0].message.content or ""

        texto = re.sub(r"```json\s*|```\s*", "", texto, flags=re.IGNORECASE).strip()
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                datos = json.loads(json_str)

                if not isinstance(datos, dict):
                    logger.warning(f"OpenRouter devolvió algo que no es un dict para {nombre}")
                    return {}

                tiene_datos = (
                    datos.get("notas") or
                    datos.get("descripcion_corta") or
                    datos.get("ocasiones_de_uso") or
                    datos.get("clima")
                )

                if not tiene_datos:
                    logger.warning(f"OpenRouter devolvió datos vacíos para {nombre}")
                    return {}

                # Forzar notas de la web o referencia
                if ref and "notas" in ref:
                    logger.info(f"Aplicando notas de referencia para {nombre}")
                    datos["notas"] = ref["notas"]
                    datos["genero"] = ref.get("genero", datos.get("genero", "Unisex"))
                    datos["familia_olfativa"] = ref.get("familia_olfativa", datos.get("familia_olfativa", ""))
                elif datos_web.get("notas"):
                    logger.info(f"Aplicando notas de la web para {nombre}")
                    datos["notas"] = datos_web["notas"]
                    if datos_web.get("genero"):
                        datos["genero"] = datos_web["genero"]
                    if datos_web.get("familia_olfativa"):
                        datos["familia_olfativa"] = datos_web["familia_olfativa"]

                # Añadir URL de la web
                if datos_web.get("url"):
                    datos["url"] = datos_web["url"]

                # Derivar colecciones automáticamente basándose en familia, género y notas
                notas_para_colecciones = datos.get("notas", {})
                colecciones_derivadas = _derivar_colecciones(
                    datos.get("familia_olfativa", ""),
                    datos.get("genero", "Unisex"),
                    notas_para_colecciones
                )
                datos["colecciones"] = colecciones_derivadas
                logger.info(f"Colecciones derivadas para {nombre}: {colecciones_derivadas}")

                return datos
            except json.JSONDecodeError as e:
                logger.warning(f"JSON inválido para {nombre}: {e}")
                logger.debug(f"Texto recibido: {texto[:500]}")
                return {}

        logger.warning(f"No se detectó JSON para {nombre}")
        logger.debug(f"Texto recibido: {texto[:500]}")
        return {}
    except Exception as e:
        logger.error(f"Error organizando con IA para {nombre}: {e}")
        return {}


def _extraer_ia_sync(nombre: str, marca: str = "", genero: str = "") -> dict:
    """
    Función principal de extracción síncrona.
    Intenta obtener datos de la web primero, luego organiza con IA.
    """
    if not openrouter_client:
        logger.error("OpenRouter no configurado")
        return {}

    ref = referencia_notas.get(nombre)

    # 1. Intentar obtener datos de la web (si el scraper está disponible)
    datos_web = None
    if SCRAPER_DISPONIBLE:
        try:
            datos_web = web_scraper.extraer_con_cache_sync(nombre, marca)
            if datos_web:
                logger.info(f"Datos obtenidos de la web para {nombre}: {sum(len(v) for v in datos_web.get('notas', {}).values())} notas")
        except Exception as e:
            logger.warning(f"Error en scraping web para {nombre}: {e}")

    # 2. Si tenemos datos de la web, organizarlos con IA
    if datos_web:
        return _organizar_con_ia_sync(nombre, marca, genero, datos_web, ref)

    # 3. Si no hay datos de web, generar solo con IA (modo fallback)
    logger.info(f"Usando modo fallback (solo IA) para {nombre}")

    ref_notas_text = ""
    if ref:
        salida = ', '.join(ref['notas']['salida'])
        corazon = ', '.join(ref['notas']['corazon'])
        fondo = ', '.join(ref['notas']['fondo'])
        ref_notas_text = f"\n\nREFERENCIA DE NOTAS CONFIRMADAS (usar EXACTAMENTE estas):\n- Salida: {salida}\n- Corazón: {corazon}\n- Fondo: {fondo}\n"

    genero_part = f" (Género: {genero})" if genero else ""
    prompt = (
        "Eres un experto en perfumería español con conocimiento profundo de fragancias de todas las marcas. Tu única lengua es el español.\n\n"
        "INSTRUCCIÓN ABSOLUTA: Debes responder ÚNICAMENTE con un objeto JSON válido. No escribas explicaciones, notas, ni texto adicional antes o después del JSON.\n\n"
        f"Tarea: Genera la ficha técnica completa para el perfume: \"{nombre}\"{' (Marca: ' + marca + ')' if marca else ''}{genero_part}.\n"
        f"{ref_notas_text}"
        "ESQUEMA JSON REQUERIDO:\n"
        "{\n"
        '    "familia_olfativa": "Cítrico - Madera",\n'
        '    "genero": "Hombre",\n'
        '    "descripcion_corta": "Una fragancia fresca y elegante con notas cítricas y amaderadas, perfecta para el día.",\n'
        '    "ocasiones_de_uso": ["Día", "Verano", "Oficina"],\n'
        '    "notas": {\n'
        '        "salida": ["Bergamota", "Limón"],\n'
        '        "corazon": ["Rosa", "Jazmín"],\n'
        '        "fondo": ["Sándalo", "Vainilla"]\n'
        '    },\n'
        '    "clima": {\n'
        '        "primavera": 80,\n'
        '        "verano": 90,\n'
        '        "otono": 40,\n'
        '        "invierno": 10,\n'
        '        "dia": 95,\n'
        '        "noche": 20\n'
        '    },\n'
        '    "colecciones": ["Sensación de Frescura"]\n'
        "}\n\n"
        "REGLAS CRÍTICAS:\n\n"
        "1. Todo el contenido debe estar en español. Prohibido usar inglés.\n\n"
        "2. \"descripcion_corta\":\n"
        "   - Máximo 2 líneas (una oración completa, o dos cortas).\n"
        "   - DEBE ser ÚNICA y ESPECÍFICA para este perfume. NUNCA uses descripciones genéricas.\n"
        "   - CRÍTICO: Si el perfume es CÍTRICO, NO uses siempre \"fresca y elegante\". Varía con: vibrante, radiante, chispeante, luminosa, revitalizante, optimista, etc.\n"
        "   - CRÍTICO: Si el perfume es FLORAL, NO uses siempre \"elegante y sofisticada\". Varía con: poética, romántica, exuberante, delicada, primaveral, etc.\n"
        "   - CRÍTICO: Si el perfume es AMADERADO, NO uses siempre \"profundidad y elegancia\". Varía con: terroso, ahumado, noble, intenso, sereno, etc.\n"
        "   - CRÍTICO: Si el perfume es GOURMAND, NO uses siempre \"dulce y tentadora\". Varía con: golosa, comestible, azucarada, reconfortante, etc.\n"
        "   - CRÍTICO: Si el perfume es ORIENTAL, NO uses siempre \"misteriosa y sensual\". Varía con: opulenta, embriagadora, exótica, nocturna, etc.\n"
        "   - Describe la esencia, personalidad o inspiración de la fragancia de forma ÚNICA.\n"
        "   - Usa metáforas variadas: viajes, momentos del día, estaciones, emociones, lugares, obras de arte.\n"
        "   - EVITA repetir estructuras: no empieces siempre con \"Una\" o \"Composición\".\n\n"
        "3. \"ocasiones_de_uso\": lista con 3-5 palabras del conjunto: Día, Noche, Verano, Invierno, Primavera, Otoño, Oficina, Casual, Formal, Romántico, Fin de semana.\n\n"
        "4. \"notas\": cada lista (salida, corazón, fondo) debe tener 2-5 notas cada una.\n"
        "   ⚠️  ADVERTENCIA CRÍTICA:\n"
        "   - NO uses siempre las mismas notas (bergamota, limón, rosa, jazmín, sándalo, vainilla).\n"
        "   - Cada perfume tiene notas ÚNICAS y REALES. Investiga mentalmente el perfume y usa sus notas específicas.\n"
        "   - Si hay \"REFERENCIA DE NOTAS CONFIRMADAS\" arriba, USA ESAS NOTAS EXACTAMENTE.\n\n"
        "5. \"clima\": porcentajes del 0 al 100. Ajusta según la personalidad real del perfume.\n\n"
        "6. \"genero\": \"Hombre\", \"Mujer\" o \"Unisex\". Usa el género de la referencia si existe.\n\n"
        "7. \"familia_olfativa\": Usa familias precisas. Usa la de la referencia si existe.\n\n"
        "8. \"colecciones\": array con 1 o más de estas 3 colecciones EXACTAS (no inventes otras):\n"
        "   - \"Sensación de Frescura\": Solo si es CÍTRICO Y NO es dulce/gourmand.\n"
        "   - \"Noche y Seducción\": Para DULCES/GOURMAND, AMADERADOS intensos, ORIENTALES, o NOCHE/INVIERNO.\n"
        "   - \"Fuerza y Elegancia\": Para ALTA GAMA (lujo), INTENSOS, eventos FORMALES.\n"
        "   REGLA DECISIVA: Si el perfume es DULCE o GOURMAND (tiene vainilla, caramelo, chocolate, café, miel en el fondo), debe estar en \"Noche y Seducción\" y NO en \"Sensación de Frescura\".\n\n"
        "IMPORTANTE: Responde SOLO con el JSON. Sin markdown, sin ```json, sin explicaciones."
    )

    try:
        logger.info(f"Extrayendo ficha de '{nombre}' con OpenRouter (Modelo: {OPENROUTER_MODEL_TEXT})")
        temp = 0.2 if ref else 0.3
        resp = openrouter_client.chat.send(
            messages=[{"role": "user", "content": prompt}],
            model=OPENROUTER_MODEL_TEXT,
            temperature=temp,
            max_tokens=2048,
        )
        texto = resp.choices[0].message.content or ""

        texto = re.sub(r"```json\s*|```\s*", "", texto, flags=re.IGNORECASE).strip()
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                datos = json.loads(json_str)

                if not isinstance(datos, dict):
                    logger.warning(f"OpenRouter devolvió algo que no es un dict para {nombre}")
                    return {}

                tiene_datos = (
                    datos.get("notas") or
                    datos.get("descripcion_corta") or
                    datos.get("ocasiones_de_uso") or
                    datos.get("clima")
                )

                if not tiene_datos:
                    logger.warning(f"OpenRouter devolvió datos vacíos para {nombre}")
                    return {}

                # Forzar notas de referencia si existe
                if ref and "notas" in ref:
                    logger.info(f"Aplicando notas de referencia para {nombre}")
                    datos["notas"] = ref["notas"]
                    datos["genero"] = ref.get("genero", datos.get("genero", "Unisex"))
                    datos["familia_olfativa"] = ref.get("familia_olfativa", datos.get("familia_olfativa", ""))

                # Forzar género desde el CSV si se proporciona y no hay referencia
                elif genero and not ref:
                    datos["genero"] = genero

                # Derivar colecciones automáticamente basándose en familia, género y notas
                notas_para_colecciones = datos.get("notas", {})
                colecciones_derivadas = _derivar_colecciones(
                    datos.get("familia_olfativa", ""),
                    datos.get("genero", "Unisex"),
                    notas_para_colecciones
                )
                datos["colecciones"] = colecciones_derivadas
                logger.info(f"Colecciones derivadas para {nombre}: {colecciones_derivadas}")

                return datos
            except json.JSONDecodeError as e:
                logger.warning(f"JSON inválido para {nombre}: {e}")
                logger.debug(f"Texto recibido: {texto[:500]}")
                return {}

        logger.warning(f"No se detectó JSON para {nombre}")
        logger.debug(f"Texto recibido: {texto[:500]}")
        return {}
    except Exception as e:
        logger.error(f"Error extrayendo con IA para {nombre}: {e}")
        return {}


async def _extraer_ia(nombre: str, marca: str = "", genero: str = "", max_retries: int = 2) -> dict:
    """Extrae datos con IA con reintentos en caso de fallo."""
    for intento in range(max_retries):
        try:
            resultado = await asyncio.to_thread(_extraer_ia_sync, nombre, marca, genero)
            if resultado:
                return resultado
            elif intento < max_retries - 1:
                logger.warning(f"Reintentando extracción para '{nombre}' ({intento + 1}/{max_retries})")
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error en extracción IA (intento {intento + 1}): {e}")
            if intento < max_retries - 1:
                await asyncio.sleep(1)

    logger.error(f"No se pudo extraer datos para '{nombre}' después de {max_retries} intentos")
    return {}


# ─────────────────────────────────────────────
#   FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────

async def scrape_perfume(nombre: str, marca: str = "", genero: str = "") -> dict | None:
    """
    Extrae ficha técnica de un perfume usando OpenRouter + Web Scraper.
    La imagen se asignará externamente por posición.

    Retorna un dict con los datos de la fragancia.
    """
    if not openrouter_client:
        logger.error("OpenRouter no configurado")
        return None

    # Buscar referencia
    ref = referencia_notas.get(nombre)

    # 1. Extraer datos con IA (que ahora incluye scraping web)
    datos_ia = await _extraer_ia(nombre, marca, genero)
    if not datos_ia:
        logger.error(f"No se pudo extraer datos para {nombre}")
        return None

    # 2. Normalizar datos
    def _str(x):
        if isinstance(x, str):
            return x.strip()
        if isinstance(x, dict):
            return str(x.get("name", x.get("nota", x.get("nombre", x))))
        return str(x).strip()

    def _norm_lista(items):
        return [_str(x) for x in (items or []) if _str(x)]

    notas_raw = datos_ia.get("notas", {}) or {}
    notas = {
        "salida": _norm_lista(notas_raw.get("salida", [])),
        "corazon": _norm_lista(notas_raw.get("corazon", [])),
        "fondo": _norm_lista(notas_raw.get("fondo", [])),
    }
    ocasiones = _norm_lista(datos_ia.get("ocasiones_de_uso", []))
    colecciones = _norm_lista(datos_ia.get("colecciones", []))

    # 3. Si existe referencia, forzar el uso de las notas reales
    if ref:
        logger.info(f"Usando notas de referencia para {nombre}")
        notas = ref["notas"]
        datos_ia["genero"] = ref.get("genero", datos_ia.get("genero", "Unisex"))
        datos_ia["familia_olfativa"] = ref.get("familia_olfativa", datos_ia.get("familia_olfativa", ""))
        
        # Recalcular colecciones basándose en la familia y género de la referencia
        colecciones_derivadas = _derivar_colecciones(
            datos_ia.get("familia_olfativa", ""),
            datos_ia.get("genero", "Unisex"),
            notas
        )
        colecciones = colecciones_derivadas
        logger.info(f"Colecciones derivadas (con referencia) para {nombre}: {colecciones_derivadas}")

    # 4. Generar descripción variada si está disponible el módulo
    # ESTRATEGIA: Siempre usar el módulo de descripciones variadas para mayor diversidad
    # La IA tiende a repetir frases genéricas. El módulo local garantiza variación real.
    descripcion = datos_ia.get("descripcion_corta", "")
    if DESC_VAR_DISPONIBLE:
        familia = datos_ia.get("familia_olfativa", "")
        genero = datos_ia.get("genero", "Unisex")
        # Generar descripción variada basada en las notas y características
        descripcion_var = desc_var.generar_descripcion_variada(notas, genero, familia)
        # Usar la descripción variada (reemplaza la de IA)
        descripcion = descripcion_var
        logger.debug(f"Descripción variada generada para {nombre}")
    else:
        # Fallback: usar la descripción de la IA
        logger.debug(f"Usando descripción de IA para {nombre} (módulo variado no disponible)")

    return {
        "nombre": nombre,
        "url": datos_ia.get("url", ""),
        "genero": datos_ia.get("genero", "Unisex"),
        "descripcion_corta": descripcion,
        "ocasiones_de_uso": ocasiones,
        "notas": notas,
        "clima": datos_ia.get("clima", {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 0, "noche": 0}),
        "colecciones": colecciones,
        "imagen_path": None,
        "ya_procesado": False,
    }


# ─────────────────────────────────────────────
#   PRUEBA RÁPIDA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    nombre_test = "Bleu de Chanel"
    res = asyncio.run(scrape_perfume(nombre_test))
    if res:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("No se pudo extraer datos.")
