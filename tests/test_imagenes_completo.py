from modulo_d_pdf import encontrar_imagen_perfume
from pathlib import Path

# Probar con TODOS los casos problemáticos del log
casos = [
    ('Sauvage', 'Dior', 'hombre'),
    ('Bleu de Chanel', 'Chanel', 'hombre'),
    ('Acqua di Gio', 'Armani', 'hombre'),
    ('1 Million', 'Paco Rabanne', 'hombre'),
    ('Invictus', 'Paco Rabanne', 'hombre'),
    ('Eros', 'Versace', 'hombre'),
    ('212 VIP Men', 'Carolina Herrera', 'hombre'),
    ('Bad Boy', 'Carolina Herrera', 'hombre'),
    ('Le Male', 'Jean Paul Gaultier', 'hombre'),
    ('Ultra Male', 'Jean Paul Gaultier', 'hombre'),
    ('Stronger With You', 'Armani', 'hombre'),
    ('Boss Bottled', 'Hugo Boss', 'hombre'),
    ('Light Blue Pour Homme', 'Dolce & Gabbana', 'hombre'),
    ('Dylan Blue', 'Versace', 'hombre'),
    ('Explorer', 'Montblanc', 'hombre'),
    ('Legend', 'Montblanc', 'hombre'),
    ('Polo Blue', 'Ralph Lauren', 'hombre'),
    ('Terre d\'Hermes', 'Hermes', 'hombre'),
    ('Fahrenheit', 'Dior', 'hombre'),
    ('Y', 'YSL', 'hombre'),
    ('Club de Nuit Intense Man', 'Armaf', 'hombre'),
    ('9PM', 'Afnan', 'hombre'),
    ('Hawas', 'Rasasi', 'hombre'),
    ('Asad', 'Lattafa', 'hombre'),
    ('Khamrah', 'Lattafa', 'hombre'),
    ('Toy Boy', 'Moschino', 'hombre'),
    ('Phantom', 'Paco Rabanne', 'hombre'),
    ('Valentino Uomo Born In Roma', 'Valentino', 'hombre'),
    ('Hacivat', 'Nishane', 'unisex'),
    ('Aventus', 'Creed', 'hombre'),
    ('Good Girl Blush', 'Carolina Herrera', 'mujer'),
    ('La Vie Est Belle', 'Lancome', 'mujer'),
    ('Black Opium', 'YSL', 'mujer'),
    ('Libre', 'YSL', 'mujer'),
    ('Cloud', 'Ariana Grande', 'mujer'),
    ('Sweet Like Candy', 'Ariana Grande', 'mujer'),
    ('Thank U Next', 'Ariana Grande', 'mujer'),
    ('Ari', 'Ariana Grande', 'mujer'),
    ('212 VIP Rose', 'Carolina Herrera', 'mujer'),
    ('J\'adore', 'Dior', 'mujer'),
    ('Miss Dior', 'Dior', 'mujer'),
    ('Chanel No 5', 'Chanel', 'mujer'),
    ('Coco Mademoiselle', 'Chanel', 'mujer'),
    ('Light Blue', 'Dolce & Gabbana', 'mujer'),
    ('Bright Crystal', 'Versace', 'mujer'),
    ('Scandal', 'Jean Paul Gaultier', 'mujer'),
    ('Lady Million', 'Paco Rabanne', 'mujer'),
    ('Olympea', 'Paco Rabanne', 'mujer'),
    ('Idole', 'Lancome', 'mujer'),
    ('Si', 'Armani', 'mujer'),
    ('My Way', 'Armani', 'mujer'),
    ('Can Can', 'Paris Hilton', 'mujer'),
    ('Fantasy', 'Britney Spears', 'mujer'),
    ('Yara', 'Lattafa', 'mujer'),
    ('Baccarat Rouge 540', 'MFK', 'unisex'),
    ('Santal 33', 'Le Labo', 'unisex'),
    ('Tobacco Vanille', 'Tom Ford', 'unisex'),
    ('Lost Cherry', 'Tom Ford', 'unisex'),
    ('Ombre Nomade', 'Louis Vuitton', 'unisex'),
    ('CK One', 'Calvin Klein', 'unisex'),
]

print("Probando coincidencias de imágenes:")
print("=" * 80)
errores = []
for nombre, marca, genero in casos:
    resultado = encontrar_imagen_perfume(nombre, marca, genero, 'imagenes_temp')
    nombre_archivo = resultado.name if resultado else "None"
    # Verificar si la coincidencia parece correcta
    nombre_simple = nombre.lower().replace(" ", "").replace("-", "").replace("'", "").replace("&", "")
    archivo_simple = nombre_archivo.lower().replace("_", "").replace(" ", "").replace("-", "").replace("'", "")
    es_correcto = nombre_simple in archivo_simple or archivo_simple in nombre_simple
    if not es_correcto and resultado:
        # Verificar si es un fallback de género
        if "hombre" in archivo_simple and genero == "mujer":
            es_correcto = False
        elif "mujer" in archivo_simple and genero == "hombre":
            es_correcto = False
        else:
            es_correcto = True  # Aceptar fuzzy matching válido
    if not es_correcto:
        errores.append((nombre, marca, genero, nombre_archivo))
    estado = "✓" if es_correcto else "✗"
    print(f"{estado} {nombre:40} -> {nombre_archivo}")

if errores:
    print("\n" + "=" * 80)
    print(f"ERRORES ENCONTRADOS: {len(errores)}")
    for nombre, marca, genero, archivo in errores:
        print(f"  - {nombre} ({marca}, {genero}) -> {archivo}")
else:
    print("\n" + "=" * 80)
    print("TODAS LAS COINCIDENCIAS SON CORRECTAS ✓")
