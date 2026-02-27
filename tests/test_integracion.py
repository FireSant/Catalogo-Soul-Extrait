"""
tests/test_integracion.py — Tests de Integración Completa del Sistema
Cubre el flujo: A (Input) -> C (Processor) -> D (PDF Generator)
"""
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import modulo_a_input as mod_a
import modulo_c_processor as mod_c
import modulo_d_pdf as mod_d


class TestIntegracionCompleta:
    def test_flujo_a_c_d_con_un_perfume(self, tmp_path, datos_integracion_completos):
        """Test de integración: A -> C -> D con un solo perfume."""
        # 1. Simular datos de entrada del módulo A (ya procesados)
        # En la realidad, A lee un CSV y devuelve perfumes pendientes
        # Aquí usamos datos simulados directamente
        info_lista = {"marca": "Test Brand", "ml": "100"}

        # 2. Procesar con módulo C
        resultado_c = mod_c.procesar(datos_integracion_completos, info_lista)

        # Verificar que C procesó correctamente
        assert resultado_c["nombre"]["titulo"] == "Test Perfume"
        assert resultado_c["ml"] == "100"
        assert "Bergamota" in resultado_c["notas"]["salida"]
        assert "Rosa" in resultado_c["notas"]["corazon"]
        assert "Vainilla" in resultado_c["notas"]["fondo"]
        assert len(resultado_c["estaciones"]) > 0
        assert "colecciones" in resultado_c

        # 3. Generar PDF con módulo D
        ruta_pdf = tmp_path / "integracion_un_perfume.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta_pdf))
        gen.crear_portada()
        gen.crear_indice([resultado_c])
        gen.agregar_perfume(resultado_c, gen.items_indice[0])
        gen.guardar()

        # Verificaciones
        assert ruta_pdf.exists()
        assert ruta_pdf.stat().st_size > 3000  # Al menos 3KB

    def test_flujo_a_c_d_multiples_perfumes(self, tmp_path):
        """Test de integración con múltiples perfumes."""
        # Datos de múltiples perfumes (simulando salida de A después de procesar B)
        perfumes_raw = [
            {
                "nombre": "Perfume A",
                "url": "https://example.com/a",
                "notas": {
                    "salida": ["bergamot", "lemon"],
                    "corazon": ["rose"],
                    "fondo": ["vanilla"]
                },
                "clima": {
                    "primavera": 80, "verano": 90, "otono": 30, "invierno": 10,
                    "dia": 85, "noche": 20
                },
                "imagen_path": None,
            },
            {
                "nombre": "Perfume B",
                "url": "https://example.com/b",
                "notas": {
                    "salida": ["mandarin"],
                    "corazon": ["jasmine", "lily"],
                    "fondo": ["sandalwood", "musk"]
                },
                "clima": {
                    "primavera": 60, "verano": 40, "otono": 70, "invierno": 50,
                    "dia": 50, "noche": 80
                },
                "imagen_path": None,
            },
            {
                "nombre": "Perfume C",
                "url": "https://example.com/c",
                "notas": {
                    "salida": ["apple"],
                    "corazon": ["peach"],
                    "fondo": ["amber", "patchouli"]
                },
                "clima": {
                    "primavera": 20, "verano": 10, "otono": 60, "invierno": 90,
                    "dia": 30, "noche": 95
                },
                "imagen_path": None,
            }
        ]

        info_lista_base = {"marca": "Test Brand", "ml": "100"}

        # Procesar cada perfume con C
        resultados_c = []
        for perfume_raw in perfumes_raw:
            resultado = mod_c.procesar(perfume_raw, info_lista_base)
            resultados_c.append(resultado)

        # Verificar que todos tienen la estructura correcta
        for res in resultados_c:
            assert "nombre" in res
            assert "notas" in res
            assert "estaciones" in res
            assert "colecciones" in res

        # Generar PDF con D
        ruta_pdf = tmp_path / "integracion_multiples.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta_pdf))
        gen.crear_portada()
        gen.crear_indice(resultados_c)

        for i, res in enumerate(resultados_c):
            gen.agregar_perfume(res, gen.items_indice[i])

        gen.guardar()

        assert ruta_pdf.exists()
        # PDF debe ser considerablemente más grande (múltiples páginas)
        assert ruta_pdf.stat().st_size > 5000

    def test_flujo_completo_con_datos_reales_csv(self, tmp_path, csv_valido, monkeypatch):
        """Test de integración usando un CSV real y simulando el módulo B."""
        # Este test simula el flujo completo desde A hasta D
        #pero sin usar la API de OpenRouter

        # 1. Cargar lista con módulo A
        df = mod_a.cargar_lista(csv_valido)
        assert len(df) == 3

        # 2. Simular que ya tenemos los datos de scraping (módulo B)
        # En producción, B se llamaría para cada perfume
        datos_scraping_simulados = [
            {
                "nombre": "Good Girl",
                "url": "https://example.com/good-girl",
                "notas": {
                    "salida": ["almond", "bergamot"],
                    "corazon": ["rose", "jasmine"],
                    "fondo": ["vanilla", "sandalwood"]
                },
                "clima": {
                    "primavera": 20, "verano": 15, "otono": 45, "invierno": 60,
                    "dia": 30, "noche": 70
                },
                "imagen_path": None,
            },
            {
                "nombre": "Black Opium",
                "url": "https://example.com/black-opium",
                "notas": {
                    "salida": ["pear", "orange"],
                    "corazon": ["jasmine", "coffee"],
                    "fondo": ["vanilla", "patchouli"]
                },
                "clima": {
                    "primavera": 10, "verano": 5, "otono": 50, "invierno": 80,
                    "dia": 20, "noche": 90
                },
                "imagen_path": None,
            },
            {
                "nombre": "Kirke",
                "url": "https://example.com/kirke",
                "notas": {
                    "salida": ["bergamot", "lemon"],
                    "corazon": ["rose"],
                    "fondo": ["musk", "amber"]
                },
                "clima": {
                    "primavera": 60, "verano": 70, "otono": 40, "invierno": 20,
                    "dia": 75, "noche": 40
                },
                "imagen_path": None,
            }
        ]

        # 3. Procesar cada perfume con módulo C
        resultados_c = []
        for idx, row in df.iterrows():
            # Obtener datos de scraping simulados para este perfume
            scraping = next(
                (s for s in datos_scraping_simulados if s["nombre"] == row["nombre"]),
                datos_scraping_simulados[0]  # fallback
            )
            info_lista = {"marca": row.get("marca", ""), "ml": row.get("ml", "")}

            resultado = mod_c.procesar(scraping, info_lista)
            resultados_c.append(resultado)

        # 4. Generar PDF con módulo D
        ruta_pdf = tmp_path / "integracion_csv.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta_pdf))
        gen.crear_portada()
        gen.crear_indice(resultados_c)

        for i, res in enumerate(resultados_c):
            gen.agregar_perfume(res, gen.items_indice[i])

        gen.guardar()

        # Verificaciones finales
        assert ruta_pdf.exists()
        assert ruta_pdf.stat().st_size > 8000  # 3 perfumes con datos mínimos

        # Verificar que el PDF contiene los nombres esperados
        # (No podemos leer el contenido fácilmente sin librería extra,
        # pero confiamos en que el tamaño indica múltiples páginas)

    def test_integracion_con_imagenes(self, tmp_path, datos_integracion_completos):
        """Test de integración cuando hay imágenes disponibles."""
        # Crear una imagen de prueba
        from PIL import Image
        img_path = tmp_path / "test_perfume.jpg"
        img = Image.new("RGB", (200, 200), color="blue")
        img.save(img_path, "JPEG")

        # Modificar datos para incluir imagen
        datos_con_imagen = datos_integracion_completos.copy()
        datos_con_imagen["imagen_path"] = str(img_path)

        # Procesar con C
        resultado_c = mod_c.procesar(datos_con_imagen, {"marca": "Test", "ml": "100"})

        # Generar PDF con D
        ruta_pdf = tmp_path / "con_imagen.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta_pdf))
        gen.crear_portada()
        gen.crear_indice([resultado_c])
        gen.agregar_perfume(resultado_c, gen.items_indice[0])
        gen.guardar()

        assert ruta_pdf.exists()

    def test_integracion_sin_estaciones(self, tmp_path):
        """Test de integración cuando no hay datos de clima."""
        datos = {
            "nombre": "Perfume Sin Clima",
            "url": "https://example.com/test",
            "notas": {
                "salida": ["bergamot"],
                "corazon": ["rose"],
                "fondo": ["vanilla"]
            },
            "clima": {
                "primavera": 0, "verano": 0, "otono": 0, "invierno": 0,
                "dia": 0, "noche": 0
            },
            "imagen_path": None,
        }

        resultado_c = mod_c.procesar(datos, {"marca": "Test", "ml": "50"})

        # Debe manejar estaciones vacías sin fallar
        assert "estaciones" in resultado_c

        # Generar PDF
        ruta_pdf = tmp_path / "sin_estaciones.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta_pdf))
        gen.crear_portada()
        gen.crear_indice([resultado_c])
        gen.agregar_perfume(resultado_c, gen.items_indice[0])
        gen.guardar()

        assert ruta_pdf.exists()

    def test_integracion_multiples_colecciones(self, tmp_path):
        """Test de integración con perfumes en diferentes colecciones."""
        perfumes = [
            {
                "nombre": "Citrico Fresco",
                "url": "https://example.com/citrico",
                "notas": {
                    "salida": ["bergamot", "lemon"],
                    "corazon": [],
                    "fondo": ["musk"]
                },
                "clima": {
                    "primavera": 80, "verano": 90, "otono": 20, "invierno": 10,
                    "dia": 95, "noche": 10
                },
                "imagen_path": None,
                "familia_olfativa": "Cítrico",  # Para Frescura y Vitalidad
            },
            {
                "nombre": "Gourmand Noche",
                "url": "https://example.com/gourmand",
                "notas": {
                    "salida": ["cinnamon"],
                    "corazon": ["jasmine"],
                    "fondo": ["vanilla", "caramel", "chocolate"]
                },
                "clima": {
                    "primavera": 10, "verano": 5, "otono": 40, "invierno": 80,
                    "dia": 20, "noche": 90
                },
                "imagen_path": None,
                "familia_olfativa": "Oriental",  # Gourmand → Noche y Seducción
            }
        ]

        resultados_c = []
        for perfume in perfumes:
            resultado = mod_c.procesar(perfume, {"marca": "Test", "ml": "100"})
            resultados_c.append(resultado)

        # Verificar que se asignaron colecciones correctamente
        assert any("Frescura y Vitalidad" in r["colecciones"] for r in resultados_c)
        assert any("Noche y Seducción" in r["colecciones"] for r in resultados_c)

        # Generar PDF
        ruta_pdf = tmp_path / "multiples_colecciones.pdf"
        gen = mod_d.GeneradorCatalog(str(ruta_pdf))
        gen.crear_portada()
        gen.crear_indice(resultados_c)

        for i, res in enumerate(resultados_c):
            gen.agregar_perfume(res, gen.items_indice[i])

        gen.guardar()

        assert ruta_pdf.exists()
