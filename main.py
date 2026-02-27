"""
Soul Extrait — Orquestador Principal
=====================================
Este script integra todos los módulos del sistema:
  A. Orquestador de Entrada (Lectura y Caché)
  B. Motor de Extracción IA (OpenRouter)
  C. Procesador de Datos (Traducción y Lógica)
  D. Generador de PDF (Catálogo Final)
"""

import asyncio
import sys
from pathlib import Path

from loguru import logger
from tqdm import tqdm

import modulo_a_input as mod_a
import modulo_b_ia_extractor as mod_b
import modulo_c_processor as mod_c
import modulo_d_pdf as mod_d

# ─────────────────────────────────────────────
#   CONFIGURACIÓN
# ─────────────────────────────────────────────

# Archivo de entrada predeterminado
INPUT_LIST = Path("data/lista_perfumes.csv")  # Lista completa de producción
OUTPUT_PDF = Path("output/catalogo_soul_extrait.pdf")
IMAGENES_TEMP_DIR = Path("imagenes_temp")  # Carpeta con imágenes manuales


async def main():
    logger.info("--- Iniciando Proceso Soul Extrait ---")
    
    # 1. Cargar lista de perfumes
    try:
        df_input = mod_a.cargar_lista(INPUT_LIST)
    except FileNotFoundError:
        logger.error(f"No se encontró el archivo {INPUT_LIST}. Por favor créalo en la carpeta /data/")
        return
    except Exception as e:
        logger.error(f"Error cargando lista: {e}")
        return

    # 2. Obtener lista de perfumes (pendientes y en caché) manteniendo orden original
    # Creamos un mapping de nombre -> índice original para asignar imágenes correctamente
    nombres_a_indice = {nombre: idx for idx, nombre in enumerate(df_input["nombre"].tolist())}
    
    perfumes_pendientes = mod_a.obtener_perfumes_pendientes(df_input)
    
    if not perfumes_pendientes:
        logger.warning("No hay perfumes por procesar.")
        return

    # 3. Cargar imágenes manuales de la carpeta imagenes_temp/
    imagenes_disponibles = []
    if IMAGENES_TEMP_DIR.exists():
        # Obtener archivos de imagen comunes, ordenados alfabéticamente
        extensiones_imagen = (".jpg", ".jpeg", ".png", ".webp")
        for ext in extensiones_imagen:
            imagenes_disponibles.extend(IMAGENES_TEMP_DIR.glob(f"*{ext}"))
        # Ordenar por nombre de archivo
        imagenes_disponibles = sorted(imagenes_disponibles, key=lambda p: p.name.lower())
        logger.info(f"Encontradas {len(imagenes_disponibles)} imágenes en {IMAGENES_TEMP_DIR}/")
    else:
        logger.warning(f"Carpeta de imágenes no encontrada: {IMAGENES_TEMP_DIR}/")
        logger.warning("Se procederá sin imágenes (imagen_path = None)")

    resultados_finales = []
    
    # 4. Ciclo de procesamiento (Extracción IA + Asignación de Imagen + Procesado)
    # Usamos tqdm para barra de progreso en consola
    pbar = tqdm(perfumes_pendientes, desc="Procesando Catálogo", unit="perfume")
    
    for p in pbar:
        nombre_perfume = p["nombre"]
        pbar.set_postfix({"perfume": nombre_perfume[:15]})
        
        # Obtener índice original en la lista para asignar imagen correcta
        idx_original = nombres_a_indice.get(nombre_perfume, len(imagenes_disponibles))
        
        datos_scraping = None
        
        # Caso A: Ya está en caché (Módulo A lo detectó)
        if p.get("estado") == "en_cache":
            logger.debug(f"Reperando desde caché: {nombre_perfume}")
            datos_scraping = mod_a.cargar_desde_cache(nombre_perfume)
        
        # Caso B: Hay que extraer con OpenRouter
        else:
            logger.info(f"Extrayendo datos: {nombre_perfume}...")
            marca = p.get("marca", "") or ""
            genero = p.get("genero", "") or ""
            datos_scraping = await mod_b.scrape_perfume(nombre_perfume, marca=marca, genero=genero)
            
            if datos_scraping:
                # Guardar en caché para la próxima
                mod_a._guardar_en_cache(datos_scraping)
            else:
                logger.error(f"No se pudo obtener datos de: {nombre_perfume}")
                continue
        
        # 5. Asignar imagen por posición original en la lista (no por índice del bucle)
        img_path = None
        if idx_original < len(imagenes_disponibles):
            img_path = imagenes_disponibles[idx_original]
            logger.debug(f"Imagen asignada a '{nombre_perfume}': {img_path.name} (índice original: {idx_original})")
        else:
            logger.warning(f"Perfume '{nombre_perfume}' no tiene imagen correspondiente (índice original: {idx_original}, total imágenes: {len(imagenes_disponibles)})")
            img_path = None
        
        # Asegurar que el campo imagen_path esté presente
        if datos_scraping is not None:
            datos_scraping["imagen_path"] = img_path
        
        # 6. Procesar datos (Módulo C)
        # Enriquecemos con los datos extra del input (ml, marca)
        datos_limpios = mod_c.procesar(datos_scraping, p)
        resultados_finales.append(datos_limpios)

    if not resultados_finales:
        logger.error("No se obtuvieron resultados válidos para generar el PDF.")
        return

    # 7. Generar PDF (Módulo D)
    logger.info(f"Generando PDF con {len(resultados_finales)} perfumes...")
    gen = mod_d.GeneradorCatalog(str(OUTPUT_PDF))
    
    # Portada e Índice
    gen.crear_portada()
    gen.crear_indice(resultados_finales)
    
    # Fichas técnicas (vinculadas al índice)
    for i, datos in enumerate(resultados_finales):
        gen.agregar_perfume(datos, gen.items_indice[i])
    
    gen.guardar()
    
    logger.success("--- Proceso Completado con Éxito ---")
    print(f"\n[OK] Catalogo generado en: {OUTPUT_PDF.absolute()}")


if __name__ == "__main__":
    # Asegurar que existan las carpetas necesarias
    Path("data").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    # La carpeta imagenes_temp debe existir con las imágenes manuales
    IMAGENES_TEMP_DIR.mkdir(exist_ok=True)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Proceso interrumpido por el usuario.")
    except Exception as e:
        logger.exception(f"Error fatal en el orquestador: {e}")
        sys.exit(1)
