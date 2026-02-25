"""
conftest.py — Fixtures compartidos para todos los tests de Soul Extrait
"""
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Directorio temporal que simula /data/ del proyecto."""
    return tmp_path


@pytest.fixture
def csv_valido(tmp_path):
    """CSV de prueba con 3 perfumes válidos."""
    ruta = tmp_path / "lista_test.csv"
    ruta.write_text(
        "nombre,marca,precio,ml\n"
        "Good Girl,Carolina Herrera,89990,80\n"
        "Black Opium,Yves Saint Laurent,120000,50\n"
        "Kirke,Tiziana Terenzi,320000,100\n",
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
    return {"marca": "Carolina Herrera", "precio": "89990", "ml": "80"}
