"""
Módulo A: Orquestador de Entrada — Soul Extrait
===============================================
Responsabilidades:
  1. Leer lista de perfumes desde Excel (.xlsx) o CSV (.csv)
  2. Verificar qué perfumes ya fueron procesados (skip logic)
  3. Retornar un iterador limpio de perfumes pendientes
  4. Guardar resultados de la extracción en un CSV de caché local

Columnas esperadas en el archivo de entrada:
  - "nombre"  (obligatorio): ej. "Good Girl Carolina Herrera"
  - "marca"   (opcional): ej. "Carolina Herrera"
  - "precio"  (opcional): ej. "89.990"
  - "ml"      (opcional): ej. "80"
"""

import os
from pathlib import Path

import pandas as pd
from loguru import logger

# ─────────────────────────────────────────────
#   RUTAS
# ─────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
CACHE_FILE = DATA_DIR / "cache_scrapeados.csv"  # Registro de perfumes ya procesados

DATA_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
#   CARGA DEL ARCHIVO DE ENTRADA
# ─────────────────────────────────────────────

def cargar_lista(ruta_archivo: str | Path) -> pd.DataFrame:
    """
    Carga el archivo Excel o CSV con la lista de perfumes.
    Retorna un DataFrame con columna 'nombre' garantizada.

    Parámetros
    ----------
    ruta_archivo : str | Path
        Ruta al archivo .xlsx o .csv con la lista de perfumes.
    """
    ruta = Path(ruta_archivo)

    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    logger.info(f"Cargando lista desde: {ruta.name}")

    if ruta.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(ruta, dtype=str)
    elif ruta.suffix.lower() == ".csv":
        # Usar motor python para mayor tolerancia a filas mal formadas
        df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig", engine="python", on_bad_lines="skip")
    else:
        raise ValueError(f"Formato no soportado: {ruta.suffix}. Usa .xlsx o .csv")

    # Normalizar nombres de columnas (trim + minúsculas)
    df.columns = [c.strip().lower() for c in df.columns]

    if "nombre" not in df.columns:
        raise ValueError(
            "El archivo debe tener una columna llamada 'nombre' con el nombre del perfume."
        )

    # Limpiar: quitar filas vacías en columna nombre
    df = df.copy()
    df.loc[:, "nombre"] = df["nombre"].str.strip()
    df = df[df["nombre"].notna() & (df["nombre"] != "")]

    # Columnas opcionales con valor por defecto
    for col in ("marca", "precio", "ml"):
        if col not in df.columns:
            df[col] = ""

    df = df.reset_index(drop=True)
    logger.success(f"{len(df)} perfumes cargados.")
    return df


# ─────────────────────────────────────────────
#   CACHÉ DE PERFUMES YA PROCESADOS
# ─────────────────────────────────────────────

def _cargar_cache() -> set:
    """Retorna un set con los nombres de perfumes ya procesados."""
    if not CACHE_FILE.exists():
        return set()
    df_cache = pd.read_csv(CACHE_FILE, dtype=str, encoding="utf-8-sig")
    if "nombre" not in df_cache.columns:
        return set()
    return set(df_cache["nombre"].str.strip().str.lower().dropna())


def _a_str(val) -> str:
    """Convierte notas u ocasiones a string (la IA puede devolver dicts)."""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return str(val.get("name", val.get("nota", val.get("nombre", str(val)))))
    return str(val)


def _join_notas(items: list) -> str:
    """Une lista de notas (acepta strings o dicts)."""
    return "|".join(_a_str(x) for x in (items or []))


def _guardar_en_cache(resultado: dict):
    """
    Agrega un perfume al archivo de caché CSV después de extraerlo con IA.
    Recibe el dict retornado por modulo_b_ia_extractor.scrape_perfume().
    """
    notas = resultado.get("notas", {}) or {}
    ocasiones = resultado.get("ocasiones_de_uso", []) or []
    nueva_fila = {
        "nombre":          resultado.get("nombre", ""),
        "url":             resultado.get("url", ""),
        "notas_salida":    _join_notas(notas.get("salida", [])),
        "notas_corazon":   _join_notas(notas.get("corazon", [])),
        "notas_fondo":     _join_notas(notas.get("fondo", [])),
        "clima_primavera": resultado.get("clima", {}).get("primavera", 0),
        "clima_verano":    resultado.get("clima", {}).get("verano", 0),
        "clima_otono":     resultado.get("clima", {}).get("otono", 0),
        "clima_invierno":  resultado.get("clima", {}).get("invierno", 0),
        "clima_dia":       resultado.get("clima", {}).get("dia", 0),
        "clima_noche":     resultado.get("clima", {}).get("noche", 0),
        "genero":          resultado.get("genero", ""),
        "descripcion":     resultado.get("descripcion_corta", ""),
        "ocasiones":       _join_notas(ocasiones),
        "imagen_path":     str(resultado.get("imagen_path") or ""),
    }

    df_fila = pd.DataFrame([nueva_fila])

    if CACHE_FILE.exists():
        df_fila.to_csv(CACHE_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df_fila.to_csv(CACHE_FILE, mode="w", header=True, index=False, encoding="utf-8-sig")

    logger.debug(f"Guardado en caché: {nueva_fila['nombre']}")


def cargar_desde_cache(nombre: str) -> dict | None:
    """
    Busca un perfume en el caché y retorna sus datos si existen.
    Útil para reconstruir el catálogo sin re-scrapear.
    """
    if not CACHE_FILE.exists():
        return None

    df = pd.read_csv(CACHE_FILE, dtype=str, encoding="utf-8-sig")
    df = df.copy()
    df.loc[:, "nombre_lower"] = df["nombre"].str.strip().str.lower()
    fila = df[df["nombre_lower"] == nombre.strip().lower()]

    if fila.empty:
        return None

    f = fila.iloc[0]
    img_val = f.get("imagen_path")
    img_path = Path(img_val) if (pd.notna(img_val) and str(img_val).strip()) else None

    return {
        "nombre":  f["nombre"],
        "url":     f.get("url", ""),
        "notas": {
            "salida":   f.get("notas_salida", "").split("|") if (pd.notna(f.get("notas_salida")) and f.get("notas_salida")) else [],
            "corazon":  f.get("notas_corazon", "").split("|") if (pd.notna(f.get("notas_corazon")) and f.get("notas_corazon")) else [],
            "fondo":    f.get("notas_fondo", "").split("|") if (pd.notna(f.get("notas_fondo")) and f.get("notas_fondo")) else [],
        },
        "clima": {
            "primavera": int(f.get("clima_primavera", 0) if pd.notna(f.get("clima_primavera")) else 0),
            "verano":    int(f.get("clima_verano", 0) if pd.notna(f.get("clima_verano")) else 0),
            "otono":     int(f.get("clima_otono", 0) if pd.notna(f.get("clima_otono")) else 0),
            "invierno":  int(f.get("clima_invierno", 0) if pd.notna(f.get("clima_invierno")) else 0),
            "dia":       int(f.get("clima_dia", 0) if pd.notna(f.get("clima_dia")) else 0),
            "noche":     int(f.get("clima_noche", 0) if pd.notna(f.get("clima_noche")) else 0),
        },
        "genero":      f.get("genero", "Unisex"),
        "descripcion": f.get("descripcion", ""),
        "ocasiones":   f.get("ocasiones", "").split("|") if (pd.notna(f.get("ocasiones")) and f.get("ocasiones")) else [],
        "imagen_path": img_path,
        "ya_procesado": True,
    }


# ─────────────────────────────────────────────
#   ITERADOR PRINCIPAL
# ─────────────────────────────────────────────

def obtener_perfumes_pendientes(df: pd.DataFrame) -> list[dict]:
    """
    Filtra la lista de perfumes y retorna solo los que aún no han
    sido scrapeados. También retorna los datos en caché para los
    que ya están listos.

    Retorna
    -------
    pendientes : list[dict]
        Lista de dicts con claves: nombre, marca, precio, ml, estado
        estado puede ser 'pendiente' o 'en_cache'
    """
    cache = _cargar_cache()
    pendientes = []
    en_cache = []

    for _, fila in df.iterrows():
        nombre = fila["nombre"]
        info = {
            "nombre": nombre,
            "marca":  fila.get("marca", ""),
            "precio": fila.get("precio", ""),
            "ml":     fila.get("ml", ""),
        }

        if nombre.strip().lower() in cache:
            info["estado"] = "en_cache"
            en_cache.append(info)
            logger.debug(f"[CACHE] En caché: {nombre}")
        else:
            info["estado"] = "pendiente"
            pendientes.append(info)

    logger.info(
        f"Resumen: {len(pendientes)} pendientes | {len(en_cache)} en caché"
    )
    return pendientes + en_cache  # Los pendientes van primero


# ─────────────────────────────────────────────
#   PRUEBA STAND-ALONE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Busca cualquier archivo de lista en /data/
    archivos = list(DATA_DIR.glob("*.xlsx")) + list(DATA_DIR.glob("*.csv"))

    if not archivos:
        print(f"No se encontraron archivos en {DATA_DIR}")
        print("Coloca tu lista de perfumes (lista_perfumes.xlsx o .csv) en la carpeta /data/")
    else:
        ruta = archivos[0]
        df = cargar_lista(ruta)
        print(df[["nombre", "marca", "precio", "ml"]].to_string(index=True))

        perfumes = obtener_perfumes_pendientes(df)
        pendientes = [p for p in perfumes if p["estado"] == "pendiente"]
        print(f"\n[OK] {len(pendientes)} perfumes listos para scrapear.")
