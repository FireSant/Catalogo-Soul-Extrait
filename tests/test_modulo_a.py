"""
tests/test_modulo_a.py — Tests para el Módulo A: Orquestador de Entrada
"""
import shutil
from pathlib import Path

import pandas as pd
import pytest

# Ajuste de ruta para que pytest encuentre los módulos del proyecto
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import modulo_a_input as mod_a


# ─────────────────────────────────────────────
#  1. CARGA DE ARCHIVOS
# ─────────────────────────────────────────────

class TestCargarLista:
    def test_carga_csv_valido(self, csv_valido):
        """Debe cargar correctamente y retornar 3 filas."""
        df = mod_a.cargar_lista(csv_valido)
        assert len(df) == 3
        assert "nombre" in df.columns

    def test_columnas_opcionales_creadas(self, csv_valido):
        """Si faltan columnas opcionales, deben agregarse vacías."""
        df = mod_a.cargar_lista(csv_valido)
        for col in ("marca", "ml"):
            assert col in df.columns

    def test_columna_nombre_obligatoria(self, csv_sin_columna_nombre):
        """Sin columna 'nombre' debe lanzar ValueError."""
        with pytest.raises(ValueError, match="nombre"):
            mod_a.cargar_lista(csv_sin_columna_nombre)

    def test_archivo_no_existe(self, tmp_path):
        """Archivo inexistente lanza FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            mod_a.cargar_lista(tmp_path / "no_existe.csv")

    def test_formato_no_soportado(self, tmp_path):
        """Extensión no soportada lanza ValueError."""
        ruta = tmp_path / "lista.txt"
        ruta.write_text("nombre\nGood Girl\n")
        with pytest.raises(ValueError, match="Formato"):
            mod_a.cargar_lista(ruta)

    def test_filas_vacias_eliminadas(self, tmp_path):
        """Las filas con nombre vacío deben eliminarse."""
        ruta = tmp_path / "lista_con_vacios.csv"
        ruta.write_text(
            "nombre,marca\nGood Girl,Carolina Herrera\n,,\n   ,\nKirke,Tiziana\n",
            encoding="utf-8-sig",
        )
        df = mod_a.cargar_lista(ruta)
        assert len(df) == 2

    def test_nombres_columnas_normalizados(self, tmp_path):
        """Nombres de columnas con espacios o mayúsculas se normalizan."""
        ruta = tmp_path / "lista_cols.csv"
        ruta.write_text("  Nombre ,  Marca  \nGood Girl,CH\n", encoding="utf-8-sig")
        df = mod_a.cargar_lista(ruta)
        assert "nombre" in df.columns
        assert "marca" in df.columns


# ─────────────────────────────────────────────
#  2. SKIP LOGIC Y CACHÉ
# ─────────────────────────────────────────────

class TestCache:
    def test_guardar_y_cargar_desde_cache(self, tmp_path, monkeypatch, resultado_scraping_fake):
        """Guardar un resultado en caché y recuperarlo."""
        # Redirigir CACHE_FILE al directorio temporal
        monkeypatch.setattr(mod_a, "CACHE_FILE", tmp_path / "cache_scrapeados.csv")

        mod_a._guardar_en_cache(resultado_scraping_fake)
        recuperado = mod_a.cargar_desde_cache("Good Girl")

        assert recuperado is not None
        assert recuperado["nombre"] == "Good Girl"
        assert recuperado["ya_procesado"] is True

    def test_cache_inexistente_retorna_none(self, tmp_path, monkeypatch):
        """Buscar en caché vacío retorna None."""
        monkeypatch.setattr(mod_a, "CACHE_FILE", tmp_path / "no_existe.csv")
        resultado = mod_a.cargar_desde_cache("Perfume Fantasma")
        assert resultado is None

    def test_perfumes_pendientes_vs_en_cache(self, csv_valido, tmp_path, monkeypatch, resultado_scraping_fake):
        """Un perfume en caché se marca 'en_cache'; el resto como 'pendiente'."""
        monkeypatch.setattr(mod_a, "CACHE_FILE", tmp_path / "cache_test.csv")

        # Precargar 'Good Girl' en caché
        resultado_scraping_fake["nombre"] = "Good Girl"
        mod_a._guardar_en_cache(resultado_scraping_fake)

        df = mod_a.cargar_lista(csv_valido)
        perfumes = mod_a.obtener_perfumes_pendientes(df)

        estados = {p["nombre"]: p["estado"] for p in perfumes}
        assert estados["Good Girl"] == "en_cache"
        assert estados["Black Opium"] == "pendiente"
        assert estados["Kirke"] == "pendiente"

    def test_cache_notas_pipe_separadas(self, tmp_path, monkeypatch):
        """Las notas se almacenan como pipe-separated y se recuperan como lista."""
        monkeypatch.setattr(mod_a, "CACHE_FILE", tmp_path / "cache_notas.csv")
        resultado = {
            "nombre": "Kirke",
            "url": "https://fragrantica.es/kirke",
            "notas": {"salida": ["bergamot", "lemon"], "corazon": ["rose"], "fondo": ["musk"]},
            "clima": {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 0, "noche": 0},
            "imagen_path": None,
        }
        mod_a._guardar_en_cache(resultado)
        recuperado = mod_a.cargar_desde_cache("Kirke")

        assert recuperado["notas"]["salida"] == ["bergamot", "lemon"]
        assert recuperado["notas"]["corazon"] == ["rose"]
