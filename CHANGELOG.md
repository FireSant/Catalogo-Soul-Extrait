# Changelog - Soul Extrait

## [1.8.2] - 2026-03-03
### Added
- **Inferencia automática de familia olfativa:** Nueva función `inferir_familia_olfativa()` en `modulo_c_processor.py` que analiza las notas, nombre, descripción y género para determinar la familia olfativa cuando la IA no la proporciona:
  - Sistema de puntuación por 12 familias: Cítrico, Aromático, Floral, Frutal, Oriental, Gourmand, Amaderado, Acuático, Verde, Chypre, Fougère, Cuero
  - Detección de combinaciones específicas: Amaderado-Aromático, Floral-Gourmand, Cítrico-Acuático
  - Bonificaciones por keywords en nombre y descripción
  - Fallback basado en género si no hay suficientes indicadores
  - Garantiza que TODOS los perfumes tengan una familia olfativa en el índice del PDF

### Fixed
- **Bug crítico en asignación de imágenes:** Se corrigió el algoritmo `encontrar_imagen_perfume()` que incorrectamente asignaba imágenes de "Lady Million" (mujer) a "1 Million" (hombre) y otros perfumes de hombre:
  - Eliminado fallback que devolvía la primera imagen de la lista sin verificar fuzzy match
  - Mejorado fuzzy matching en paso 2d (género inferido) incluyendo la marca en el nombre objetivo
  - Ahora distingue correctamente entre versiones con nombres similares pero diferente género/marca
  - Tests unitarios agregados en `tests/test_modulo_d.py::TestEncontrarImagenPerfume`

### Changed
- **Módulo C (`modulo_c_processor.py`):**
  - Integrada inferencia de familia olfativa en la función `procesar()` para ambos caminos (con/sin referencia)
  - La descripción ahora se traduce ANTES de ser usada para inferencia
  - Mejora en la precisión del algoritmo de asignación de categorías (colecciones) mediante penalizaciones y bonificaciones específicas:
    - Penalización de -5 puntos si las notas contienen `cuero`, `tabaco` u `oud` al evaluar Frescura
    - Penalización de -2 puntos si la descripción contiene palabras clave de Noche o Elegancia al evaluar Frescura
    - Bonificación de +2 puntos automática para perfumes unisex en Elegancia e Intensidad
- **Módulo D (`modulo_d_pdf.py`):** Refinamiento de lógica en `encontrar_imagen_perfume()` para evitar falsos positivos

## [1.8.1] - 2026-03-03
### Fixed
- **Bug crítico en asignación de imágenes:** Se corrigió el algoritmo `encontrar_imagen_perfume()` que incorrectamente asignaba imágenes de "Lady Million" (mujer) a "1 Million" (hombre) y otros perfumes de hombre:
  - Eliminado fallback que devolvía la primera imagen de la lista sin verificar fuzzy match
  - Mejorado fuzzy matching en paso 2d (género inferido) incluyendo la marca en el nombre objetivo
  - Ahora distingue correctamente entre versiones con nombres similares pero diferente género/marca
  - Tests unitarios agregados en `tests/test_modulo_d.py::TestEncontrarImagenPerfume`

### Changed
- **Módulo D (`modulo_d_pdf.py`):** Refinamiento de lógica en `encontrar_imagen_perfume()` para evitar falsos positivos
- **Módulo C (`modulo_c_processor.py`):** Mejora en la precisión del algoritmo de asignación de categorías (colecciones) mediante penalizaciones y bonificaciones específicas:
  - Penalización de -5 puntos si las notas contienen `cuero`, `tabaco` u `oud` al evaluar Frescura
  - Penalización de -2 puntos si la descripción contiene palabras clave de Noche o Elegancia al evaluar Frescura
  - Bonificación de +2 puntos automática para perfumes unisex en Elegancia e Intensidad
  - Estos ajustes mejoran la discriminación entre las tres colecciones y evitan clasificaciones incorrectas

## [1.8.0] - 2026-03-02
### Added
- **Asignación de imágenes por género:** El sistema ahora distingue correctamente entre versiones hombre/mujer del mismo perfume:
  - Parámetro `genero` en función `encontrar_imagen_perfume()` de `modulo_d_pdf.py`
  - Filtrado de imágenes por palabras clave: `hombre`/`male`/`pour_homme` vs `mujer`/`female`/`pour_femme`
  - Búsqueda por subcadena y por marca dentro del género correspondiente
  - Fallback a primera imagen del género correcto si no hay coincidencia
  - Integración en `main.py` priorizando género del CSV sobre scraping


### Changed
- **Módulo D (`modulo_d_pdf.py`):** Función `encontrar_imagen_perfume()` ahora recibe parámetro `genero` y aplica lógica de priorización por género
- **Módulo A (`main.py`):** Paso de parámetro `genero` al buscar imágenes

### Fixed
- **Asignación incorrecta de imágenes:** Perfumes de hombre ya no usan imágenes de mujer y viceversa

## [1.7.0] - 2026-02-27
### Added
- **Sistema de estaciones mejorado:** Umbral reducido de 40% a 20% para mayor sensibilidad
- **Bonificaciones por notas:** Algoritmo de conocimiento de perfumería que ajusta porcentajes de estaciones basándose en las notas olfativas:
  - Notas cítricas/verdes → +15% a Primavera/Verano
  - Notas acuáticas → +15% a Verano
  - Notas especiadas/amaderadas → +15% a Otoño/Invierno
  - Notas gourmand/cálidas → +15% a Invierno
- **Inferencia inteligente de ocasiones:** Nueva función `inferir_ocasiones()` que analiza notas, descripción, familia olfativa y género para recomendar 2-3 contextos de uso:
  - Citas románticas (dulces, gourmand, florales intensos)
  - Oficina/Negocios (cítricos, fougère, notas limpias)
  - Gimnasio/Deporte (frescos, acuáticos, deportivos)
  - Evento Formal (amaderados intensos, orientales, cuero)
  - Fin de Semana/Casual (versátiles, frutales, frescos)
  - Playa/Verano (acuáticos, cítricos, sal marina)
  - Invierno (gourmand, amaderados pesados)
  - Noche (orientales, gourmand, proyección fuerte)
- **Lógica híbrida de ocasiones:** Si la IA proporciona ocasiones, se complementan con inferencia; si no, se infieren completamente desde cero

### Changed
- **Módulo C (`modulo_c_processor.py`):**
  - `determinar_estaciones()`: Ahora recibe parámetro `notas` para aplicar bonificaciones
  - `_calcular_ajuste_estacional_por_notas()`: Nueva función que calcula bonificaciones basadas en keywords de notas
  - `inferir_ocasiones()`: Nueva función principal para inferir contextos de uso
  - `procesar()`: Integra la nueva lógica de estaciones y ocasiones
  - Límite máximo de 2 estaciones/momentos y 3 ocasiones para presentación concisa

### Fixed
- **Estaciones poco discriminativas:** El umbral del 40% era demasiado alto, ahora 20% permite mayor variación
- **Ocasiones genéricas:** Sistema anterior solo traducía de la IA, ahora genera recomendaciones inteligentes basadas en características del perfume

## [1.6.0] - 2026-02-27
### Added
- **Sistema de Base de Datos de Referencia:** Base de datos JSON (`data/referencia_notas.json`) con notas reales de más de 100 perfumes populares para garantizar precisión
- **Derivación automática de colecciones:** Algoritmo de puntuación dinámica en `modulo_c_processor.py` que clasifica automáticamente los perfumes en 3 colecciones basándose en familia olfativa, género y notas:
  - *Frescura y Vitalidad*: cítricos, acuáticos, veraniegos
  - *Noche y Seducción*: orientales, gourmand, especiados, dulces
  - *Elegancia e Intensidad*: amaderados, intensos, unisex
- **Priorización de datos de referencia:** Sistema de fallback que usa notas reales de la base de datos cuando están disponibles, sobreescribiendo lo extraído por IA
- **Traducción robusta de notas:** Diccionario ampliado con más de 100 traducciones de notas olfativas del inglés al español
- **Asignación de imágenes por posición original:** Las imágenes de `imagenes_temp/` se asignan según la posición en la lista original, no por orden de procesamiento

### Changed
- **Modelo de IA:** Actualizado de Meta LLaMA 3.1 8B Instruct a **Meta LLaMA 3.3 70B Instruct** (modelo más capable)
- **Módulo B (`modulo_b_ia_extractor.py`):**
  - Carga de referencia al iniciar para usar como guía en el prompt
  - Prompt mejorado para forzar el uso de notas exactas de la referencia
  - Temperature ajustada a 0.3 para mayor consistencia
  - Eliminación completa de todo código relacionado con búsqueda y descarga de imágenes
  - `scrape_perfume()` retorna `imagen_path: None` para asignación en `main.py`
- **Módulo C (`modulo_c_processor.py`):**
  - Carga de `data/referencia_notas.json` al iniciar
  - Si el perfume existe en la referencia, usa sus notas, género y familia olfativa directamente (notas ya en español)
  - Nueva función `_derivar_colecciones()` con sistema de puntuación por keywords
  - Priorización del género del CSV sobre el de la IA
  - Funciones `traducir_texto()` y `traducir_lista_ocasiones()` para traducción al español
- **Módulo D (`modulo_d_pdf.py`):**
  - Diseño de índice completamente nuevo: layout tipográfico por colecciones con dos columnas (Hombres | Mujeres)
  - Encabezados de colección se redibujan automáticamente en cada salto de página
  - Eliminación de emojis en el índice para look más profesional
  - Familia olfativa mostrada debajo del nombre en cursiva 8pt
  - Manejo manual de saltos de página para evitar páginas en blanco
- **Orquestador (`main.py`):**
  - Carga imágenes de `imagenes_temp/` ordenadas alfabéticamente
  - Diccionario `nombres_a_indice` para mapear nombre → posición original
  - Asignación de imagen por índice original: perfume en posición `i` → imagen en posición `i`
  - Validación: si no hay imagen para la posición, asigna `None` y registra advertencia
  - Guarda rutas como `Path` completo en JSON para que el PDF las encuentre

### Removed
- **Dependencias eliminadas:**
  - `playwright` (ya no se usa para scraping)
  - `beautifulsoup4` (ya no se parsea HTML)
  - `lxml` (dependencia indirecta removida)
  - `fake-useragent` (ya no se rotan User-Agents)
  - `requests` (ya no se descargan imágenes)
  - `duckduckgo_search` (ya no se buscan imágenes)
- **Funciones eliminadas en Módulo B:**
  - Toda lógica de scraping con Playwright
  - `buscar_imagen_web()`, `_buscar_en_duckduckgo()`, `buscar_imagen_wikipedia()`, `buscar_imagen_commons()`
  - `validar_imagen_visual()`, `_descargar_imagen()`, `imagen_ya_descargada()`, `_es_imagen_valida()`
- **Constantes eliminadas en Módulo B:**
  - `IMAGENES_DIR` (ya no se descargan imágenes)
  - `OPENROUTER_MODEL_VISION` (ya no se usa modelo con visión)
  - `USER_AGENT_BROWSER` (ya no se descargan archivos)

### Fixed
- **Simplificación radical:** Flujo más simple y rápido sin búsquedas automáticas
- **Sin bloqueos:** Se eliminan riesgos de rate limiting al evitar búsquedas
- **Control total del usuario:** El usuario descarga manualmente las imágenes y las coloca en `imagenes_temp/`
- **Orden de imágenes corregido:** Las imágenes se asignan según posición original en la lista, no por orden de procesamiento
- **Clasificación de colecciones:** Corregido bug donde no se usaban `familia_olfativa` y `genero` de la referencia
- **Páginas en blanco en PDF:** Manejo manual de saltos de página en `modulo_d_pdf.py` asegura que encabezados de colección se redibujen correctamente

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
  - **Nueva lógica de asignación:** Carga imágenes de `imagenes_perfumes/` ordenadas alfabéticamente
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
