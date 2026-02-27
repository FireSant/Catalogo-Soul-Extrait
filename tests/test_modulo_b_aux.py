"""
tests/test_modulo_b_aux.py — Tests para funciones auxiliares del Módulo B (sin API)
"""
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from modulo_c_processor import _derivar_colecciones


# ─────────────────────────────────────────────
#  TESTS: FUNCIÓN _derivar_colecciones
# ─────────────────────────────────────────────

class TestDerivarColecciones:
    def test_citrico_no_gourmand_va_a_frescura(self):
        """Cítrico que NO es gourmand debe ir a Frescura y Vitalidad."""
        notas = {"salida": ["bergamot", "lemon"], "corazon": [], "fondo": ["musk"]}
        colecciones = _derivar_colecciones("Cítrico", "Hombre", notas)
        assert "Frescura y Vitalidad" in colecciones
        assert "Noche y Seducción" not in colecciones

    def test_citrico_gourmand_va_a_ambas(self):
        """Cítrico que ES gourmand puede ir a ambas colecciones si llega a 2 puntos."""
        notas = {"salida": ["bergamot"], "corazon": [], "fondo": ["vainilla", "caramelo"]}
        colecciones = _derivar_colecciones("Cítrico", "Mujer", notas)
        # Familia cítrica (+2) → Frescura y Vitalidad
        # Notas gourmand (+2) → Noche y Seducción
        assert "Frescura y Vitalidad" in colecciones
        assert "Noche y Seducción" in colecciones

    def test_gourmand_va_a_noche_seduccion(self):
        """Perfume con notas dulces en fondo debe ir a Noche y Seducción."""
        notas = {"salida": ["bergamot"], "corazon": ["rosa"], "fondo": ["vainilla", "chocolate"]}
        colecciones = _derivar_colecciones("Floral", "Mujer", notas)
        assert "Noche y Seducción" in colecciones

    def test_amaderado_va_a_elegancia(self):
        """Amaderado debe ir a Elegancia e Intensidad."""
        notas = {"salida": ["bergamot"], "corazon": [], "fondo": ["sandalwood", "cedar"]}
        colecciones = _derivar_colecciones("Amaderado", "Hombre", notas)
        assert "Elegancia e Intensidad" in colecciones

    def test_oriental_va_a_noche_seduccion(self):
        """Oriental debe ir a Noche y Seducción."""
        colecciones = _derivar_colecciones("Oriental", "Unisex", {"salida": [], "corazon": [], "fondo": []})
        assert "Noche y Seducción" in colecciones

    def test_unisex_va_a_fuerza_elegancia(self):
        """Unisex debe ir a Elegancia e Intensidad."""
        colecciones = _derivar_colecciones("Floral", "Unisex", {"salida": [], "corazon": [], "fondo": []})
        assert "Elegancia e Intensidad" in colecciones

    def test_sin_colecciones_asignadas_va_a_fuerza_elegancia(self):
        """Si todas las puntuaciones son 0, debe ir a Elegancia e Intensidad por defecto."""
        notas = {"salida": ["rosa"], "corazon": ["lirio"], "fondo": ["musk"]}
        colecciones = _derivar_colecciones("Aromático", "Hombre", notas)
        assert "Elegancia e Intensidad" in colecciones

    def test_multiples_colecciones(self):
        """Puede asignar múltiples colecciones si aplica."""
        # Gourmand + Unisex → Noche y Seducción + Elegancia e Intensidad
        notas = {"salida": [], "corazon": [], "fondo": ["vainilla"]}
        colecciones = _derivar_colecciones("Oriental", "Unisex", notas)
        assert "Noche y Seducción" in colecciones
        assert "Elegancia e Intensidad" in colecciones

    def test_case_insensitive_familia(self):
        """Debe ser case-insensitive para familia olfativa."""
        # Usar notas que NO sean gourmand para probar cítrico → frescura
        notas = {"salida": ["bergamot"], "corazon": [], "fondo": ["musk"]}
        colecciones = _derivar_colecciones("cítrico", "Hombre", notas)
        assert "Frescura y Vitalidad" in colecciones

    def test_sin_notas_no_falla(self):
        """Con notas vacías no debe fallar."""
        notas = {"salida": [], "corazon": [], "fondo": []}
        colecciones = _derivar_colecciones("Cítrico", "Hombre", notas)
        # Cítrico sin gourmand → Frescura y Vitalidad
        assert "Frescura y Vitalidad" in colecciones

    def test_notas_dulces_varias_opciones(self):
        """Debe detectar various notas dulces."""
        for nota_dulce in ["vainilla", "caramelo", "chocolate", "miel", "praliné", "tonka"]:
            notas = {"salida": [], "corazon": [], "fondo": [nota_dulce]}
            colecciones = _derivar_colecciones("Floral", "Mujer", notas)
            assert "Noche y Seducción" in colecciones, f"Falló con nota: {nota_dulce}"

    def test_citrico_con_musk_no_es_gourmand(self):
        """Cítrico con musk NO es gourmand."""
        notas = {"salida": ["bergamot", "lemon"], "corazon": [], "fondo": ["musk"]}
        colecciones = _derivar_colecciones("Cítrico", "Hombre", notas)
        assert "Frescura y Vitalidad" in colecciones
        assert "Noche y Seducción" not in colecciones

    def test_amaderado_sin_notas_dulces_no_es_gourmand(self):
        """Amaderado sin notas dulces no es gourmand."""
        notas = {"salida": [], "corazon": [], "fondo": ["sandalwood", "cedar"]}
        colecciones = _derivar_colecciones("Amaderado", "Hombre", notas)
        assert "Elegancia e Intensidad" in colecciones  # Por ser amaderado
        assert "Frescura y Vitalidad" not in colecciones

    def test_colecciones_sin_duplicados(self):
        """No debe retornar colecciones duplicadas."""
        # Forzar múltiples rutas a la misma colección
        notas = {"salida": [], "corazon": [], "fondo": ["vainilla", "caramelo"]}
        colecciones = _derivar_colecciones("Cítrico Gourmand", "Unisex", notas)
        # Debe tener Noche y Seducción (por gourmand) y Elegancia e Intensidad (por Unisex)
        # pero no duplicados
        assert colecciones.count("Noche y Seducción") <= 1
        assert colecciones.count("Elegancia e Intensidad") <= 1
