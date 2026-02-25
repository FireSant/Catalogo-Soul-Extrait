"""
tests/test_modulo_c.py — Tests para el Módulo C: Procesador de Datos
"""
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import modulo_c_processor as mod_c


# ─────────────────────────────────────────────
#  1. TRADUCCIÓN DE NOTAS
# ─────────────────────────────────────────────

class TestTraduccion:
    def test_nota_conocida_traducida(self):
        assert mod_c.traducir_nota("rose") == "Rosa"

    def test_nota_conocida_case_insensitive(self):
        assert mod_c.traducir_nota("VANILLA") == "Vainilla"
        assert mod_c.traducir_nota("Sandalwood") == "Sándalo"

    def test_nota_desconocida_devuelve_original_capitalizada(self):
        resultado = mod_c.traducir_nota("abcxyz_desconocido")
        assert resultado == "Abcxyz_Desconocido"

    def test_nota_con_espacios_limpios(self):
        assert mod_c.traducir_nota("  musk  ") == "Almizcle"

    def test_traducir_notas_completas(self):
        notas = {
            "salida":  ["bergamot", "lemon"],
            "corazon": ["rose", "jasmine"],
            "fondo":   ["sandalwood", "vanilla"],
        }
        resultado = mod_c.traducir_notas(notas)
        assert "Bergamota" in resultado["salida"]
        assert "Limón" in resultado["salida"]
        assert "Rosa" in resultado["corazon"]
        assert "Sándalo" in resultado["fondo"]
        assert "Vainilla" in resultado["fondo"]

    def test_nota_vacia_no_rompe(self):
        resultado = mod_c.traducir_nota("")
        assert isinstance(resultado, str)

    def test_piramide_vacia(self):
        notas = {"salida": [], "corazon": [], "fondo": []}
        resultado = mod_c.traducir_notas(notas)
        assert resultado == {"salida": [], "corazon": [], "fondo": []}

    def test_multiples_notas_traducidas_correctamente(self):
        notas_en = ["coffee", "almond", "caramel", "patchouli", "musk", "amber"]
        esperadas = ["Café", "Almizcle", "Ámbar"]
        resultado = [mod_c.traducir_nota(n) for n in notas_en]
        for esp in esperadas:
            assert esp in resultado


# ─────────────────────────────────────────────
#  2. LÓGICA DE ICONOS DE ESTACIÓN
# ─────────────────────────────────────────────

class TestEstaciones:
    def test_invierno_mas_alto_gana(self):
        clima = {"primavera": 10, "verano": 10, "otono": 20, "invierno": 60, "dia": 0, "noche": 0}
        resultado = mod_c.determinar_estaciones(clima)
        nombres = [e["nombre"] for e in resultado]
        assert "Invierno" in nombres

    def test_icono_correcto_por_estacion(self):
        clima = {"primavera": 0, "verano": 80, "otono": 0, "invierno": 0, "dia": 0, "noche": 0}
        resultado = mod_c.determinar_estaciones(clima)
        verano = next((e for e in resultado if e["nombre"] == "Verano"), None)
        assert verano is not None
        assert verano["icono"] == "☀️"

    def test_noche_mas_alta_que_dia(self):
        clima = {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 30, "noche": 70}
        resultado = mod_c.determinar_estaciones(clima)
        nombres = [e["nombre"] for e in resultado]
        assert "Noche" in nombres
        assert resultado[0]["nombre"] == "Noche"  # La primera debe ser la de mayor %

    def test_fallback_a_maximo_cuando_ninguno_supera_umbral(self):
        """Si ningún valor supera el UMBRAL (40%), igual retorna el máximo."""
        clima = {"primavera": 10, "verano": 15, "otono": 20, "invierno": 38, "dia": 0, "noche": 0}
        resultado = mod_c.determinar_estaciones(clima)
        nombres = [e["nombre"] for e in resultado]
        assert "Invierno" in nombres  # El máximo es Invierno

    def test_multiples_estaciones_dominantes(self):
        """Dos estaciones con > 40% deben aparecer ambas."""
        clima = {"primavera": 50, "verano": 15, "otono": 10, "invierno": 55, "dia": 0, "noche": 0}
        resultado = mod_c.determinar_estaciones(clima)
        nombres = [e["nombre"] for e in resultado]
        assert "Primavera" in nombres
        assert "Invierno" in nombres

    def test_clima_todo_cero(self):
        """Sin votos no debe lanzar error."""
        clima = {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 0, "noche": 0}
        resultado = mod_c.determinar_estaciones(clima)
        assert isinstance(resultado, list)

    def test_ordenado_por_porcentaje_descendente(self):
        clima = {"primavera": 10, "verano": 70, "otono": 50, "invierno": 20, "dia": 0, "noche": 0}
        resultado = mod_c.determinar_estaciones(clima)
        porcentajes = [e["porcentaje"] for e in resultado]
        assert porcentajes == sorted(porcentajes, reverse=True)


# ─────────────────────────────────────────────
#  3. FORMATEO DE NOMBRE
# ─────────────────────────────────────────────

class TestFormateoNombre:
    def test_titulo_capitalizado(self):
        fn = mod_c.formatear_nombre("good girl")
        assert fn["titulo"] == "Good Girl"

    def test_subtitulo_vacio_si_no_hay_marca(self):
        fn = mod_c.formatear_nombre("Good Girl")
        assert fn["subtitulo"] == ""

    def test_completo_con_marca(self):
        fn = mod_c.formatear_nombre("Good Girl", "Carolina Herrera")
        assert "Good Girl" in fn["completo"]
        assert "Carolina Herrera" in fn["completo"]

    def test_completo_sin_marca(self):
        fn = mod_c.formatear_nombre("Kirke")
        assert fn["completo"] == "Kirke"

    def test_espacios_en_blancos_limpiados(self):
        fn = mod_c.formatear_nombre("  Good Girl  ", "  Carolina Herrera  ")
        assert fn["titulo"] == "Good Girl"
        assert fn["subtitulo"] == "Carolina Herrera"


# ─────────────────────────────────────────────
#  4. PROCESO COMPLETO
# ─────────────────────────────────────────────

class TestProcesar:
    def test_retorna_dict_con_claves_correctas(self, resultado_scraping_fake, info_lista_fake):
        resultado = mod_c.procesar(resultado_scraping_fake, info_lista_fake)
        for clave in ("nombre", "notas", "estaciones", "imagen_path", "url", "precio", "ml"):
            assert clave in resultado

    def test_notas_traducidas_en_resultado_final(self, resultado_scraping_fake, info_lista_fake):
        resultado = mod_c.procesar(resultado_scraping_fake, info_lista_fake)
        assert "Bergamota" in resultado["notas"]["salida"]
        assert "Rosa" in resultado["notas"]["corazon"]
        assert "Sándalo" in resultado["notas"]["fondo"]

    def test_precio_y_ml_incluidos(self, resultado_scraping_fake, info_lista_fake):
        resultado = mod_c.procesar(resultado_scraping_fake, info_lista_fake)
        assert resultado["precio"] == "89990"
        assert resultado["ml"] == "80"

    def test_sin_info_lista_no_rompe(self, resultado_scraping_fake):
        """Sin info_lista el proceso debe completarse igualmente."""
        resultado = mod_c.procesar(resultado_scraping_fake)
        assert resultado["precio"] == ""
        assert resultado["ml"] == ""

    def test_imagen_path_none_si_no_hay_imagen(self, resultado_scraping_fake, info_lista_fake):
        resultado_scraping_fake["imagen_path"] = None
        resultado = mod_c.procesar(resultado_scraping_fake, info_lista_fake)
        assert resultado["imagen_path"] is None
