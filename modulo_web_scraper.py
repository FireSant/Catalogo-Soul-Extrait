"""
Módulo de Scraping Web — Soul Extrait
=====================================
Responsabilidades:
  1. Buscar el perfume en Fragrantica (y otras fuentes)
  2. Extraer las notas olfativas reales de la página
  3. Extraer metadatos: género, familia, descripción
  4. Retornar datos estructurados para OpenRouter
"""

import asyncio
import re
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger

# Fuentes de datos (en orden de preferencia)
FUENTES = {
    "fragrantica": {
        "base_url": "https://www.fragrantica.es",
        "search_url": "https://www.fragrantica.es/search/",
        "nombre_archivo": "fragrantica"
    },
    "fragrantica_eng": {
        "base_url": "https://www.fragrantica.com",
        "search_url": "https://www.fragrantica.com/search/",
        "nombre_archivo": "fragrantica_eng"
    }
}

# Headers para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Cache para evitar requests repetidos
CACHE_DIR = Path("data/cache_scrapeados")
CACHE_DIR.mkdir(exist_ok=True)


def limpiar_texto(texto: str) -> str:
    """Limpia texto eliminando espacios extra, saltos de línea, etc."""
    if not texto:
        return ""
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    return texto


def normalizar_nombre_url(nombre: str) -> str:
    """Normaliza el nombre para URL (sin tildes, sin caracteres especiales)."""
    nombre = nombre.lower()
    nombre = re.sub(r'[^\w\s-]', '', nombre)
    nombre = re.sub(r'\s+', '-', nombre)
    return nombre


async def buscar_url_perfume(nombre: str, marca: str = "") -> Optional[str]:
    """
    Busca un perfume en Fragrantica y retorna la URL de su ficha.

    Returns:
        URL completa de la ficha del perfume o None si no se encuentra.
    """
    session = aiohttp.ClientSession(headers=HEADERS)

    try:
        # Estrategia 1: Búsqueda directa con nombre y marca
        query = f"{nombre} {marca}".strip()
        if query:
            search_term = quote_plus(query)
            url_busqueda = f"https://www.fragrantica.es/search/?q={search_term}"
            logger.debug(f"Buscando en: {url_busqueda}")

            async with session.get(url_busqueda, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Buscar resultados
                    resultados = soup.select('.grid-2 .item-card')
                    for resultado in resultados:
                        link_elem = resultado.select_one('a[href*="/perfume/"]')
                        if link_elem:
                            href = link_elem.get('href', '')
                            if href.startswith('/'):
                                href = f"https://www.fragrantica.es{href}"
                            # Verificar que coincida con el nombre
                            texto_resultado = link_elem.get_text(strip=True).lower()
                            if nombre.lower() in texto_resultado:
                                logger.info(f"Encontrado: {href}")
                                return href

        # Estrategia 2: Búsqueda por nombre solo
        if marca:
            search_term = quote_plus(nombre)
            url_busqueda = f"https://www.fragrantica.es/search/?q={search_term}"
            logger.debug(f"Búsqueda alternativa: {url_busqueda}")

            async with session.get(url_busqueda, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    resultados = soup.select('.grid-2 .item-card')
                    for resultado in resultados:
                        link_elem = resultado.select_one('a[href*="/perfume/"]')
                        if link_elem:
                            href = link_elem.get('href', '')
                            if href.startswith('/'):
                                href = f"https://www.fragrantica.es{href}"
                            texto_resultado = link_elem.get_text(strip=True).lower()
                            # Ser más flexible: si el nombre tiene palabras clave
                            palabras_nombre = set(nombre.lower().split())
                            palabras_texto = set(texto_resultado.split())
                            if len(palabras_nombre & palabras_texto) >= 1:
                                logger.info(f"Encontrado (flexible): {href}")
                                return href

        logger.warning(f"No se encontró URL para {nombre} {marca}")
        return None

    except Exception as e:
        logger.error(f"Error buscando {nombre}: {e}")
        return None
    finally:
        await session.close()


async def extraer_notas_de_pagina(url: str) -> Dict[str, List[str]]:
    """
    Extrae las notas de la página de Fragrantica.

    Returns:
        Dict con claves: 'salida', 'corazon', 'fondo'
    """
    session = aiohttp.ClientSession(headers=HEADERS)

    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                logger.error(f"Status {response.status} para {url}")
                return {"salida": [], "corazon": [], "fondo": []}

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            notas = {"salida": [], "corazon": [], "fondo": []}

            # Buscar sección de notas
            # Fragrantica usa diferentes formatos
            # Opción 1: Buscar tablas con "Notas de salida", "Notas de corazón", etc.
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
                            # Extraer notas individuales
                            notas_individuales = [limpiar_texto(n) for n in notas_lista.split(',') if limpiar_texto(n)]

                            if 'salida' in tipo_texto:
                                notas["salida"] = notas_individuales
                            elif 'corazón' in tipo_texto or 'corazon' in tipo_texto:
                                notas["corazon"] = notas_individuales
                            elif 'fondo' in tipo_texto:
                                notas["fondo"] = notas_individuales

            # Opción 2: Buscar divs con clases específicas
            if not any(notas.values()):
                # Buscar por texto
                contenido = soup.get_text()
                # Patrones para extraer notas
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
    finally:
        await session.close()


async def extraer_metadatos_de_pagina(url: str) -> Dict:
    """
    Extrae metadatos adicionales de la página.
    """
    session = aiohttp.ClientSession(headers=HEADERS)

    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return {}

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            metadatos = {}

            # Extraer género
            genero_elem = soup.select_one('meta[name="og:description"]')
            if genero_elem:
                desc = genero_elem.get('content', '').lower()
                if 'hombre' in desc or 'men' in desc:
                    metadatos['genero'] = 'Hombre'
                elif 'mujer' in desc or 'women' in desc:
                    metadatos['genero'] = 'Mujer'
                else:
                    metadatos['genero'] = 'Unisex'

            # Extraer familia olfativa
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
    finally:
        await session.close()


async def extraer_datos_completos(nombre: str, marca: str = "") -> Optional[Dict]:
    """
    Función principal: busca y extrae todos los datos del perfume.

    Returns:
        Dict con notas, género, familia, url, descripción o None si falla.
    """
    logger.info(f"Iniciando extracción web para: {nombre} {marca}")

    # 1. Buscar URL
    url = await buscar_url_perfume(nombre, marca)
    if not url:
        logger.warning(f"No se encontró URL para {nombre}")
        return None

    # 2. Extraer notas
    notas = await extraer_notas_de_pagina(url)
    if not any(notas.values()):
        logger.warning(f"No se extrajeron notas de {url}")
        return None

    # 3. Extraer metadatos
    metadatos = await extraer_metadatos_de_pagina(url)

    resultado = {
        "nombre": nombre,
        "url": url,
        "notas": notas,
        "genero": metadatos.get('genero', 'Unisex'),
        "familia_olfativa": metadatos.get('familia_olfativa', ''),
        "descripcion": "",  # Se puede extraer también si es necesario
    }

    logger.success(f"Datos extraídos para {nombre}: {len(sum(notas.values(), []))} notas")
    return resultado


# Cache simple
def obtener_clave_cache(nombre: str, marca: str = "") -> str:
    clave = f"{nombre}_{marca}".strip().replace(' ', '_').lower()
    clave = re.sub(r'[^\w_]', '', clave)
    return clave


async def extraer_con_cache(nombre: str, marca: str = "", fuerza: bool = False) -> Optional[Dict]:
    """
    Extrae datos con cache para evitar requests repetidos.
    """
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
    datos = await extraer_datos_completos(nombre, marca)
    if datos:
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            logger.debug(f"Datos guardados en cache: {clave}")
        except Exception as e:
            logger.warning(f"Error guardando cache: {e}")

    return datos


if __name__ == "__main__":
    # Prueba rápida
    async def prueba():
        datos = await extraer_datos_completos("Bleu de Chanel", "Chanel")
        if datos:
            print(json.dumps(datos, indent=2, ensure_ascii=False))
        else:
            print("No se pudieron extraer datos")

    import json
    asyncio.run(prueba())
