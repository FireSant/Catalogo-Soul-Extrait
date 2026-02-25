# Soul Extrait - Catálogo de Perfumería

Este proyecto genera catálogos de perfumería en formato PDF. Utiliza OpenRouter con el modelo **Meta LLaMA 3.1 8B Instruct** (solo texto) para extraer fichas técnicas (notas, clima, descripción) y un motor de diseño basado en FPDF2.

## 🚀 Cómo Funciona

1. **Prepara tus imágenes:** Coloca todas las imágenes de perfumes en la carpeta `imagenes_temp/`. El sistema asignará la primera imagen al primer perfume de la lista, la segunda al segundo, y así sucesivamente (orden alfabético).

2. **Prepara tu lista:** Coloca tu lista de perfumes en `data/lista_perfumes.csv` con columnas: `nombre`, `marca` (opcional), `precio` (opcional), `ml` (opcional).

3. **Ejecuta:** `python main.py`

4. **Resultado:** El catálogo PDF se genera en `output/catalogo_soul_extrait.pdf`.

## 📁 Estructura del Proyecto

### Módulos Principales

- [`main.py`](main.py:1) — Orquestador central: carga la lista, asigna imágenes por posición, coordina los módulos y genera el PDF.
- [`modulo_a_input.py`](modulo_a_input.py:1) — Gestión de entrada y caché: lee CSV/Excel, evita reprocesar perfumes ya escrapeados.
- [`modulo_b_ia_extractor.py`](modulo_b_ia_extractor.py:1) — Extracción de datos con IA (OpenRouter + Meta LLaMA 3.1 8B Instruct): obtiene fichas técnicas (notas, clima, descripción) sin buscar imágenes.
- [`modulo_c_processor.py`](modulo_c_processor.py:1) — Traducción y lógica: traduce notas del inglés al español, determina estaciones ideales, formatea nombres.
- [`modulo_d_pdf.py`](modulo_d_pdf.py:1) — Generador de PDF: diseño elegante con índice interactivo, botones de WhatsApp y soporte para imágenes.

### Carpetas del Proyecto

```
soul_extrait/
├── main.py
├── modulo_a_input.py
├── modulo_b_ia_extractor.py
├── modulo_c_processor.py
├── modulo_d_pdf.py
├── requirements.txt
├── .gitignore
├── README.md
├── CHANGELOG.md
├── assets/
│   └── logo.png
├── data/
│   ├── lista_perfumes.csv
│   ├── cache_scrapeados.csv
│   └── test_perfumes.csv
├── tests/
│   ├── conftest.py
│   ├── check_models.py
│   ├── test_modulo_a.py
│   ├── test_modulo_b_imagenes.py
│   ├── test_modulo_c.py
│   ├── test_descarga_imagen.py
│   └── debug/
├── .pytest_cache/
└── [imagenes_temp/]        # Debes crear esta carpeta manualmente
    [output/]               # Se crea automáticamente al generar el PDF
```

**Nota:** Las carpetas `imagenes_temp/` y `output/` no existen inicialmente y deben crearse según sea necesario.

## 📸 Sistema de Imágenes (v1.4.0)

- **Asignación por posición:** Las imágenes se asignan según el orden en la lista (no por nombre).
- **Carpeta `imagenes_temp/`:** Debes colocar manualmente las imágenes de los perfumes.
- **Formatos soportados:** `.jpg`, `.jpeg`, `.png`, `.webp`.
- **Si faltan imágenes:** El PDF muestra un recuadro vacío con "Imagen no disponible".
- **Rutas absolutas:** El sistema guarda las rutas completas para que el PDF encuentre las imágenes sin problemas.

## 🛠 Instalación

1. **Requisitos:** Python 3.10+
2. **Entorno virtual:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configuración:** Crea un archivo `.env` con tu clave de OpenRouter:
   ```
   OPENROUTER_API_KEY=tu_clave_aqui
   ```
   (Obtén una clave gratis en [openrouter.ai](https://openrouter.ai))
   
   El sistema usa el modelo **Meta LLaMA 3.1 8B Instruct** (gratuito en OpenRouter).
4. **Ejecución:**
   ```powershell
   .\venv\Scripts\python.exe main.py
   ```

## 📂 Carpetas Importantes

- `data/` — Lista de perfumes (CSV/Excel).
- `imagenes_temp/` — Imágenes manuales de perfumes.
- `output/` — Catálogos PDF generados.
- `cache/` — Caché de perfumes ya procesados (`cache_scrapeados.csv`).

## 🔧 Dependencias

- `fpdf2` — Generación de PDF
- `pandas` — Manejo de datos
- `openrouter` — Acceso a modelos de IA (Meta LLaMA 3.1 8B Instruct)
- `loguru` — Logging estructurado
- `tqdm` — Barra de progreso
- `Pillow` — Procesamiento de imágenes

