"""
Módulo de Scraping Web Síncrono — Soul Extrait
==============================================
Versión síncrona para usar en contextos donde no se puede usar asyncio.
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, List

import requests
from bs4 import BeautifulSoup
from loguru import logger

# Headers para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Cache
CACHE_DIR = Path("data/cache_scrapeados")
CACHE_DIR.mkdir(exist_ok=True)


def limpiar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    return texto


def buscar_url_perfume_sync(nombre: str, marca: str = "") -> Optional[str]:
    """Versión síncrona de búsqueda de URL."""
    try:
        # Estrategia 1: Búsqueda directa
        query = f"{nombre} {marca}".strip()
        if query:
            search_term = requests.utils.quote(query)
            url_busqueda = f"https://www.fragrantica.es/search/?q={search_term}"
            logger.debug(f"Buscando (síncrono): {url_busqueda}")

            response = requests.get(url_busqueda, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Múltiples selectores para mayor compatibilidad
                selectores = [
                    '.grid-2 .item-card',
                    '.search-results .item',
                    '.results .item-card',
                    'div[class*="item"]',
                    'a[href*="/perfume/"]'
                ]
                
                for selector in selectores:
                    resultados = soup.select(selector)
                    if resultados:
                        logger.debug(f"Selector '{selector}' encontró {len(resultados)} resultados")
                        for resultado in resultados:
                            link_elem = resultado if resultado.name == 'a' else resultado.select_one('a[href*="/perfume/"]')
                            if link_elem:
                                href = link_elem.get('href', '')
                                if href.startswith('/'):
                                    href = f"https://www.fragrantica.es{href}"
                                texto_resultado = link_elem.get_text(strip=True).lower()
                                # Verificar que el nombre esté en el texto
                                if nombre.lower() in texto_resultado:
                                    logger.info(f"Encontrado URL: {href}")
                                    return href
                                # O verificar que coincida al menos una palabra
                                palabras_nombre = set(nombre.lower().split())
                                palabras_texto = set(texto_resultado.split())
                                if len(palabras_nombre & palabras_texto) >= 1:
                                    logger.info(f"Encontrado URL (flexible): {href}")
                                    return href

        # Estrategia 2: Búsqueda por nombre solo
        if marca:
            search_term = requests.utils.quote(nombre)
            url_busqueda = f"https://www.fragrantica.es/search/?q={search_term}"
            response = requests.get(url_busqueda, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for selector in selectores:
                    resultados = soup.select(selector)
                    for resultado in resultados:
                        link_elem = resultado if resultado.name == 'a' else resultado.select_one('a[href*="/perfume/"]')
                        if link_elem:
                            href = link_elem.get('href', '')
                            if href.startswith('/'):
                                href = f"https://www.fragrantica.es{href}"
                            texto_resultado = link_elem.get_text(strip=True).lower()
                            palabras_nombre = set(nombre.lower().split())
                            palabras_texto = set(texto_resultado.split())
                            if len(palabras_nombre & palabras_texto) >= 1:
                                logger.info(f"Encontrado URL (flexible): {href}")
                                return href

        # Estrategia 3: Construir URL directa (patrón común de Fragrantica)
        nombre_url = nombre.lower().replace(' ', '-').replace("'", "").replace('"', "")
        url_directa = f"https://www.fragrantica.es/perfume/{marca.lower().replace(' ', '-')}/{nombre_url}/"
        logger.debug(f"Intentando URL directa: {url_directa}")
        response = requests.get(url_directa, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            logger.info(f"URL directa encontrada: {url_directa}")
            return url_directa

        logger.warning(f"No se encontró URL para {nombre} {marca}")
        return None

    except Exception as e:
        logger.error(f"Error buscando {nombre}: {e}")
        return None


def extraer_notas_de_pagina_sync(url: str) -> Dict[str, List[str]]:
    """Versión síncrona de extracción de notas."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.error(f"Status {response.status_code} para {url}")
            return {"salida": [], "corazon": [], "fondo": []}

        soup = BeautifulSoup(response.text, 'html.parser')
        notas = {"salida": [], "corazon": [], "fondo": []}

        # Opción 1: Buscar tablas
        tablas = soup.select('table')
        for tabla in tablas:
            texto_tabla = tabla.get_text(strip=True).lower()
            if 'salida' in texto_tabla or 'corazón' in texto_tabla or 'fondo' in texto_tabla:
                filas = tabla.select('tr')
                for fila in filas:
                    celdas = fila.select('td')
                    if len(celdas) >= 2:
                        tipo_texto = celdas[0].get_text(strip=True).lower()
                        notas_lista = celdas[1].get_text(strip=True)
                        notas_individuales = [limpiar_texto(n) for n in notas_lista.split(',') if limpiar_texto(n)]

                        if 'salida' in tipo_texto:
                            notas["salida"] = notas_individuales
                        elif 'corazón' in tipo_texto or 'corazon' in tipo_texto:
                            notas["corazon"] = notas_individuales
                        elif 'fondo' in tipo_texto:
                            notas["fondo"] = notas_individuales

        # Opción 2: Buscar por texto con regex
        if not any(notas.values()):
            contenido = soup.get_text()
            patrones = {
                "salida": r'Notas?\s+de\s+salida[:\s]+([^\n]+)',
                "corazon": r'Notas?\s+de\s+(?:corazón|corazon)[:\s]+([^\n]+)',
                "fondo": r'Notas?\s+de\s+fondo[:\s]+([^\n]+)'
            }

            for tipo, patron in patrones.items():
                match = re.search(patron, contenido, re.IGNORECASE)
                if match:
                    texto_notas = match.group(1)
                    notas[tipo] = [limpiar_texto(n) for n in texto_notas.split(',') if limpiar_texto(n)]

        logger.info(f"Notas extraídas de {url}: {notas}")
        return notas

    except Exception as e:
        logger.error(f"Error extrayendo notas de {url}: {e}")
        return {"salida": [], "corazon": [], "fondo": []}


def extraer_metadatos_sync(url: str) -> Dict:
    """Versión síncrona de extracción de metadatos."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        metadatos = {}

        # Género
        genero_elem = soup.select_one('meta[name="og:description"]')
        if genero_elem:
            desc = genero_elem.get('content', '').lower()
            if 'hombre' in desc or 'men' in desc:
                metadatos['genero'] = 'Hombre'
            elif 'mujer' in desc or 'women' in desc:
                metadatos['genero'] = 'Mujer'
            else:
                metadatos['genero'] = 'Unisex'

        # Familia
        contenido = soup.get_text()
        familias = ['Cítrico', 'Floral', 'Oriental', 'Gourmand', 'Aromático', 'Acuático', 'Madera', 'Cuero', 'Verde']
        for familia in familias:
            if familia.lower() in contenido.lower():
                metadatos['familia_olfativa'] = familia
                break

        return metadatos

    except Exception as e:
        logger.error(f"Error extrayendo metadatos: {e}")
        return {}


def extraer_datos_completos_sync(nombre: str, marca: str = "") -> Optional[Dict]:
    """Versión síncrona de extracción completa."""
    logger.info(f"Iniciando extracción web (síncrona) para: {nombre} {marca}")

    # 1. Buscar URL
    url = buscar_url_perfume_sync(nombre, marca)
    if not url:
        logger.warning(f"No se encontró URL para {nombre}")
        return None

    # 2. Extraer notas
    notas = extraer_notas_de_pagina_sync(url)
    if not any(notas.values()):
        logger.warning(f"No se extrajeron notas de {url}")
        return None

    # 3. Extraer metadatos
    metadatos = extraer_metadatos_sync(url)

    resultado = {
        "nombre": nombre,
        "url": url,
        "notas": notas,
        "genero": metadatos.get('genero', 'Unisex'),
        "familia_olfativa": metadatos.get('familia_olfativa', ''),
        "descripcion": "",
    }

    logger.success(f"Datos extraídos para {nombre}: {sum(len(v) for v in notas.values())} notas")
    return resultado


def obtener_clave_cache(nombre: str, marca: str = "") -> str:
    clave = f"{nombre}_{marca}".strip().replace(' ', '_').lower()
    clave = re.sub(r'[^\w_]', '', clave)
    return clave


def extraer_con_cache_sync(nombre: str, marca: str = "", fuerza: bool = False) -> Optional[Dict]:
    """Extrae datos con cache (versión síncrona)."""
    clave = obtener_clave_cache(nombre, marca)
    cache_file = CACHE_DIR / f"{clave}.json"

    if cache_file.exists() and not fuerza:
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            logger.info(f"Datos cargados desde cache: {clave}")
            return datos
        except Exception as e:
            logger.warning(f"Error leyendo cache {clave}: {e}")

    # Extraer datos frescos
    datos = extraer_datos_completos_sync(nombre, marca)
    if datos:
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            logger.debug(f"Datos guardados en cache: {clave}")
        except Exception as e:
            logger.warning(f"Error guardando cache: {e}")

    return datos


if __name__ == "__main__":
    import json
    datos = extraer_datos_completos_sync("Bleu de Chanel", "Chanel")
    if datos:
        print(json.dumps(datos, indent=2, ensure_ascii=False))
    else:
        print("No se pudieron extraer datos")
