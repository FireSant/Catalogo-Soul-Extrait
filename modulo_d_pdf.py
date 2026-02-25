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
import urllib.parse
from datetime import datetime
from pathlib import Path

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
        self.pdf.multi_cell(0, 8, "Expertos en capturar memorias en frascos.\nUna selección curada de las mejores fragancias del mundo.", 0, "C")
        
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
        """Crea la pagina de indice interactivo."""
        self.pdf.add_page()
        # Vincular el marcador global a esta página (la del índice)
        self.pdf.set_link(self.link_indice, y=0, page=-1)
        
        self._pintar_fondo()
        self._pintar_marco()
        self.pdf.chapter_title("Indice de Fragancias")
        self.pdf.set_font("helvetica", "", 12)
        self.pdf.set_text_color(*COLOR_TEXTO)

        # Agrupar por marca si es posible, o simple lista
        for i, p in enumerate(perfumes, 1):
            nombre_label = p["nombre"]["completo"]
            # Guardamos el link para despues
            link = self.pdf.add_link()
            self.items_indice.append(link)
            
            self.pdf.set_text_color(*COLOR_PRIMARIO)
            self.pdf.cell(0, 10, f"{i}. {nombre_label}", 0, 1, "L", link=link)
            self.pdf.set_draw_color(240)
            self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())

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
        
        specs = [
            ("Presentacion:", f"{datos.get('ml', '--')} ml"),
            ("Precio Estimado:", f"${datos.get('precio', 'Consultar')}")
        ]
        
        x_info = 85
        for label, val in specs:
            self.pdf.set_x(x_info)
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(35, 8, label, 0, 0)
            self.pdf.set_font("helvetica", "", 10)
            self.pdf.cell(0, 8, val, 0, 1)

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
    # Mock de datos para probar el diseno
    fake_data = {
        "nombre": {"titulo": "Oud Wood", "subtitulo": "Tom Ford", "completo": "Oud Wood - Tom Ford"},
        "ml": "100",
        "precio": "250.000",
        "estaciones": [
            {"nombre": "Invierno", "icono": "❄️", "porcentaje": 80},
            {"nombre": "Noche", "icono": "🌙", "porcentaje": 90}
        ],
        "notas": {
            "salida": ["Palo de Rosa", "Cardamomo", "Pimienta China"],
            "corazon": ["Oud", "Sandalo", "Vetiver"],
            "fondo": ["Vainilla", "Ámbar", "Haba Tonka"]
        },
        "imagen_path": None
    }

    gen = GeneradorCatalog("output/test_diseno.pdf")
    gen.crear_portada()
    gen.crear_indice([fake_data])
    gen.agregar_perfume(fake_data, gen.items_indice[0])
    gen.guardar()
    print("PDF de prueba creado. Revisa 'output/test_diseno.pdf'")
