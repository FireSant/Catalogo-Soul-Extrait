import pytest
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importa las funciones del módulo b
from modulo_b_ia_extractor import scrape_perfume, _slug


@pytest.mark.asyncio
async def test_scrape_perfume_extrae_datos_con_ia():
    """Verifica que scrape_perfume extrae datos con IA y retorna imagen_path=None."""
    perfume_nombre = "Bleu de Chanel"
    marca = "Chanel"

    mock_ia_data = {
        "familia_olfativa": "Amaderada Aromática",
        "genero": "Hombre",
        "descripcion_corta": "Una fragancia icónica y sofisticada de Chanel.",
        "ocasiones_de_uso": ["Noche", "Casual"],
        "notas": {"salida": [], "corazon": [], "fondo": []},
        "clima": {"primavera": 0, "verano": 0, "otono": 0, "invierno": 0, "dia": 0, "noche": 0},
    }

    with patch("modulo_b_ia_extractor._extraer_ia", new_callable=AsyncMock) as mock_extraer_ia:
        mock_extraer_ia.return_value = mock_ia_data

        # Ejecutar la función a testear
        result = await scrape_perfume(perfume_nombre, marca)

        # Verificar aserciones
        assert result is not None
        assert result["nombre"] == perfume_nombre
        assert result["imagen_path"] is None  # Ya no se descarga imagen en modulo_b
        assert result["url"] == ""  # Ya no se obtiene URL
        assert result["genero"] == "Hombre"
        assert result["descripcion_corta"] == "Una fragancia icónica y sofisticada de Chanel."

        # Verificar que _extraer_ia fue llamada
        mock_extraer_ia.assert_called_once_with(perfume_nombre, marca)


@pytest.mark.asyncio
async def test_scrape_perfume_sin_datos_ia():
    """Verifica que scrape_perfume retorna None si la IA no devuelve datos."""
    perfume_nombre = "Perfume Desconocido"
    marca = "Marca X"

    with patch("modulo_b_ia_extractor._extraer_ia", new_callable=AsyncMock) as mock_extraer_ia:
        mock_extraer_ia.return_value = {}  # Datos vacíos

        result = await scrape_perfume(perfume_nombre, marca)

        assert result is None
        mock_extraer_ia.assert_called_once_with(perfume_nombre, marca)


@pytest.mark.asyncio
async def test_scrape_perfume_openrouter_no_configurado():
    """Verifica que scrape_perfume retorna None si OpenRouter no está configurado."""
    perfume_nombre = "Test Perfume"
    marca = "Test Marca"

    # Simular que openrouter_client es None
    with patch("modulo_b_ia_extractor.openrouter_client", None):
        result = await scrape_perfume(perfume_nombre, marca)

        assert result is None


@pytest.mark.asyncio
async def test_scrape_perfume_ia_falla_todos_los_intentos():
    """Verifica que scrape_perfume retorna None si la IA falla en todos los reintentos."""
    perfume_nombre = "Perfume con Fallos"
    marca = "Marca Y"

    with patch("modulo_b_ia_extractor._extraer_ia", new_callable=AsyncMock) as mock_extraer_ia:
        mock_extraer_ia.return_value = {}  # Siempre devuelve vacío

        result = await scrape_perfume(perfume_nombre, marca)

        assert result is None
        # Verificar que se intentó al menos una vez
        assert mock_extraer_ia.called


def test_slug_funcionamiento():
    """Verifica que la función _slug genera nombres de archivo válidos."""
    casos = [
        ("Bleu de Chanel", "bleu_de_chanel"),
        ("Good Girl Carolina Herrera", "good_girl_carolina_herrera"),
        ("La Vie Est Belle", "la_vie_est_belle"),
        ("Añade Caracteres Especiales!", "anade_caracteres_especiales"),
        ("   Espacios   Extra   ", "espacios_extra"),
    ]

    for entrada, esperado in casos:
        resultado = _slug(entrada)
        assert resultado == esperado, f"Para '{entrada}' se esperaba '{esperado}', se obtuvo '{resultado}'"
