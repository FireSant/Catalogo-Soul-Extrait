"""
Módulo B: Motor de Extracción IA — Soul Extrait
===============================================
Flujo:
    1. Extrae ficha técnica con OpenRouter (modelo gratuito)
    2. Retorna diccionario con ficha (la imagen se asigna externamente por posición)
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

# Configuración
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Modelo de Meta (LLaMA) - Solo texto, sin visión
OPENROUTER_MODEL_TEXT = "meta-llama/llama-3.1-8b-instruct"

openrouter_client = OpenRouter(api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None


def _slug(nombre: str) -> str:
    s = re.sub(r"[^\w\s-]", "", unicodedata.normalize("NFD", nombre).encode("ascii", "ignore").decode()).strip().lower()
    return re.sub(r"\s+", "_", s)


# ─────────────────────────────────────────────
#   EXTRACCIÓN IA (OPENROUTER)
# ─────────────────────────────────────────────

def _extraer_ia_sync(nombre: str, marca: str = "") -> dict:
    if not openrouter_client:
        logger.error("OpenRouter no configurado")
        return {}

    prompt = f"""Eres un experto en perfumería español. Tu única lengua es el español.

INSTRUCCIÓN ABSOLUTA: Debes responder ÚNICAMENTE con un objeto JSON válido. No escribas explicaciones, notas, ni texto adicional antes o después del JSON.

Tarea: Genera la ficha técnica completa para el perfume: "{nombre}"{' (Marca: ' + marca + ')' if marca else ''}.

ESQUEMA JSON REQUERIDO:
{{
    "familia_olfativa": "Cítrico Aromático",
    "genero": "Hombre",
    "descripcion_corta": "Una fragancia fresca y elegante con notas cítricas y amaderadas, perfecta para el día.",
    "ocasiones_de_uso": ["Día", "Verano", "Oficina"],
    "notas": {{
        "salida": ["Bergamota", "Limón"],
        "corazon": ["Rosa", "Jazmín"],
        "fondo": ["Sándalo", "Vainilla"]
    }},
    "clima": {{
        "primavera": 80,
        "verano": 90,
        "otono": 40,
        "invierno": 10,
        "dia": 95,
        "noche": 20
    }}
}}

REGLAS CRÍTICAS:
1. Todo el contenido debe estar en español. Prohibido usar inglés.
2. "descripcion_corta": oración completa (máximo 2 líneas) que describa la fragancia.
3. "ocasiones_de_uso": lista con 3-5 palabras del conjunto: Día, Noche, Verano, Invierno, Primavera, Otoño, Oficina, Casual, Formal, Romántico, Fin de semana.
4. "notas": cada lista (salida, corazón, fondo) debe tener 2-5 notas cada una. Usa nombres en español: Bergamota, Rosa, Sándalo, Vainilla, etc.
5. "clima": porcentajes del 0 al 100 para cada estación/momento. La suma no necesita ser 100.
6. "genero": "Hombre", "Mujer" o "Unisex".

IMPORTANTE: Responde SOLO con el JSON. Sin markdown, sin ```json, sin explicaciones."""

    try:
        logger.info(f"Extrayendo ficha de '{nombre}' con OpenRouter (Modelo: {OPENROUTER_MODEL_TEXT})")
        resp = openrouter_client.chat.send(
            messages=[{"role": "user", "content": prompt}],
            model=OPENROUTER_MODEL_TEXT,
            temperature=0.3,
            max_tokens=2048,
        )
        texto = resp.choices[0].message.content or ""

        # Limpiar y extraer JSON
        texto = re.sub(r"```json\s*|```\s*", "", texto, flags=re.IGNORECASE).strip()

        # Buscar el primer objeto JSON completo
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                datos = json.loads(json_str)

                # Validar que los datos sean un diccionario con campos esperados
                if not isinstance(datos, dict):
                    logger.warning(f"OpenRouter devolvió algo que no es un dict para {nombre}")
                    return {}

                # Verificar que tenga al menos algunos campos clave con datos
                tiene_datos = (
                    datos.get("notas") or
                    datos.get("descripcion_corta") or
                    datos.get("ocasiones_de_uso") or
                    datos.get("clima")
                )

                if not tiene_datos:
                    logger.warning(f"OpenRouter devolvió datos vacíos para {nombre}")
                    return {}

                return datos
            except json.JSONDecodeError as e:
                logger.warning(f"JSON inválido para {nombre}: {e}")
                logger.debug(f"Texto recibido: {texto[:500]}")
                return {}

        logger.warning(f"No se detectó JSON para {nombre}")
        logger.debug(f"Texto recibido: {texto[:500]}")
        return {}
    except Exception as e:
        logger.error(f"Error OpenRouter para {nombre}: {e}")
        return {}


async def _extraer_ia(nombre: str, marca: str = "", max_retries: int = 2) -> dict:
    """Extrae datos con IA con reintentos en caso de fallo."""
    for intento in range(max_retries):
        try:
            resultado = await asyncio.to_thread(_extraer_ia_sync, nombre, marca)
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

async def scrape_perfume(nombre: str, marca: str = "") -> dict | None:
    """
    Extrae ficha técnica de un perfume usando OpenRouter.
    La imagen se asignará externamente por posición desde la carpeta imagenes_perfumes/.

    Retorna un dict con los datos de la fragancia. El campo 'imagen_path' se dejara como None
    y será completado por el orquestador (main.py) según el índice del perfume.
    """
    if not openrouter_client:
        logger.error("OpenRouter no configurado")
        return None

    # 1. Extraer datos con IA
    datos_ia = await _extraer_ia(nombre, marca)
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

    return {
        "nombre": nombre,
        "url": "",  # Ya no se obtiene URL de imagen
        "genero": datos_ia.get("genero", "Unisex"),
        "descripcion_corta": datos_ia.get("descripcion_corta", ""),
        "ocasiones_de_uso": ocasiones,
        "notas": notas,
        "clima": datos_ia.get("clima", {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 0, "noche": 0}),
        "imagen_path": None,  # Será asignado por main.py
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
