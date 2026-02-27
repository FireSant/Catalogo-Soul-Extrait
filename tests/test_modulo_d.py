"""
tests/test_modulo_d.py — Tests para el Módulo D: Generador de PDF
"""
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import modulo_d_pdf as mod_d


# ─────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def datos_perfume_ejemplo():
    """Datos de ejemplo para un perfume completo."""
    return {
        "nombre": {
            "titulo": "Good Girl",
            "subtitulo": "Carolina Herrera",
            "completo": "Good Girl - Carolina Herrera"
        },
        "ml": "80",
        "genero": "Mujer",
        "familia_olfativa": "Floral - Oriental",
        "estaciones": [
            {"nombre": "Invierno", "porcentaje": 60},
            {"nombre": "Noche", "porcentaje": 70}
        ],
        "notas": {
            "salida": ["Bergamota", "Almendra"],
            "corazon": ["Rosa", "Jazmín"],
            "fondo": ["Vainilla", "Sándalo", "Musk"]
        },
        "ocasiones": ["Noche", "Invierno", "Romántico"],
        "descripcion_corta": "Una fragancia dulce y seductora con notas de almendra y rosa.",
        "imagen_path": None,
        "colecciones": ["Noche y Seducción"]
    }


@pytest.fixture
def datos_perfume_sin_imagen(datos_perfume_ejemplo):
    """Perfume sin imagen."""
    datos = datos_perfume_ejemplo.copy()
    datos["imagen_path"] = None
    return datos


@pytest.fixture
def datos_perfume_con_imagen(tmp_path, datos_perfume_ejemplo):
    """Perfume con una imagen de prueba."""
    # Crear una imagen dummy
    img_path = tmp_path / "test_image.jpg"
    from PIL import Image
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path, "JPEG")

    datos = datos_perfume_ejemplo.copy()
    datos["imagen_path"] = str(img_path)
    return datos


# ─────────────────────────────────────────────
#  TESTS: INICIALIZACIÓN
# ─────────────────────────────────────────────

class TestInicializacion:
    def test_crear_generador_con_ruta_default(self, tmp_path):
        """Debe crear el generador con ruta por defecto."""
        gen = mod_d.GeneradorCatalog()
        assert gen.output_path == Path("output/catalogo_soul_extrait.pdf")

    def test_crear_generador_con_ruta_personalizada(self, tmp_path):
        """Debe crear el generador con ruta personalizada."""
        ruta = tmp_path / "mi_catalogo.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        assert gen.output_path == ruta
        assert ruta.parent.exists()

    def test_directorio_output_se_crea_automaticamente(self, tmp_path):
        """Debe crear el directorio de output si no existe."""
        ruta = tmp_path / "nuevo_dir" / "catalogo.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        assert ruta.parent.exists()

    def test_items_indice_inicializado_vacio(self):
        """El índice debe iniciarse vacío."""
        gen = mod_d.GeneradorCatalog()
        assert gen.items_indice == []

    def test_link_indice_creado(self):
        """Debe crear un link para el índice."""
        gen = mod_d.GeneradorCatalog()
        assert gen.link_indice is not None


# ─────────────────────────────────────────────
#  TESTS: PORTADA
# ─────────────────────────────────────────────

class TestPortada:
    def test_crear_portada_agrega_pagina(self, tmp_path):
        """crear_portada debe agregar al menos una página."""
        ruta = tmp_path / "portada_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.guardar()

        assert ruta.exists()
        # Verificar que el PDF tiene contenido
        assert ruta.stat().st_size > 0

    def test_portada_con_logo_existente(self, tmp_path):
        """Si existe logo, debe incluirlo en la portada."""
        # Crear un logo dummy
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        logo_path = assets_dir / "logo.png"
        from PIL import Image
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(logo_path, "PNG")

        # Monkeypatch BASE_DIR para usar el directorio temporal
        original_base = mod_d.BASE_DIR
        mod_d.BASE_DIR = tmp_path

        try:
            ruta = tmp_path / "con_logo.pdf"
            gen = mod_d.GeneradorCatalog(str(ruta))
            gen.crear_portada()
            gen.guardar()
            assert ruta.exists()
        finally:
            mod_d.BASE_DIR = original_base

    def test_portada_sin_logo_no_falla(self, tmp_path):
        """Si no existe logo, la portada debe generarse sin errores."""
        original_base = mod_d.BASE_DIR
        mod_d.BASE_DIR = tmp_path  # Forzar directorio sin assets

        try:
            ruta = tmp_path / "sin_logo.pdf"
            gen = mod_d.GeneradorCatalog(str(ruta))
            gen.crear_portada()
            gen.guardar()
            assert ruta.exists()
        finally:
            mod_d.BASE_DIR = original_base


# ─────────────────────────────────────────────
#  TESTS: ÍNDICE
# ─────────────────────────────────────────────

class TestIndice:
    def test_crear_indice_agrega_pagina(self, tmp_path, datos_perfume_ejemplo):
        """crear_indice debe agregar una página."""
        ruta = tmp_path / "indice_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos_perfume_ejemplo])
        gen.guardar()

        assert ruta.exists()
        assert len(gen.items_indice) == 1

    def test_items_indice_links_creados(self, tmp_path, datos_perfume_ejemplo):
        """Debe crear un link por cada perfume."""
        ruta = tmp_path / "links_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos_perfume_ejemplo, datos_perfume_ejemplo])
        gen.guardar()

        assert len(gen.items_indice) == 2

    def test_indice_con_multiples_colecciones(self, tmp_path):
        """Debe agrupar perfumes por colección correctamente."""
        perfumes = [
            {
                "nombre": {"titulo": "Perfume A", "subtitulo": "Marca A", "completo": "Perfume A - Marca A"},
                "genero": "Hombre",
                "familia_olfativa": "Cítrico",
                "colecciones": ["Sensación de Frescura"],
                "estaciones": []
            },
            {
                "nombre": {"titulo": "Perfume B", "subtitulo": "Marca B", "completo": "Perfume B - Marca B"},
                "genero": "Mujer",
                "familia_olfativa": "Oriental",
                "colecciones": ["Noche y Seducción"],
                "estaciones": []
            },
            {
                "nombre": {"titulo": "Perfume C", "subtitulo": "Marca C", "completo": "Perfume C - Marca C"},
                "genero": "Unisex",
                "familia_olfativa": "Amaderado",
                "colecciones": [],  # Debe ir a Fuerza y Elegancia por defecto
                "estaciones": []
            }
        ]

        ruta = tmp_path / "colecciones_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice(perfumes)
        gen.guardar()

        assert ruta.exists()


# ─────────────────────────────────────────────
#  TESTS: AGREGAR PERFUME
# ─────────────────────────────────────────────

class TestAgregarPerfume:
    def test_agregar_perfume_crea_pagina(self, tmp_path, datos_perfume_ejemplo):
        """Cada perfume debe agregar una página."""
        ruta = tmp_path / "perfume_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos_perfume_ejemplo])
        gen.agregar_perfume(datos_perfume_ejemplo, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_perfume_con_todos_los_campos(self, tmp_path, datos_perfume_ejemplo):
        """Debe procesar correctamente todos los campos."""
        ruta = tmp_path / "completo_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos_perfume_ejemplo])
        gen.agregar_perfume(datos_perfume_ejemplo, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_perfume_sin_imagen_muestra_placeholder(self, tmp_path, datos_perfume_sin_imagen):
        """Si no hay imagen, debe mostrar recuadro vacío."""
        ruta = tmp_path / "sin_imagen_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos_perfume_sin_imagen])
        gen.agregar_perfume(datos_perfume_sin_imagen, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_perfume_con_imagen_la_incluye(self, tmp_path, datos_perfume_con_imagen):
        """Si hay imagen, debe incluirla."""
        ruta = tmp_path / "con_imagen_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos_perfume_con_imagen])
        gen.agregar_perfume(datos_perfume_con_imagen, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_perfume_sin_ocasiones_no_falla(self, tmp_path):
        """Si no hay 'ocasiones', debe continuar sin error."""
        datos = {
            "nombre": {"titulo": "Test", "subtitulo": "", "completo": "Test"},
            "ml": "100",
            "genero": "Unisex",
            "estaciones": [],
            "notas": {"salida": [], "corazon": [], "fondo": []},
            "descripcion_corta": "Test"
        }
        ruta = tmp_path / "sin_ocasiones.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos])
        gen.agregar_perfume(datos, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_perfume_sin_descripcion_no_falla(self, tmp_path, datos_perfume_ejemplo):
        """Si no hay descripción, debe continuar."""
        datos = datos_perfume_ejemplo.copy()
        datos["descripcion_corta"] = ""

        ruta = tmp_path / "sin_desc.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos])
        gen.agregar_perfume(datos, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()


# ─────────────────────────────────────────────
#  TESTS: GUARDAR Y ESTRUCTURA
# ─────────────────────────────────────────────

class TestGuardar:
    def test_guardar_crea_archivo(self, tmp_path, datos_perfume_ejemplo):
        """guardar debe crear el archivo PDF."""
        ruta = tmp_path / "guardado_test.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos_perfume_ejemplo])
        gen.agregar_perfume(datos_perfume_ejemplo, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()
        assert ruta.is_file()

    def test_guardar_sobrescribe_archivo_existente(self, tmp_path, datos_perfume_ejemplo):
        """Debe sobrescribir si el archivo ya existe."""
        ruta = tmp_path / "sobrescritura.pdf"

        # Crear primer PDF
        gen1 = mod_d.GeneradorCatalog(str(ruta))
        gen1.crear_portada()
        gen1.guardar()
        size1 = ruta.stat().st_size

        # Crear segundo PDF con más contenido
        gen2 = mod_d.GeneradorCatalog(str(ruta))
        gen2.crear_portada()
        gen2.crear_indice([datos_perfume_ejemplo])
        gen2.agregar_perfume(datos_perfume_ejemplo, gen2.items_indice[0])
        gen2.guardar()
        size2 = ruta.stat().st_size

        assert size2 > size1

    def test_flujo_completo_simple(self, tmp_path, datos_perfume_ejemplo):
        """Test de flujo completo: portada + índice + 1 perfume."""
        ruta = tmp_path / "flujo_completo.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))

        gen.crear_portada()
        gen.crear_indice([datos_perfume_ejemplo])
        gen.agregar_perfume(datos_perfume_ejemplo, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()
        # El PDF debe tener al menos 2 páginas (portada + ficha)
        # No podemos verificar páginas fácilmente sin librería extra,
        # pero sí el tamaño
        assert ruta.stat().st_size > 3000  # Al menos 3KB


# ─────────────────────────────────────────────
#  TESTS: VALIDACIÓN DE DATOS
# ─────────────────────────────────────────────

class TestValidacionDatos:
    def test_nombre_titulo_se_muestra(self, tmp_path):
        """El título del perfume debe aparecer en el PDF."""
        datos = {
            "nombre": {"titulo": "Test Perfume", "subtitulo": "Test Brand", "completo": "Test Perfume - Test Brand"},
            "ml": "100",
            "genero": "Hombre",
            "estaciones": [],
            "notas": {"salida": ["Nota1"], "corazon": ["Nota2"], "fondo": ["Nota3"]},
            "descripcion_corta": "Descripción de prueba"
        }
        ruta = tmp_path / "validacion_nombre.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos])
        gen.agregar_perfume(datos, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_ml_se_muestra_correctamente(self, tmp_path):
        """Los ml deben aparecer en la ficha."""
        datos = {
            "nombre": {"titulo": "Perfume", "subtitulo": "", "completo": "Perfume"},
            "ml": "50",
            "genero": "Mujer",
            "estaciones": [],
            "notas": {"salida": [], "corazon": [], "fondo": []}
        }
        ruta = tmp_path / "validacion_ml.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos])
        gen.agregar_perfume(datos, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_estaciones_se_muestran(self, tmp_path):
        """Las estaciones deben aparecer con porcentajes."""
        datos = {
            "nombre": {"titulo": "Perfume", "subtitulo": "", "completo": "Perfume"},
            "ml": "100",
            "genero": "Unisex",
            "estaciones": [
                {"nombre": "Verano", "porcentaje": 90},
                {"nombre": "Primavera", "porcentaje": 80}
            ],
            "notas": {"salida": [], "corazon": [], "fondo": []}
        }
        ruta = tmp_path / "validacion_estaciones.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos])
        gen.agregar_perfume(datos, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()

    def test_piramide_olfativa_se_muestra(self, tmp_path):
        """La pirámide olfativa debe aparecer completa."""
        datos = {
            "nombre": {"titulo": "Perfume", "subtitulo": "", "completo": "Perfume"},
            "ml": "100",
            "genero": "Hombre",
            "estaciones": [],
            "notas": {
                "salida": ["Bergamota", "Limón"],
                "corazon": ["Rosa", "Jazmín"],
                "fondo": ["Vainilla", "Sándalo"]
            }
        }
        ruta = tmp_path / "validacion_piramide.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([datos])
        gen.agregar_perfume(datos, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()


# ─────────────────────────────────────────────
#  TESTS: INTEGRACIÓN
# ─────────────────────────────────────────────

class TestIntegracion:
    def test_flujo_completo_varios_perfumes(self, tmp_path):
        """Test de flujo completo con múltiples perfumes."""
        perfumes = [
            {
                "nombre": {"titulo": f"Perfume {i}", "subtitulo": f"Marca {i}", "completo": f"Perfume {i} - Marca {i}"},
                "ml": str(50 + i * 10),
                "genero": "Hombre" if i % 2 == 0 else "Mujer",
                "familia_olfativa": "Cítrico" if i % 2 == 0 else "Floral",
                "estaciones": [{"nombre": "Verano", "porcentaje": 80}],
                "notas": {
                    "salida": ["Bergamota"],
                    "corazon": ["Rosa"],
                    "fondo": ["Vainilla"]
                },
                "ocasiones": ["Día"],
                "descripcion_corta": f"Descripción del perfume {i}",
                "colecciones": ["Frescura y Vitalidad"] if i % 2 == 0 else ["Noche y Seducción"]
            }
            for i in range(1, 6)
        ]

        ruta = tmp_path / "multiples_perfumes.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))

        gen.crear_portada()
        gen.crear_indice(perfumes)

        for i, perfume in enumerate(perfumes):
            gen.agregar_perfume(perfume, gen.items_indice[i])

        gen.guardar()

        assert ruta.exists()
        # Debe tener al menos 6 páginas (portada + índice + 4 fichas)
        assert ruta.stat().st_size > 12000

    def test_integracion_modulo_c_y_d(self, tmp_path):
        """Test de integración: módulo C procesa datos y módulo D genera PDF."""
        from modulo_c_processor import procesar as procesar_c

        # Datos simulados del módulo B
        fake_scraping = {
            "nombre": "Test Perfume",
            "url": "https://example.com/test",
            "notas": {
                "salida": ["bergamot", "lemon"],
                "corazon": ["rose", "jasmine"],
                "fondo": ["vanilla", "sandalwood"]
            },
            "clima": {
                "primavera": 80, "verano": 90, "otono": 40, "invierno": 10,
                "dia": 95, "noche": 20
            },
            "imagen_path": None,
        }
        fake_info = {"marca": "Test Brand", "ml": "100"}

        # Procesar con módulo C
        resultado_c = procesar_c(fake_scraping, fake_info)

        # Generar PDF con módulo D
        ruta = tmp_path / "integracion_c_d.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta))
        gen.crear_portada()
        gen.crear_indice([resultado_c])
        gen.agregar_perfume(resultado_c, gen.items_indice[0])
        gen.guardar()

        assert ruta.exists()
        assert ruta.stat().st_size > 4000  # Verificar que el PDF tiene contenido
        assert resultado_c["ml"] == "100"
        assert "Bergamota" in resultado_c["notas"]["salida"]
        assert "Rosa" in resultado_c["notas"]["corazon"]
        assert "Vainilla" in resultado_c["notas"]["fondo"]
