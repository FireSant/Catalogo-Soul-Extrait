# Changelog - Soul Extrait

## [1.5.0] - 2026-02-26
### Added
- **Nuevo diseño tipográfico del índice:** Índice completamente rediseñado, con layout limpio y elegante
- **Clasificación por colecciones:** Sistema de 3 colecciones para organizar el catálogo:
  - *Sensación de Frescura*: Perfumes cítricos, acuáticos, veraniegos
  - *Noche y Seducción*: Perfumes amaderados, orientales, especiados, dulces
  - *Fuerza y Elegancia*: Perfumes intensos, de alta gama, formales
- **Layout de dos columnas:** Separación visual clara entre Hombres (izquierda) y Mujeres (derecha) en cada colección
- **Información sutil:** Familia olfativa mostrada debajo del nombre en fuente cursiva 8pt
- **Soporte multicategoría:** Un perfume puede aparecer en múltiples colecciones si aplica
- **Asignación automática:** Si un perfume no tiene colecciones asignadas, se incluye en "Fuerza y Elegancia" por defecto

### Changed
- **Módulo B (`modulo_b_ia_extractor.py`):**
  - Añadido campo `colecciones` al esquema JSON de respuesta
  - Prompt actualizado para que la IA clasifique automáticamente en las 3 colecciones
- **Módulo D (`modulo_d_pdf.py`):**
  - `crear_indice()`: Reescrito completamente con nuevo diseño tipográfico
  - Eliminados todos los emojis del índice
  - Implementada lógica de agrupación por colección y género
  - Mantenida compatibilidad con el sistema de links del índice original

### Fixed
- **Clasificación automática de colecciones:** Corregido bug en `modulo_c_processor.py` donde no se usaban `familia_olfativa` y `genero` de la referencia, causando clasificaciones incorrectas
- **Páginas vacías en índice PDF:** Implementado manejo manual de saltos de página en `modulo_d_pdf.py` para evitar páginas en blanco y asegurar que los encabezados de colección se redibujen en cada nueva página

## [1.4.0] - 2026-02-25
### Added
- **Sistema de imágenes simplificado:** Asignación directa por posición desde carpeta `imagenes_temp/`
- **Carpeta de imágenes manuales:** Nueva carpeta `imagenes_temp/` para gestionar imágenes sin búsquedas automáticas
- **Mapeo por posición:** El perfume 1 recibe la primera imagen, perfume 2 la segunda, etc.
- **Validación robusta:** Si faltan imágenes, se asigna `null` sin fallar el PDF
- **Documentación de imágenes:** Sección en README con instrucciones detalladas

### Changed
- **Modelo de IA:** Cambiado de Qwen Vision a **Meta LLaMA 3.1 8B Instruct** (solo texto, sin capacidad de visión)
- **Módulo B (`modulo_b_ia_extractor.py`):**
  - **Eliminada** toda lógica de búsqueda de imágenes (DuckDuckGo, Wikipedia, Wikimedia Commons)
  - **Eliminada** validación visual con Qwen Vision
  - **Eliminada** descarga automática de imágenes
  - Ahora solo extrae ficha técnica con OpenRouter usando Meta LLaMA
  - `scrape_perfume()` retorna `imagen_path: None` (será asignado por `main.py`)
  - Prompt mejorado para forzar respuesta JSON estricta
- **Módulo A (`modulo_a_input.py`):**
  - `cargar_desde_cache()` y `_guardar_en_cache()` mantienen compatibilidad con campo `imagen_path`
  - CSV reader más tolerante: `engine="python", on_bad_lines="skip"` para filas mal formadas
- **Módulo C (`modulo_c_processor.py`):**
  - Sin cambios necesarios (ya manejaba `imagen_path` correctamente)
- **Módulo D (`modulo_d_pdf.py`):**
  - Sin cambios necesarios (ya manejaba `imagen_path` como `Path | None`)
- **Orquestador (`main.py`):**
  - **Nueva lógica de asignación:** Carga imágenes de `imagenes_temp/` ordenadas alfabéticamente
  - **Asignación por posición original:** Se crea mapping `nombres_a_indice` para mantener el orden de la lista original
  - **Validación:** Si no hay imagen para la posición, asigna `None` y registra advertencia
  - Las rutas de imagen se guardan como `Path` completo en el JSON para que el PDF las encuentre

### Removed
- **Dependencias eliminadas:**
  - `duckduckgo_search` (ya no se usa)
  - Llamadas a Qwen Vision (OpenRouter)
- **Funciones eliminadas en Módulo B:**
  - `buscar_imagen_web()`
  - `_buscar_en_duckduckgo()`
  - `validar_imagen_visual()`
  - `_descargar_imagen()`
  - `imagen_ya_descargada()`
  - `_es_imagen_valida()`
- **Constantes eliminadas:**
  - `IMAGENES_DIR` (ya no se descargan imágenes)
  - `OPENROUTER_MODEL_VISION` (ya no se usa Qwen)
  - `USER_AGENT_BROWSER` (ya no se descargan archivos)

### Fixed
- **Simplificación radical:** El flujo ahora es más simple, rápido y sin dependencias externas de búsqueda
- **Sin bloqueos:** Al evitar búsquedas automáticas, se eliminan riesgos de bloqueos por rate limiting
- **Control total del usuario:** El usuario descarga manualmente las imágenes y las coloca en la carpeta
- **Orden de imágenes corregido:** Las imágenes ahora se asignan según la posición en la lista original, sin importar el orden de procesamiento (pendientes primero, caché después)
- **Módulo A (`modulo_a_input.py`):**
  - `cargar_desde_cache()` y `_guardar_en_cache()` mantienen compatibilidad con campo `imagen_path`
- **Módulo C (`modulo_c_processor.py`):**
  - Sin cambios necesarios (ya manejaba `imagen_path` correctamente)
- **Módulo D (`modulo_d_pdf.py`):**
  - Sin cambios necesarios (ya manejaba `imagen_path` como `Path | None`)
- **Orquestador (`main.py`):**
  - **Nueva lógica de asignación:** Carga imágenes de `imagenes_perfumes/` ordenadas alfabéticamente
  - **Asignación por índice:** Para el perfume en posición `i`, asigna la imagen en posición `i`
  - **Validación:** Si `i >= len(imagenes)`, asigna `None` y registra advertencia
  - Las rutas de imagen se guardan como `Path` completo en el JSON para que el PDF las encuentre

### Removed
- **Dependencias eliminadas:**
  - `duckduckgo_search` (ya no se usa)
  - Llamadas a Qwen Vision (OpenRouter)
- **Funciones eliminadas en Módulo B:**
  - `buscar_imagen_web()`
  - `_buscar_en_duckduckgo()`
  - `validar_imagen_visual()`
  - `_descargar_imagen()`
  - `imagen_ya_descargada()`
  - `_es_imagen_valida()`
- **Constantes eliminadas:**
  - `IMAGENES_DIR` (ya no se descargan imágenes)
  - `OPENROUTER_MODEL_VISION` (ya no se usa Qwen)
  - `USER_AGENT_BROWSER` (ya no se descargan archivos)

### Fixed
- **Simplificación radical:** El flujo ahora es más simple, rápido y sin dependencias externas de búsqueda
- **Sin bloqueos:** Al evitar búsquedas automáticas, se eliminan riesgos de bloqueos por rate limiting
- **Control total del usuario:** El usuario descarga manualmente las imágenes y las coloca en la carpeta

## [1.3.1] - 2026-02-25
### Added
- **Búsqueda multi-idioma:** Wikipedia ES y EN con múltiples queries (nombre, nombre+marca, nombre+perfume, etc.)
- **Filtros en Commons:** Exclusión automática de imágenes de personas (actores, retratos) para encontrar solo frascos de perfume
- **Traducción de descripciones:** Todas las descripciones cortas ahora se traducen al español
- **Traducción de ocasiones:** Lista de ocasiones de uso traducida al español (day→Día, night→Noche, etc.)
- **Validación estricta de datos:** Rechazo de respuestas vacías o con solo texto del prompt en OpenRouter
- **Reintentos en extracción:** 2 intentos con backoff para obtener datos de OpenRouter
- **Reintentos en descarga:** 3 intentos con backoff exponencial para descargar imágenes

### Changed
- **Módulo B (`modulo_b_ia_extractor.py`):**
  - `buscar_imagen_wikipedia()`: ahora recibe parámetro `marca` y busca en ES/EN con múltiples estrategias
  - `buscar_imagen_commons()`: mejorada con filtros de contenido y queries específicas
  - `_extraer_ia_sync()`: validación mejorada y prompt optimizado
  - `_extraer_ia()`: añadidos reintentos
  - `_descargar_imagen()`: añadidos reintentos y verificación de integridad
- **Módulo C (`modulo_c_processor.py`):**
  - Añadida función `traducir_texto()` para descripciones
  - Añadida función `traducir_lista_ocasiones()` para ocasiones de uso
  - `procesar()`: ahora traduce descripción y ocasiones al español
- **Lista de perfumes:** Reducida a 5 perfumes para pruebas en `data/lista_perfumes.csv`

### Fixed
- **Imágenes no encontradas:** Mejorada la estrategia de búsqueda para encontrar frascos de perfume reales
- **Datos inválidos en cache:** Validación estricta evita guardar datos vacíos o incorrectos
- **Textos en inglés:** Ahora todos los textos (descripciones, ocasiones) se garantizan en español

## [1.3.0] - 2026-02-24
### Added
- **Nuevo sistema de imágenes:** Reemplazo completo de DuckDuckGo por Wikipedia API (bot-friendly, sin bloqueos Cloudflare).
- **Validación visual con IA:** Integración de Qwen Vision (qwen3-vl-30b-a3b-thinking) para verificar que las imágenes sean frascos de perfume reales.
- **Descarga segura:** User-Agent de navegador para evitar errores 403 de Wikimedia.
- **Tests de imágenes:** Nuevas pruebas unitarias en `tests/test_modulo_b_imagenes.py` que cubren todos los escenarios.

### Changed
- **Módulo B (`modulo_b_ia_extractor.py`):** Refactorización completa del flujo de extracción:
  - Antes: DuckDuckGo → Validación paralela → Descarga
  - Ahora: Wikipedia API → Validación Qwen → Descarga (solo si válida)
- **Proveedor IA:** Cambiado de Groq a OpenRouter (modelos gratuitos disponibles).
- **Robustez:** Timeouts, manejo de errores y logs mejorados.
- **Pruebas:** Eliminadas pruebas obsoletas no relacionadas con la funcionalidad actual.

### Fixed
- **Bloqueos Cloudflare:** Eliminados completamente usando API oficial de Wikipedia.
- **Errores 403 en descargas:** Solucionado con User-Agent de navegador real.
- **Validación de imágenes:** Ahora solo se descargan imágenes validadas por IA (reduce ruido).

## [1.2.2] - 2026-02-21
### Fixed
- **Navegación:** Reparado el enlace global "Volver al Índice" para que funcione en todas las páginas.
- **Estética:** Cambiado el color de acento (líneas/porcentajes) de naranja a un gris elegante.
- **Escalado de Imágenes:** Implementado ajuste de tamaño proporcional `70x70mm` para evitar solapamientos con el texto.
- **WhatsApp:** El número y el mensaje de consulta ahora se cargan dinámicamente desde el `.env`.

## [1.2.1] - 2026-02-21
### Fixed
- **Diseño de Fichas:** Restaurados los márgenes, líneas divisoras y espaciado de títulos para mayor legibilidad.
- **Procesamiento de Lista:** Asegurada la inclusión total de la lista de perfumes (10/10) mediante la limpieza de caché y mejora en la detección de imágenes.
- **Encoding:** Corregido el error de caracteres Unicode al finalizar el proceso en Windows.

## [1.2.0] - 2026-02-21
### Added
- **Navegación en PDF:** Botón "Volver al Índice" en cada ficha de perfume.
- **Marca de Agua:** Logo de la marca en la portada con opacidad ajustada (estética premium).
- **Documentación:** Creado `README.md` con explicación detallada de cada módulo.
- **Organización:** Carpeta `tests/` para scripts de depuración y logs.

### Changed
- **Estética Unificada:** Color de fondo crema y textos en negro para coincidir con la identidad visual del logo.
- **Robustez del PDF:** Mejorado el manejo de imágenes corruptas o inexistentes (ya no detienen la generación).
- **Limpieza de Proyecto:** Movidos todos los archivos `.txt` y scripts de prueba a carpetas secundarias.

### Fixed
- Error de visualización del logo en formato `.jpg`.
- Sesgo de transparencia que ocultaba elementos en la portada.
- Corregido error de atributo en el footer del PDF.

## [1.1.0] - 2026-02-21
### Added
- **Migración a IA:** Implementación de motor de scraping basado en Gemini 1.5 Flash.
- **Estrategia Fallback:** Búsqueda en DuckDuckGo si la API de Google falla.
- **Extracción Estructurada:** Generación automática de pirámides olfativas y clima ideal mediante IA.
- **Sistema de Caché:** Implementación de persistencia JSON para evitar duplicidad de costos y tiempo.

## [1.0.0] - 2026-02-19
### Added
- Estructura inicial del proyecto (Módulos A, B, C, D).
- Generación base de PDF.
- Lectura de CSV básica.
