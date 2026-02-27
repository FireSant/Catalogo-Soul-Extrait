"""
conftest.py — Fixtures compartidos para todos los tests de Soul Extrait
"""
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Directorio temporal que simula /data/ del proyecto."""
    return tmp_path


@pytest.fixture
def csv_valido(tmp_path):
    """CSV de prueba con 3 perfumes válidos."""
    ruta = tmp_path / "lista_test.csv"
    ruta.write_text(
        "nombre,marca,ml\n"
        "Good Girl,Carolina Herrera,80\n"
        "Black Opium,Yves Saint Laurent,50\n"
        "Kirke,Tiziana Terenzi,100\n",
        encoding="utf-8-sig",
    )
    return ruta


@pytest.fixture
def csv_sin_columna_nombre(tmp_path):
    """CSV que NO tiene columna 'nombre' — debe lanzar ValueError."""
    ruta = tmp_path / "lista_mala.csv"
    ruta.write_text(
        "perfume,marca\nGood Girl,Carolina Herrera\n",
        encoding="utf-8-sig",
    )
    return ruta


@pytest.fixture
def resultado_scraping_fake():
    """Resultado de scraping simulado del Módulo B."""
    return {
        "nombre": "Good Girl",
        "url": "https://www.fragrantica.es/perfumes/carolina-herrera/good-girl-29298.html",
        "notas": {
            "salida":  ["almond", "coffee", "bergamot"],
            "corazon": ["rose", "jasmine", "tuberose"],
            "fondo":   ["sandalwood", "vanilla", "musk"],
        },
        "clima": {
            "primavera": 20, "verano": 15,
            "otono": 45,    "invierno": 60,
            "dia": 30,      "noche": 70,
        },
        "imagen_path": None,
        "ya_procesado": False,
    }


@pytest.fixture
def info_lista_fake():
    """Datos de la lista del perfume (Módulo A)."""
    return {"marca": "Carolina Herrera", "ml": "80"}


@pytest.fixture
def datos_integracion_completos():
    """Datos completos para test de integración A->C->D."""
    return {
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


@pytest.fixture
def lista_perfumes_simulada(tmp_path):
    """Crea un CSV simulado y retorna la ruta y los datos esperados."""
    ruta = tmp_path / "lista_simulada.csv"
    ruta.write_text(
        "nombre,marca,ml\n"
        "Good Girl,Carolina Herrera,80\n"
        "Black Opium,Yves Saint Laurent,50\n",
        encoding="utf-8-sig"
    )
    return ruta
