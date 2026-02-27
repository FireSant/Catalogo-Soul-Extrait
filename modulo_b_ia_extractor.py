"""
Módulo B: Motor de Extracción IA — Soul Extrait
"""

import asyncio
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from openrouter import OpenRouter

load_dotenv()

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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Modelo principal: alta capacidad para notas complejas
OPENROUTER_MODEL_TEXT = "meta-llama/llama-3.3-70b-instruct:free"
# Fallbacks en caso de rate limits o errores
OPENROUTER_MODEL_FALLBACKS = [
    "openai/gpt-oss-120b:free",
    "arcee-ai/trinity-large-preview:free",
]
openrouter_client = OpenRouter(api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None


def _organizar_con_ia_sync(nombre: str, marca: str, genero: str, ref: dict = None, modelo: str = None) -> dict:
    """
    Genera ficha técnica usando solo IA (sin scraping).
    
    Parámetros
    ----------
    nombre : str
        Nombre del perfume
    marca : str
        Marca del perfume
    genero : str
        Género (Hombre/Mujer/Unisex)
    ref : dict | None
        Referencia de notas (si existe en base local)
    modelo : str | None
        Modelo específico a usar. Si None, usa OPENROUTER_MODEL_TEXT
    """
    if not openrouter_client:
        return {}

    ref_notas_text = ""
    if ref:
        salida = ', '.join(ref['notas']['salida'])
        corazon = ', '.join(ref['notas']['corazon'])
        fondo = ', '.join(ref['notas']['fondo'])
        ref_notas_text = f"\n\nREFERENCIA NOTAS (usar EXACTAMENTE):\n- Salida: {salida}\n- Corazón: {corazon}\n- Fondo: {fondo}\n"

    genero_part = f" (Género: {genero})" if genero else ""
    prompt = (
        "Eres un Maestro Perfumista experto. Tu tarea es extraer la pirámide olfativa REAL, EXACTA y COMPLETA (salida, corazón, fondo) de la base de datos de Fragrantica para el perfume indicado. No simplifiques las notas ni uses términos genéricos si el perfume tiene notas específicas (ej. si tiene \"yuzu\" o \"madera de oud\", escríbelo así). Devuelve la respuesta estrictamente en JSON en idioma ESPAÑOL. No inventes perfumes que no existen.\n\n"
        f"Perfume: \"{nombre}\"{' (Marca: ' + marca + ')' if marca else ''}{genero_part}.\n"
        f"{ref_notas_text}"
        "ESQUEMA JSON:\n"
        "{\n"
        '    "familia_olfativa": "Familia olfativa",\n'
        '    "genero": "Hombre/Mujer/Unisex",\n'
        '    "descripcion_corta": "Descripción (máx 2 líneas)",\n'
        '    "ocasiones_de_uso": ["Día", "Noche"],\n'
        '    "notas": {"salida": [], "corazon": [], "fondo": []},\n'
        '    "clima": {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 0, "noche": 0}\n'
        "}\n"
    )

    try:
        # Usar modelo especificado o el predeterminado
        modelo_a_usar = modelo if modelo else OPENROUTER_MODEL_TEXT
        resp = openrouter_client.chat.send(
            messages=[{"role": "user", "content": prompt}],
            model=modelo_a_usar,
            temperature=0.3,
            max_tokens=1024,
        )
        texto = resp.choices[0].message.content or ""
        texto = re.sub(r"```json\s*|```\s*", "", texto, flags=re.IGNORECASE).strip()
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            datos = json.loads(match.group(0))
            if isinstance(datos, dict) and datos.get("notas"):
                return datos
    except Exception:
        pass
    return {}


def _extraer_ia_sync(nombre: str, marca: str = "", genero: str = "", modelo: str = None) -> dict:
    """Extracción síncrona con modelo opcional."""
    if not openrouter_client:
        return {}

    ref = referencia_notas.get(nombre)
    # Generar ficha técnica directamente con IA
    return _organizar_con_ia_sync(nombre, marca, genero, ref, modelo)


async def _extraer_ia(nombre: str, marca: str = "", genero: str = "", max_retries: int = 2) -> dict:
    """
    Intenta extraer datos de IA probando modelo principal y fallbacks.
    Estrategia: 1er intento → modelo principal, 2do → fallback 1, 3er → fallback 2
    """
    modelos = [OPENROUTER_MODEL_TEXT] + OPENROUTER_MODEL_FALLBACKS
    
    for modelo_idx, modelo in enumerate(modelos):
        for intento in range(max_retries):
            try:
                # Pasar modelo específico a _extraer_ia_sync
                resultado = await asyncio.to_thread(
                    _extraer_ia_sync,
                    nombre, marca, genero,
                    modelo  # pasar modelo específico
                )
                if resultado:
                    logger.info(f"Extracción exitosa con modelo: {modelo}")
                    return resultado
                if intento < max_retries - 1:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Intento {intento+1} con modelo {modelo} falló: {e}")
                if intento < max_retries - 1:
                    await asyncio.sleep(1)
    return {}


async def scrape_perfume(nombre: str, marca: str = "", genero: str = "") -> dict | None:
    if not openrouter_client:
        return None

    datos_ia = await _extraer_ia(nombre, marca, genero)
    if not datos_ia:
        return None

    # Normalizar
    def _str(x):
        if isinstance(x, str):
            return x.strip()
        if isinstance(x, dict):
            return str(x.get("name", x.get("nota", x.get("nombre", x))))
        return str(x).strip()

    def _norm(items):
        return [_str(x) for x in (items or []) if _str(x)]

    notas_raw = datos_ia.get("notas", {}) or {}
    notas = {
        "salida": _norm(notas_raw.get("salida", [])),
        "corazon": _norm(notas_raw.get("corazon", [])),
        "fondo": _norm(notas_raw.get("fondo", [])),
    }
    ocasiones = _norm(datos_ia.get("ocasiones_de_uso", []))

    return {
        "nombre": nombre,
        "url": datos_ia.get("url", ""),
        "genero": datos_ia.get("genero", "Unisex"),
        "descripcion_corta": datos_ia.get("descripcion_corta", ""),
        "ocasiones_de_uso": ocasiones,
        "notas": notas,
        "clima": datos_ia.get("clima", {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 0, "noche": 0}),
        "imagen_path": None,
        "ya_procesado": False,
    }


if __name__ == "__main__":
    import json
    nombre_test = "Bleu de Chanel"
    res = asyncio.run(scrape_perfume(nombre_test))
    if res:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("No se pudo extraer datos.")
