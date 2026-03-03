"""
Modulo D: Generador de PDF - Soul Extrait
==========================================
Responsabilidades:
  1. Crear un PDF elegante y profesional.
  2. Pagina de portada y aviso legal/intro.
  3. Índice interactivo (enlaces internos).
  4. Fichas tecnicas por perfume:
     - Imagen del frasco (auto-ajustada).
     - Piramide olfativa (Salida, Corazon, Fondo).
     - Atributos de clima/estacion con iconos.
     - Boton de consulta via WhatsApp.
"""

import os
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from difflib import get_close_matches

from dotenv import load_dotenv
from fpdf import FPDF
from loguru import logger
from PIL import Image

# Cargar variables de entorno
load_dotenv()

# ─────────────────────────────────────────────
#   RUTAS Y CONFIGURACIÓN
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent

COLOR_PRIMARIO = (0, 0, 0)      # Negro (coincide con el logo)
COLOR_ACENTO   = (140, 140, 140) # Gris elegante (antes Naranja)
COLOR_RECUADRO = (229, 229, 229) # Gris Claro
COLOR_TEXTO    = (0, 0, 0)
COLOR_FONDO    = (245, 241, 225) # Beige/Crema que coincide con el logo

WHATSAPP_NUM = os.getenv("WHATSAPP_NUMERO", "593983548396")
WHATSAPP_MSG = os.getenv("WHATSAPP_MENSAJE", "Hola, me interesa este perfume del catálogo Soul Extrait")


def encontrar_imagen_perfume(nombre: str, marca: str = "", genero: str = "", directorio_imagenes: str | Path = "imagenes_temp") -> Path | None:
    """
    Encuentra la imagen más parecida al perfume usando fuzzy matching,
    considerando el género para desambiguar entre versiones (ej: Light Blue Hombre/Mujer).

    Parámetros
    ----------
    nombre : str
        Nombre del perfume (del CSV)
    marca : str
        Marca del perfume (del CSV)
    genero : str
        Género del perfume (Hombre, Mujer, Unisex)
    directorio_imagenes : str | Path
        Carpeta donde están las imágenes

    Retorna
    -------
    Path | None
        Ruta a la imagen encontrada, o a default.jpg si no hay coincidencia.
    """
    dir_path = Path(directorio_imagenes)
    if not dir_path.exists():
        logger.warning(f"Directorio de imágenes no existe: {dir_path}")
        return None

    # Normalizar género
    genero_lower = (genero or "").lower()
    
    # Palabras clave para identificar género en los nombres de archivo
    keywords_hombre = ["hombre", "male", "men", "man", "him", "masculino", "masculine", "pour_homme", "homme", "him"]
    keywords_mujer = ["mujer", "female", "women", "woman", "her", "femenino", "feminine", "pour_femme", "femme", "her"]
    
    # Limpiar palabras de género del nombre (mujer, hombre, her, him, femme, homme, etc.)
    # para que "Light Blue Mujer" coincida con "light_blue_dolce_gabbana"
    palabras_a_eliminar = [
        r"\bmujer\b", r"\bhombre\b", r"\bher\b", r"\bhim\b",
        r"\bfemme\b", r"\bhomme\b", r"\bwomen\b", r"\bmen\b",
        r"\bwoman\b", r"\bman\b", r"\bgirl\b", r"\bboy\b"
    ]
    nombre_limpio = nombre.lower()
    for patron in palabras_a_eliminar:
        nombre_limpio = re.sub(patron, "", nombre_limpio, flags=re.IGNORECASE)
    
    # Crear "nombre objetivo" normalizado: solo el nombre del perfume (sin marca)
    # Esto evita que la marca interfiera en el fuzzy matching cuando el archivo no la incluye
    nombre_objetivo = re.sub(r"[^a-z0-9\s]", "", nombre_limpio)  # Quitar caracteres especiales
    nombre_objetivo = re.sub(r"\s+", "_", nombre_objetivo.strip())  # Espacios → guiones bajos
    
    # Preparar nombre_busqueda (sin espacios, guiones, etc.) para comparaciones
    nombre_busqueda = nombre.lower().replace(" ", "").replace("-", "").replace("'", "").lower()
    
    # Para nombres de 1 carácter, incluir la marca en el nombre objetivo para fuzzy matching
    # (evita falsos positivos en búsqueda por subcadena)
    if len(nombre_busqueda) == 1 and marca:
        marca_limpia = re.sub(r"[^a-z0-9\s]", "", marca.lower())
        marca_limpia = re.sub(r"\s+", "_", marca_limpia.strip())
        nombre_objetivo = f"{nombre_objetivo}_{marca_limpia}"

    # Obtener lista de archivos de imagen disponibles
    extensiones_imagen = (".jpg", ".jpeg", ".png", ".webp", ".avif")
    archivos_disponibles = []
    for ext in extensiones_imagen:
        archivos_disponibles.extend(dir_path.glob(f"*{ext}"))

    if not archivos_disponibles:
        logger.warning(f"No se encontraron imágenes en {dir_path}")
        return None

    # Extraer nombres de archivo (sin extensión) para comparar
    nombres_archivo = []
    for archivo in archivos_disponibles:
        nombre_sin_ext = archivo.stem.lower()  # Nombre sin extensión
        nombres_archivo.append((nombre_sin_ext, archivo))

    # Si no hay imágenes, retornar None
    if not nombres_archivo:
        return None

    # ─────────────────────────────────────────────────────────
    # ESTRATEGIA DE BÚSQUEDA CON GÉNERO
    # ─────────────────────────────────────────────────────────
    
    # 1. Primero, filtrar por género si está especificado
    candidatos_genero = []
    if genero_lower in ["hombre", "male", "men", "man", "masculino", "masculine"]:
        # Buscar imágenes que contengan palabras clave de hombre
        for nombre_sin_ext, archivo in nombres_archivo:
            if any(keyword in nombre_sin_ext for keyword in keywords_hombre):
                candidatos_genero.append((nombre_sin_ext, archivo))
    elif genero_lower in ["mujer", "female", "women", "woman", "femenino", "feminine"]:
        # Buscar imágenes que contengan palabras clave de mujer
        for nombre_sin_ext, archivo in nombres_archivo:
            if any(keyword in nombre_sin_ext for keyword in keywords_mujer):
                candidatos_genero.append((nombre_sin_ext, archivo))
    else:
        # Para Unisex o género no especificado, considerar todos
        candidatos_genero = nombres_archivo.copy()
    
    # 2. Intentar encontrar coincidencia en los candidatos con género
    if candidatos_genero:
        # 2a. Para nombres de 1 carácter, saltar a fuzzy matching directamente
        # (la búsqueda por subcadena es demasiado permisiva y genera falsos positivos)
        nombre_busqueda = nombre.lower().replace(" ", "").replace("-", "").replace("'", "").lower()
        if len(nombre_busqueda) <= 1:
            # Saltar a 2c (fuzzy matching)
            pass
        else:
            for nombre_sin_ext, archivo in candidatos_genero:
                archivo_nombre = nombre_sin_ext.replace("_", "").replace(" ", "").replace("-", "").replace("'", "").lower()
                if nombre_busqueda in archivo_nombre or archivo_nombre in nombre_busqueda:
                    logger.info(f"Imagen encontrada por subcadena para '{nombre}' ({genero}): {archivo.name}")
                    return archivo
        
        # 2b. Si no hay subcadena, buscar por marca (solo si también contiene el nombre)
        # Para nombres de 1 carácter, saltar a fuzzy matching (demasiado permisivo)
        if marca and len(nombre_busqueda) > 1:
            marca_busqueda = marca.lower().replace(" ", "").replace("&", "").replace(".", "")
            for nombre_sin_ext, archivo in candidatos_genero:
                archivo_nombre = nombre_sin_ext.replace("_", "").replace(" ", "").lower()
                if marca_busqueda in archivo_nombre:
                    # Verificar que el nombre del perfume también esté presente
                    if len(nombre_busqueda) == 2:
                        # Para nombres de 2 caracteres, usar búsqueda de palabra completa
                        patron_nombre = r'(^|[_\-.\s])' + re.escape(nombre_busqueda) + r'($|[_\-.\s])'
                        if re.search(patron_nombre, archivo_nombre, re.IGNORECASE):
                            logger.info(f"Imagen encontrada por marca (con nombre) para '{nombre}' ({marca}, {genero}): {archivo.name}")
                            return archivo
                    else:
                        if nombre_busqueda in archivo_nombre:
                            logger.info(f"Imagen encontrada por marca (con nombre) para '{nombre}' ({marca}, {genero}): {archivo.name}")
                            return archivo
        
        # 2c. Si no hay subcadena ni marca, usar fuzzy matching con cutoff más alto
        lista_candidatos = [n[0] for n in candidatos_genero]
        coincidencias = get_close_matches(nombre_objetivo, lista_candidatos, n=1, cutoff=0.8)
        
        if coincidencias:
            # Verificar que la coincidencia no sea demasiado genérica
            # (evitar que "Legend" coincida con "Explorer" por ejemplo)
            mejor_match = coincidencias[0]
            # La coincidencia debe contener al menos una palabra clave del nombre original
            palabras_clave = nombre_objetivo.replace('_', '').lower()
            match_limpio = mejor_match.replace('_', '').lower()
            
            # Si la coincidencia es muy genérica (ej: "legend" para "explorer"), no usarla
            if len(match_limpio) < len(palabras_clave) * 0.7:
                logger.warning(f"Fuzzy match demasiado débil para '{nombre}': '{mejor_match}' ({(len(match_limpio)/len(palabras_clave)*100):.0f}%)")
            else:
                # Buscar el archivo correspondiente al nombre coincidente
                for nombre_sin_ext, archivo in candidatos_genero:
                    if nombre_sin_ext == mejor_match:
                        logger.info(f"Imagen encontrada (fuzzy) para '{nombre}' ({marca}, {genero}): {archivo.name}")
                        return archivo
    
    # 2d. Si NO hay coincidencias en candidatos con género (candidatos_genero vacío o sin match),
    #      intentar inferir género de los archivos y filtrar ANTES de búsqueda global
    if genero_lower:
        # No hay candidatos con género, intentar inferir género del archivo
        candidatos_por_genero_inferido = []
        keywords_hombre_extra = ["1_million", "invictus", "phantom", "eros", "le_male", "ultra_male", "bad_boy", "toy_boy", "stronger_with_you", "bottled", "bleu", "sauvage", "dior", "fahrenheit", "explorer", "legend", "polo_blue", "y_ysl", "dylan_blue", "acqua_di_gio", "212_vip_men", "club_de_nuit_intense_man", "asad", "aventus", "hawas", "terre_d'hermes", "valentino_uomo", "paco_rabanne"]
        keywords_mujer_extra = ["lady_million", "ariana_grande", "coco_mademoiselle", "j'adore", "la_vie_est_belle", "libre", "black_opium", "miss_dior", "fantasy", "bright_crystal", "can_can", "chanel_5", "cloud", "good_girl_blush", "idole", "light_blue_mujer", "scandal_mujer", "si", "sweet_like_candy", "thank_u_next", "yara", "212_vip_rose", "my_way", "olympea", "baccarat_rouge_540", "lost_cherry", "ombre_nomade", "santal_33", "tobacco_vanille", "hacivat", "khamrah"]
        
        for nombre_sin_ext, archivo in nombres_archivo:
            archivo_lower = nombre_sin_ext.lower()
            if genero_lower in ["hombre", "male", "men", "man", "masculino", "masculine"]:
                # Para hombre, preferir archivos que NO contengan palabras de mujer
                es_mujer = any(kw in archivo_lower for kw in keywords_mujer_extra) or any(kw in archivo_lower for kw in keywords_mujer)
                if not es_mujer:
                    candidatos_por_genero_inferido.append((nombre_sin_ext, archivo))
            elif genero_lower in ["mujer", "female", "women", "woman", "femenino", "feminine"]:
                # Para mujer, preferir archivos que contengan palabras de mujer
                es_mujer = any(kw in archivo_lower for kw in keywords_mujer_extra) or any(kw in archivo_lower for kw in keywords_mujer)
                if es_mujer:
                    candidatos_por_genero_inferido.append((nombre_sin_ext, archivo))
        
        if candidatos_por_genero_inferido:
            # Intentar fuzzy matching solo con candidatos que coincidan con el género inferido
            lista_candidatos = [n[0] for n in candidatos_por_genero_inferido]
            # Para el fuzzy matching con género inferido, incluir la marca en el nombre objetivo si está disponible
            # Esto ayuda a distinguir entre versiones como "1 Million" vs "Lady Million"
            nombre_objetivo_inferido = nombre_objetivo
            if marca and len(nombre_busqueda) > 1:
                # Solo incluir marca si el nombre tiene más de 1 carácter (evita falsos positivos)
                marca_limpia = re.sub(r"[^a-z0-9\s]", "", marca.lower())
                marca_limpia = re.sub(r"\s+", "_", marca_limpia.strip())
                # Solo agregar marca si no está ya presente en el nombre objetivo
                if marca_limpia not in nombre_objetivo_inferido:
                    nombre_objetivo_inferido = f"{nombre_objetivo_inferido}_{marca_limpia}"
            coincidencias = get_close_matches(nombre_objetivo_inferido, lista_candidatos, n=1, cutoff=0.8)
            if coincidencias:
                mejor_match = coincidencias[0]
                # Verificar que la coincidencia sea suficientemente específica
                palabras_clave = nombre_objetivo_inferido.replace('_', '').lower()
                match_limpio = mejor_match.replace('_', '').lower()
                
                if len(match_limpio) >= len(palabras_clave) * 0.7:
                    for nombre_sin_ext, archivo in candidatos_por_genero_inferido:
                        if nombre_sin_ext == mejor_match:
                            logger.info(f"Imagen encontrada (fuzzy con género inferido) para '{nombre}' ({genero}): {archivo.name}")
                            return archivo
                else:
                    logger.warning(f"Fuzzy match con género inferido demasiado débil para '{nombre}': '{mejor_match}' ({(len(match_limpio)/len(palabras_clave)*100):.0f}%)")
            # Si no hay fuzzy match, continuar con búsqueda global (no devolver primera de la lista)
    
    # 3. Si no se encontró en candidatos con género, buscar entre TODOS los archivos
    # (esto permite encontrar imágenes sin palabra clave de género)
    lista_nombres = [n[0] for n in nombres_archivo]
    coincidencias = get_close_matches(nombre_objetivo, lista_nombres, n=1, cutoff=0.7)
    
    if coincidencias:
        for nombre_sin_ext, archivo in nombres_archivo:
            if nombre_sin_ext == coincidencias[0]:
                logger.info(f"Imagen encontrada (búsqueda global) para '{nombre}' ({marca}): {archivo.name}")
                return archivo

    # 4. Búsqueda por subcadena en TODOS los archivos
    # Usar el nombre original (sin eliminar palabras de género) para la búsqueda
    nombre_busqueda = nombre.lower().replace(" ", "").replace("-", "").replace("'", "").lower()
    # Para nombres de 1 carácter, saltar a fuzzy matching (demasiado permisivo)
    if len(nombre_busqueda) > 1:
        # Para nombres de 2 caracteres, la subcadena debe coincidir como palabra completa
        requiere_palabra_completa = len(nombre_busqueda) == 2
        for nombre_sin_ext, archivo in nombres_archivo:
            archivo_nombre = nombre_sin_ext.replace("_", "").replace(" ", "").replace("-", "").replace("'", "").lower()
            if requiere_palabra_completa:
                # Buscar como palabra separada (al inicio/fin o rodeada de no-letras)
                patron = r'(^|[_\-.\s])' + re.escape(nombre_busqueda) + r'($|[_\-.\s])'
                if re.search(patron, archivo_nombre, re.IGNORECASE):
                    logger.info(f"Imagen encontrada por subcadena (global, palabra completa) para '{nombre}': {archivo.name}")
                    return archivo
            else:
                if nombre_busqueda in archivo_nombre or archivo_nombre in nombre_busqueda:
                    logger.info(f"Imagen encontrada por subcadena (global) para '{nombre}': {archivo.name}")
                    return archivo
    
    # 4b. Búsqueda por palabras individuales (más flexible)
    # Si no se encontró por subcadena exacta, buscar que la mayoría de palabras estén presentes
    palabras_nombre = set(nombre.lower().split())
    if len(palabras_nombre) >= 2:  # Solo si hay al menos 2 palabras
        mejor_match = None
        mejor_puntaje = 0
        for nombre_sin_ext, archivo in nombres_archivo:
            archivo_nombre_limpio = nombre_sin_ext.replace("_", " ").replace("-", " ").lower()
            palabras_archivo = set(archivo_nombre_limpio.split())
            # Calcular intersección
            palabras_comunes = palabras_nombre.intersection(palabras_archivo)
            puntaje = len(palabras_comunes) / len(palabras_nombre)
            if puntaje > 0.7 and puntaje > mejor_puntaje:  # 70% de las palabras deben coincidir
                mejor_match = (nombre_sin_ext, archivo, puntaje)
                mejor_puntaje = puntaje
        if mejor_match:
            logger.info(f"Imagen encontrada por palabras ({int(mejor_puntaje*100)}%) para '{nombre}': {mejor_match[1].name}")
            return mejor_match[1]

    # 5. Búsqueda por marca en TODOS los archivos (solo si también contiene el nombre)
    # Para nombres de 1 carácter, saltar a fuzzy matching (demasiado permisivo)
    if marca and len(nombre_busqueda) > 1:
        marca_busqueda = marca.lower().replace(" ", "").replace("&", "").replace(".", "")
        for nombre_sin_ext, archivo in nombres_archivo:
            archivo_nombre = nombre_sin_ext.replace("_", "", 1).replace(" ", "").lower()
            if marca_busqueda in archivo_nombre:
                # Verificar que el nombre del perfume también esté presente
                if len(nombre_busqueda) == 2:
                    # Para nombres de 2 caracteres, usar búsqueda de palabra completa
                    patron_nombre = r'(^|[_\-.\s])' + re.escape(nombre_busqueda) + r'($|[_\-.\s])'
                    if re.search(patron_nombre, archivo_nombre, re.IGNORECASE):
                        logger.info(f"Imagen encontrada por marca (global, con nombre) para '{nombre}' ({marca}): {archivo.name}")
                        return archivo
                else:
                    if nombre_busqueda in archivo_nombre:
                        logger.info(f"Imagen encontrada por marca (global, con nombre) para '{nombre}' ({marca}): {archivo.name}")
                        return archivo

    # 6. Búsqueda por género en nombres de archivo (para archivos sin keywords explícitas)
    # Si los archivos no tienen palabras clave de género, inferir género del archivo y filtrar
    # Se activa cuando: hay género especificado Y (candidatos_genero está vacío O no hubo filtrado efectivo)
    if genero_lower and (not candidatos_genero or len(candidatos_genero) == len(nombres_archivo)):
        # No hubo filtrado efectivo (todos pasaron) o no hay candidatos, intentar inferir género del archivo
        candidatos_por_genero_inferido = []
        keywords_hombre_extra = ["1_million", "invictus", "phantom", "eros", "le_male", "ultra_male", "bad_boy", "toy_boy", "stronger_with_you", "bottled", "bleu", "sauvage", "dior", "fahrenheit", "explorer", "legend", "polo_blue", "y_ysl", "dylan_blue", "acqua_di_gio", "212_vip_men", "club_de_nuit_intense_man", "asad", "aventus", "hawas", "terre_d'hermes", "valentino_uomo", "paco_rabanne"]
        keywords_mujer_extra = ["lady_million", "ariana_grande", "coco_mademoiselle", "j'adore", "la_vie_est_belle", "libre", "black_opium", "miss_dior", "fantasy", "bright_crystal", "can_can", "chanel_5", "cloud", "good_girl_blush", "idole", "light_blue_mujer", "scandal_mujer", "si", "sweet_like_candy", "thank_u_next", "yara", "212_vip_rose", "my_way", "olympea", "baccarat_rouge_540", "lost_cherry", "ombre_nomade", "santal_33", "tobacco_vanille", "hacivat", "khamrah"]
        
        for nombre_sin_ext, archivo in nombres_archivo:
            archivo_lower = nombre_sin_ext.lower()
            if genero_lower in ["hombre", "male", "men", "man", "masculino", "masculine"]:
                # Para hombre, preferir archivos que NO contengan palabras de mujer
                es_mujer = any(kw in archivo_lower for kw in keywords_mujer_extra) or any(kw in archivo_lower for kw in keywords_mujer)
                if not es_mujer:
                    candidatos_por_genero_inferido.append((nombre_sin_ext, archivo))
            elif genero_lower in ["mujer", "female", "women", "woman", "femenino", "feminine"]:
                # Para mujer, preferir archivos que contengan palabras de mujer
                es_mujer = any(kw in archivo_lower for kw in keywords_mujer_extra) or any(kw in archivo_lower for kw in keywords_mujer)
                if es_mujer:
                    candidatos_por_genero_inferido.append((nombre_sin_ext, archivo))
        
        if candidatos_por_genero_inferido:
            # Intentar fuzzy matching solo con candidatos que coincidan con el género inferido
            lista_candidatos = [n[0] for n in candidatos_por_genero_inferido]
            coincidencias = get_close_matches(nombre_objetivo, lista_candidatos, n=1, cutoff=0.8)
            if coincidencias:
                mejor_match = coincidencias[0]
                palabras_clave = nombre_objetivo.replace('_', '').lower()
                match_limpio = mejor_match.replace('_', '').lower()
                
                if len(match_limpio) >= len(palabras_clave) * 0.7:
                    for nombre_sin_ext, archivo in candidatos_por_genero_inferido:
                        if nombre_sin_ext == mejor_match:
                            logger.info(f"Imagen encontrada (fuzzy con género inferido) para '{nombre}' ({genero}): {archivo.name}")
                            return archivo
            # Si no hay fuzzy match válido, NO usar la primera de la lista; continuar con búsqueda global

    # 7. NO usar fallback de primera imagen de género - puede ser incorrecta
    # Mejor continuar con búsqueda global o usar default.jpg

    # 8. Fallback final: retornar default.jpg si existe
    default_img = dir_path / "default.jpg"
    if default_img.exists():
        logger.info(f"Usando imagen por defecto para '{nombre}' ({marca})")
        return default_img

    # 9. Último recurso: retornar la primera imagen disponible
    if archivos_disponibles:
        logger.warning(f"No se encontró coincidencia para '{nombre}'. Usando primera imagen disponible.")
        return archivos_disponibles[0]

    return None


class PDFCatalog(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(150)
            self.cell(0, 10, "Soul Extrait - Catalogo Premium", 0, 0, "R")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150)
        
        # Instagram link
        self.set_font("helvetica", "B", 8)
        self.set_text_color(*COLOR_ACENTO)
        self.cell(100, 10, "Siguenos en Instagram: @soul_extrait", 0, 0, "L", link="https://www.instagram.com/soul_extrait/")
        
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "R")

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(*COLOR_PRIMARIO)
        self.cell(0, 10, title, 0, 1, "L")
        self.set_draw_color(*COLOR_ACENTO)
        self.set_line_width(0.5)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(10)

# ─────────────────────────────────────────────
#   CLASE GENERADORA
# ─────────────────────────────────────────────

class GeneradorCatalog:
    def __init__(self, output_path: str = "output/catalogo_soul_extrait.pdf"):
        self.pdf = PDFCatalog()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(exist_ok=True)
        
        # Lista para el indice
        self.items_indice = []
        # Marcador global para volver al indice
        self.link_indice = self.pdf.add_link()

    def _pintar_fondo(self):
        """Pinta el fondo de la página con el color de la marca."""
        self.pdf.set_fill_color(*COLOR_FONDO)
        self.pdf.rect(0, 0, 210, 297, "F")

    def _pintar_marco(self):
        """Pinta un marco sutil en la página."""
        self.pdf.set_draw_color(*COLOR_PRIMARIO)
        self.pdf.set_line_width(0.4)
        self.pdf.rect(5, 5, 200, 287, "D")

    def _pintar_boton_volver(self):
        """Dibuja un enlace para volver al índice."""
        self.pdf.set_xy(10, 8)
        self.pdf.set_font("helvetica", "I", 7)
        self.pdf.set_text_color(160)
        self.pdf.cell(30, 5, "<< Volver al Indice", 0, 0, "L", link=self.link_indice)

    def crear_portada(self):
        """Crea la pagina de inicio del catalogo."""
        self.pdf.add_page()
        self._pintar_fondo()
        self._pintar_marco()
        
        # Logo grande y "opacado" en el fondo
        logo_path = BASE_DIR / "assets" / "logo.jpg"
        if not logo_path.exists():
            logo_path = BASE_DIR / "assets" / "logo.png"
            
        if logo_path.exists():
            try:
                # Verificar que el logo es una imagen válida antes de usarla
                from PIL import Image
                with Image.open(logo_path) as img:
                    img.verify()  # Verificar integridad
                # Logo de fondo (transparente) con context manager de fpdf2
                with self.pdf.local_context(fill_opacity=0.25):
                    # Centrado y grande
                    self.pdf.image(str(logo_path), x=30, y=70, w=150)
            except Exception as e:
                logger.warning(f"No se pudo cargar el logo de fondo: {e}")

        # Titulo Principal (Sobre el logo opacado)
        self.pdf.ln(60)
        self.pdf.set_font("helvetica", "B", 45)
        self.pdf.set_text_color(*COLOR_PRIMARIO)
        self.pdf.cell(0, 25, "SOUL EXTRAIT", 0, 1, "C")
        
        self.pdf.set_font("helvetica", "", 20)
        self.pdf.set_text_color(80)
        self.pdf.cell(0, 10, "Catálogo de Perfumería de Autor", 0, 1, "C")
        
        # Logo pequeño arriba si se quiere (opcional, lo dejamos el grande de fondo)
        # self.pdf.image(str(logo_path), x=90, y=20, w=30)

        self.pdf.set_y(240)
        self.pdf.set_font("helvetica", "I", 14)
        self.pdf.set_text_color(120)
        self.pdf.multi_cell(0, 8, "Una selección de las mejores fragancias del mundo.", 0, "C")
        
        self.pdf.set_y(self.pdf.get_y() + 5) # Añadir un pequeño margen después del multi_cell
        self.pdf.set_font("helvetica", "B", 14)
        self.pdf.set_text_color(*COLOR_ACENTO)
        
        # Fecha dinámica: MES - AÑO EDITION
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                 "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        ahora = datetime.now()
        fecha_edicion = f"{meses[ahora.month-1]} - {ahora.year} EDITION"
        self.pdf.cell(0, 10, fecha_edicion, 0, 1, "C")

    def crear_indice(self, perfumes: list):
        """Crea la pagina de indice interactivo con diseño tipográfico por colecciones."""
        self.pdf.add_page()
        # Vincular el marcador global a esta página (la del índice)
        self.pdf.set_link(self.link_indice, y=0, page=-1)
        
        self._pintar_fondo()
        self._pintar_marco()
        
        # Título principal del índice
        self.pdf.set_font("helvetica", "B", 24)
        self.pdf.set_text_color(*COLOR_PRIMARIO)
        self.pdf.cell(0, 15, "ÍNDICE DE FRAGANCIAS", 0, 1, "C")
        
        # Línea decorativa
        self.pdf.set_draw_color(*COLOR_ACENTO)
        self.pdf.set_line_width(0.8)
        self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
        self.pdf.ln(15)
        
        # Crear links para cada perfume (en orden original) para mantener compatibilidad con main.py
        self.items_indice = []  # Resetear lista de links
        for perfume in perfumes:
            link = self.pdf.add_link()
            self.items_indice.append(link)
        
        # Diccionario para lookup rápido: nombre -> link
        links_por_nombre = {
            perfume["nombre"]["completo"]: link
            for perfume, link in zip(perfumes, self.items_indice)
        }
        
        # Definir las 3 colecciones
        colecciones = [
            "Frescura y Vitalidad",
            "Noche y Seducción",
            "Elegancia e Intensidad"
        ]
        
        # Agrupar perfumes por colección y género
        perfumes_por_coleccion = {}
        for coleccion in colecciones:
            perfumes_por_coleccion[coleccion] = {"Hombre": [], "Mujer": [], "Unisex": []}
        
        for perfume in perfumes:
            colecciones_perfume = perfume.get("colecciones", [])
            genero = perfume.get("genero", "Unisex")
            # Normalizar género: capitalizar primera letra (hombre → Hombre, mujer → Mujer)
            genero_norm = genero.capitalize() if genero else "Unisex"
            
            # Si no tiene colecciones asignadas, asignar a "Elegancia e Intensidad" por defecto
            if not colecciones_perfume:
                colecciones_perfume = ["Elegancia e Intensidad"]
            
            # Agregar el perfume a cada colección que corresponda
            for coleccion in colecciones_perfume:
                if coleccion in perfumes_por_coleccion:
                    perfumes_por_coleccion[coleccion][genero_norm].append(perfume)
        
        # Para cada colección, dibujar sección con dos columnas (Hombres | Mujeres)
        ancho_columna = 95
        
        for coleccion_nombre, generos in perfumes_por_coleccion.items():
            # Verificar si hay perfumes en esta colección
            total_en_coleccion = sum(len(perfumes) for perfumes in generos.values())
            if total_en_coleccion == 0:
                continue
            
            # Título de la colección
            # Verificar si hay espacio suficiente para el título + encabezados + al menos 1 fila
            # Si no, agregar nueva página
            espacio_necesario = 10 + 2 + 6 + 3 + 5 + 10  # título + ln + encabezados + ln + línea + ln
            if self.pdf.get_y() + espacio_necesario > 270:  # Margen inferior (A4 = 297mm, margen ~27mm)
                self.pdf.add_page()
                self._pintar_fondo()
                self._pintar_marco()
            
            self.pdf.set_font("helvetica", "B", 16)
            self.pdf.set_text_color(*COLOR_PRIMARIO)
            self.pdf.cell(0, 10, coleccion_nombre.upper(), 0, 1, "L")
            self.pdf.ln(2)
            
            # Encabezados de columnas
            self.pdf.set_font("helvetica", "B", 11)
            self.pdf.set_text_color(100)
            self.pdf.cell(ancho_columna, 6, "HOMBRES", 0, 0, "L")
            self.pdf.cell(ancho_columna, 6, "MUJERES", 0, 1, "R")
            self.pdf.ln(3)
            
            # Línea sutil debajo de los encabezados
            self.pdf.set_draw_color(220)
            self.pdf.set_line_width(0.3)
            self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
            self.pdf.ln(5)
            
            # Preparar listas
            hombres_list = generos["Hombre"]
            mujeres_list = generos["Mujer"]
            max_rows = max(len(hombres_list), len(mujeres_list))
            
            # Dibujar filas
            for i in range(max_rows):
                y_start = self.pdf.get_y()
                
                # Verificar si hay espacio para esta fila (12mm por fila)
                if y_start + 12 > 270:
                    self.pdf.add_page()
                    self._pintar_fondo()
                    self._pintar_marco()
                    # Redibujar encabezados de colección en nueva página
                    self.pdf.set_font("helvetica", "B", 16)
                    self.pdf.set_text_color(*COLOR_PRIMARIO)
                    self.pdf.cell(0, 10, coleccion_nombre.upper(), 0, 1, "L")
                    self.pdf.ln(2)
                    self.pdf.set_font("helvetica", "B", 11)
                    self.pdf.set_text_color(100)
                    self.pdf.cell(ancho_columna, 6, "HOMBRES", 0, 0, "L")
                    self.pdf.cell(ancho_columna, 6, "MUJERES", 0, 1, "R")
                    self.pdf.ln(3)
                    self.pdf.set_draw_color(220)
                    self.pdf.set_line_width(0.3)
                    self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
                    self.pdf.ln(5)
                    y_start = self.pdf.get_y()
                
                # Guardar posición Y inicial para esta fila
                self.pdf.set_y(y_start)
                
                # Guardar Y inicial para esta fila
                y_fila = y_start
                
                # Columna izquierda - Hombres
                if i < len(hombres_list):
                    perfume = hombres_list[i]
                    nombre = perfume["nombre"]["completo"]
                    familia = perfume.get("familia_olfativa", "")
                    link = links_por_nombre.get(nombre)
                    
                    # Posicionar en columna izquierda
                    self.pdf.set_xy(10, y_fila)
                    self.pdf.set_font("helvetica", "", 10)
                    self.pdf.set_text_color(*COLOR_PRIMARIO)
                    self.pdf.cell(ancho_columna, 6, nombre, 0, 1, "L", link=link)
                    
                    # Familia olfativa debajo (si existe)
                    if familia:
                        self.pdf.set_xy(10, self.pdf.get_y())
                        self.pdf.set_font("helvetica", "I", 8)
                        self.pdf.set_text_color(120)
                        self.pdf.cell(ancho_columna, 4, familia, 0, 1, "L")
                    else:
                        # Espaciador para mantener alineación
                        self.pdf.set_xy(10, self.pdf.get_y())
                        self.pdf.cell(ancho_columna, 4, "", 0, 1, "L")
                
                # Columna derecha - Mujeres (resetear Y a y_fila)
                if i < len(mujeres_list):
                    perfume = mujeres_list[i]
                    nombre = perfume["nombre"]["completo"]
                    familia = perfume.get("familia_olfativa", "")
                    link = links_por_nombre.get(nombre)
                    
                    # Resetear Y a la posición inicial de la fila
                    self.pdf.set_xy(10 + ancho_columna, y_fila)
                    self.pdf.set_font("helvetica", "", 10)
                    self.pdf.set_text_color(*COLOR_PRIMARIO)
                    self.pdf.cell(ancho_columna, 6, nombre, 0, 1, "R", link=link)
                    
                    # Familia olfativa debajo
                    if familia:
                        self.pdf.set_xy(10 + ancho_columna, self.pdf.get_y())
                        self.pdf.set_font("helvetica", "I", 8)
                        self.pdf.set_text_color(120)
                        self.pdf.cell(ancho_columna, 4, familia, 0, 1, "R")
                    else:
                        # Espaciador para mantener alineación
                        self.pdf.set_xy(10 + ancho_columna, self.pdf.get_y())
                        self.pdf.cell(ancho_columna, 4, "", 0, 1, "R")
                
                # Avance vertical después de dibujar ambas columnas
                self.pdf.ln(2)
            
            self.pdf.ln(6)
            
            # Línea separadora entre colecciones
            self.pdf.set_draw_color(230)
            self.pdf.set_line_width(0.5)
            self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
            self.pdf.ln(10)

    def _optimizar_imagen(self, image_path: Path) -> str:
        """Redimensiona la imagen para que quepa en el PDF sin pesar demasiado."""
        try:
            temp_path = image_path.parent / f"temp_{image_path.name}"
            with Image.open(image_path) as img:
                img.thumbnail((400, 400))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(temp_path, "JPEG", quality=85)
            return str(temp_path)
        except Exception as e:
            logger.error(f"Error optimizando imagen {image_path}: {e}")
            return str(image_path)

    def agregar_perfume(self, datos: dict, index_link=None):
        """Agrega una pagina de ficha tecnica para un perfume."""
        self.pdf.add_page()
        self._pintar_fondo()
        self._pintar_marco()
        self._pintar_boton_volver()
        
        # Si tenemos un link del indice, lo vinculamos a esta pagina
        if index_link:
            self.pdf.set_link(index_link, y=0, page=-1)

        nombre = datos["nombre"]
        
        # --- Cabecera ---
        self.pdf.set_y(25) # Más margen superior
        self.pdf.set_font("helvetica", "B", 26)
        self.pdf.set_text_color(*COLOR_PRIMARIO)
        self.pdf.cell(0, 15, nombre["titulo"].upper(), 0, 1, "C")
        
        # Línea de separación debajo del título
        self.pdf.set_draw_color(*COLOR_ACENTO)
        self.pdf.set_line_width(0.7) # Más gruesa
        self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
        self.pdf.ln(8)

        if nombre["subtitulo"]:
            self.pdf.set_font("helvetica", "I", 16)
            self.pdf.set_text_color(80)
            self.pdf.cell(0, 10, nombre["subtitulo"], 0, 1, "C")
        
        # Género
        genero = datos.get("genero", "Unisex")
        self.pdf.set_font("helvetica", "B", 10)
        self.pdf.set_text_color(120)
        self.pdf.cell(0, 8, f"LINEA: {genero.upper()}", 0, 1, "C")
        
        self.pdf.ln(5)
        
        # --- Imagen y Datos Base ---
        y_start = self.pdf.get_y()
        
        # Imagen (Lado izquierdo)
        img_path = datos.get("imagen_path")
        imagen_cargada = False
        if img_path and Path(img_path).exists():
            try:
                # Optimizar y limitar tamaño para que NO pise la pirámide
                with Image.open(img_path) as img:
                    orig_w, orig_h = img.size
                    # Box de 70x70 mm
                    # Calcular escala proporcional
                    ratio = min(70/orig_w, 70/orig_h)
                    new_w = orig_w * ratio
                    
                self.pdf.image(str(img_path), x=10, y=y_start, w=70, h=70, keep_aspect_ratio=True)
                imagen_cargada = True
            except Exception as e:
                logger.warning(f"No se pudo cargar imagen del perfume {nombre['titulo']}: {e}")
        
        if not imagen_cargada:
            self.pdf.rect(10, y_start, 70, 70, "D")
            self.pdf.set_xy(10, y_start + 30)
            self.pdf.set_font("helvetica", "I", 10)
            self.pdf.cell(70, 10, "Imagen no disponible", 0, 0, "C")

        # Info Derecha (Especificaciones)
        self.pdf.set_xy(85, y_start)
        self.pdf.set_font("helvetica", "B", 12)
        self.pdf.set_text_color(*COLOR_PRIMARIO)
        self.pdf.cell(0, 10, "ESPECIFICACIONES", 0, 1, "L")
        
        self.pdf.set_font("helvetica", "", 10)
        self.pdf.set_text_color(50)
        
        x_info = 85
        self.pdf.set_x(x_info)
        self.pdf.set_font("helvetica", "B", 10)
        self.pdf.cell(35, 8, "Presentacion:", 0, 0)
        self.pdf.set_font("helvetica", "", 10)
        self.pdf.cell(0, 8, f"{datos.get('ml', '--')} ml", 0, 1)

        self.pdf.ln(5)
        
        # Ocasiones de Uso
        ocasiones = datos.get("ocasiones", [])
        if ocasiones:
            self.pdf.set_x(x_info)
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.set_text_color(*COLOR_PRIMARIO)
            self.pdf.cell(0, 8, "OCASIONES:", 0, 1, "L")
            self.pdf.set_x(x_info)
            self.pdf.set_font("helvetica", "", 9)
            self.pdf.set_text_color(80)
            self.pdf.multi_cell(0, 5, ", ".join(ocasiones), 0, "L")
            self.pdf.ln(3)
        
        # --- Clima y Estaciones ---
        self.pdf.set_x(x_info)
        self.pdf.set_font("helvetica", "B", 12)
        self.pdf.set_text_color(*COLOR_PRIMARIO)
        self.pdf.cell(0, 10, "IDEAL PARA", 0, 1, "L")
        
        estaciones = datos.get("estaciones", [])
        if not estaciones:
            self.pdf.set_x(x_info)
            self.pdf.set_font("helvetica", "I", 10)
            self.pdf.cell(0, 8, "Datos de clima no disponibles.", 0, 1)
        else:
            for est in estaciones:
                self.pdf.set_x(x_info)
                self.pdf.set_font("helvetica", "", 10)
                self.pdf.cell(40, 8, f"{est['nombre']}:", 0, 0)
                self.pdf.set_text_color(*COLOR_ACENTO)
                self.pdf.cell(0, 8, f"{est['porcentaje']}%", 0, 1)
                self.pdf.set_text_color(50)

        # Descripción del Perfume (Abajo del bloque de imagen e info)
        self.pdf.set_y(max(self.pdf.get_y(), y_start + 72))
        self.pdf.set_font("helvetica", "I", 10)
        self.pdf.set_text_color(60)
        descripcion = datos.get("descripcion", "")
        if descripcion:
            self.pdf.multi_cell(0, 6, f'"{descripcion}"', 0, "C")
            self.pdf.ln(5)

        # --- Piramide Olfativa ---
        self.pdf.ln(5)
        self.pdf.set_font("helvetica", "B", 14)
        self.pdf.set_text_color(*COLOR_PRIMARIO)
        self.pdf.cell(0, 10, "PIRAMIDE OLFATIVA", 0, 1, "C")
        
        # Línea decorativa
        self.pdf.set_draw_color(*COLOR_ACENTO)
        self.pdf.set_line_width(0.6)
        x_line = 60
        self.pdf.line(x_line, self.pdf.get_y(), 210 - x_line, self.pdf.get_y())
        self.pdf.ln(8)

        notas = datos.get("notas", {})
        niveles = [
            ("NOTAS DE SALIDA", notas.get("salida", []), "(Lo que percibes al inicio)"),
            ("NOTAS DE CORAZON", notas.get("corazon", []), "(Luego de unos minutos)"),
            ("NOTAS DE FONDO", notas.get("fondo", []), "(La fijacion final)"),
        ]

        for titulo_nota, lista, desc in niveles:
            if not lista: continue
            
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.set_text_color(*COLOR_PRIMARIO)
            self.pdf.cell(50, 8, titulo_nota, 0, 0)
            
            self.pdf.set_font("helvetica", "I", 8)
            self.pdf.set_text_color(150)
            self.pdf.cell(0, 8, desc, 0, 1)
            
            self.pdf.set_font("helvetica", "", 10)
            self.pdf.set_text_color(50)
            self.pdf.multi_cell(0, 6, " * ".join(lista), 0, "L")
            self.pdf.ln(3)

        # --- Boton de Accion (WhatsApp) ---
        # Posicionamiento fijo al fondo para evitar solapamientos
        self.pdf.set_y(-30) 
        self.pdf.set_fill_color(*COLOR_PRIMARIO)
        self.pdf.rect(10, self.pdf.get_y(), 190, 15, "F")
        
        # Crear link de WhatsApp robusto
        clean_num = "".join(filter(str.isdigit, WHATSAPP_NUM))
        msg = f"{WHATSAPP_MSG}: {nombre['completo']}"
        encoded_msg = urllib.parse.quote(msg)
        wa_link = f"https://wa.me/{clean_num}?text={encoded_msg}"
        
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("helvetica", "B", 11)
        self.pdf.cell(0, 15, "CONSULTAR DISPONIBILIDAD VIA WHATSAPP", 0, 0, "C", link=wa_link)

    def guardar(self):
        """Genera el archivo final y limpia temporales."""
        self.pdf.output(str(self.output_path))
        logger.success(f"Catalogo generado con exito en: {self.output_path}")
        
        # Limpiar imagenes temporales (opcional)
        for f in self.output_path.parent.glob("temp_*"):
            try: os.remove(f)
            except: pass

# ─────────────────────────────────────────────
#   PRUEBA STAND-ALONE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Mock de datos para probar el diseño tipográfico por colecciones
    fake_perfumes = [
        {
            "nombre": {"titulo": "Bleu de Chanel", "subtitulo": "Chanel", "completo": "Bleu de Chanel - Chanel"},
            "ml": "100",
            "genero": "Hombre",
            "familia_olfativa": "Cítrico - Madera",
            "estaciones": [
                {"nombre": "Primavera", "porcentaje": 80},
                {"nombre": "Verano", "porcentaje": 70}
            ],
            "notas": {
                "salida": ["Pomelo", "Limón", "Menta"],
                "corazon": ["Jengibre", "Pimienta", "Iso E Super"],
                "fondo": ["Incienso", "Sándalo", "Pachulí"]
            },
            "ocasiones": ["Día", "Oficina", "Casual"],
            "descripcion_corta": "Una fragancia elegante y versátil con notas cítricas y amaderadas.",
            "imagen_path": None
        },
        {
            "nombre": {"titulo": "Light Blue", "subtitulo": "Dolce & Gabbana", "completo": "Light Blue - Dolce & Gabbana"},
            "ml": "100",
            "genero": "Mujer",
            "familia_olfativa": "Cítrico - Floral",
            "estaciones": [
                {"nombre": "Verano", "porcentaje": 95},
                {"nombre": "Primavera", "porcentaje": 85}
            ],
            "notas": {
                "salida": ["Cedro", "Manzana", "Limón"],
                "corazon": ["Jazmín", "Rosa", "Azucena"],
                "fondo": ["Vainilla", "Musk", "Amber"]
            },
            "ocasiones": ["Verano", "Día", "Playa"],
            "descripcion_corta": "Frescura mediterránea en cada nota, ideal para el verano.",
            "imagen_path": None
        },
        {
            "nombre": {"titulo": "La Nuit de L'Homme", "subtitulo": "Yves Saint Laurent", "completo": "La Nuit de L'Homme - YSL"},
            "ml": "60",
            "genero": "Hombre",
            "familia_olfativa": "Especiado - Aromático",
            "estaciones": [
                {"nombre": "Invierno", "porcentaje": 75},
                {"nombre": "Noche", "porcentaje": 90}
            ],
            "notas": {
                "salida": ["Cardamomo", "Bergamota", "Lavanda"],
                "corazon": ["Café", "Cedro", "Pimienta"],
                "fondo": ["Vainilla", "Pachulí", "Musk"]
            },
            "ocasiones": ["Noche", "Invierno", "Cena"],
            "descripcion_corta": "Misteriosa y seductora, perfecta para las noches de invierno.",
            "imagen_path": None,
            "colecciones": ["Noche y Seducción"]
        },
        {
            "nombre": {"titulo": "Sauvage", "subtitulo": "Dior", "completo": "Sauvage - Dior"},
            "ml": "100",
            "genero": "Hombre",
            "familia_olfativa": "Cítrico - Aromático",
            "estaciones": [
                {"nombre": "Verano", "porcentaje": 85},
                {"nombre": "Primavera", "porcentaje": 80}
            ],
            "notas": {
                "salida": ["Bergamota", "Pimienta"],
                "corazon": ["Lavanda", "Pimienta", "Notas afrutadas"],
                "fondo": ["Ambroxan", "Cedro", "Musk"]
            },
            "ocasiones": ["Día", "Oficina", "Verano"],
            "descripcion_corta": "Una fragancia fresca y potente con carácter inconfundible.",
            "imagen_path": None,
            "colecciones": ["Sensación de Frescura", "Fuerza y Elegancia"]
        },
        {
            "nombre": {"titulo": "Black Opium", "subtitulo": "Yves Saint Laurent", "completo": "Black Opium - YSL"},
            "ml": "90",
            "genero": "Mujer",
            "familia_olfativa": "Oriental - Vainilla",
            "estaciones": [
                {"nombre": "Invierno", "porcentaje": 85},
                {"nombre": "Noche", "porcentaje": 95}
            ],
            "notas": {
                "salida": ["Pera", "Naranja", "Café"],
                "corazon": ["Jazmín", "Rosa", "Flor de Azahar"],
                "fondo": ["Vainilla", "Pachulí", "Musk"]
            },
            "ocasiones": ["Noche", "Invierno", "Romántico"],
            "descripcion_corta": "Exótica y adictiva, una mezcla de café y vainilla irresistible.",
            "imagen_path": None,
            "colecciones": ["Noche y Seducción"]
        },
        {
            "nombre": {"titulo": "Acqua di Gio", "subtitulo": "Giorgio Armani", "completo": "Acqua di Gio - Giorgio Armani"},
            "ml": "100",
            "genero": "Hombre",
            "familia_olfativa": "Cítrico - Acuático",
            "estaciones": [
                {"nombre": "Verano", "porcentaje": 95},
                {"nombre": "Primavera", "porcentaje": 85}
            ],
            "notas": {
                "salida": ["Limón", "Neroli", "Jazmín de Agua"],
                "corazon": ["Romero", "Hiedra", "Pimienta"],
                "fondo": ["Pachulí", "Musk", "Sándalo"]
            },
            "ocasiones": ["Verano", "Día", "Playa"],
            "descripcion_corta": "La esencia del mar y la frescura mediterránea.",
            "imagen_path": None,
            "colecciones": ["Sensación de Frescura"]
        }
    ]

    gen = GeneradorCatalog("output/test_diseno.pdf")
    gen.crear_portada()
    gen.crear_indice(fake_perfumes)
    
    # Agregar fichas técnicas para cada perfume
    for i, datos in enumerate(fake_perfumes):
        gen.agregar_perfume(datos, gen.items_indice[i])
    
    gen.guardar()
    print("PDF de prueba creado con diseño tipográfico. Revisa 'output/test_diseno.pdf'")
