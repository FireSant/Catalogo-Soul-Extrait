#!/usr/bin/env python3
"""
Verificación completa de búsqueda de imágenes.
Prueba diferentes casos para confirmar que la corrección funciona.
"""

from modulo_d_pdf import encontrar_imagen_perfume

def probar_casos():
    """Probar varios casos de búsqueda."""
    casos = [
        # (nombre, marca, genero, descripcion)
        ("Y", "YSL", "mujer", "Y + YSL debería encontrar Y_YSL.jpg"),
        ("Y", "", "", "Y sin marca (fallback)"),
        ("CK", "One", "unisex", "CK + One debería encontrar CK_One.jpg"),
        ("X", "YSL", "mujer", "X + YSL (fuzzy matching)"),
        ("Bad Boy", "", "hombre", "Bad Boy debería encontrar bad_boy.jpg"),
        ("Light Blue", "Dolce & Gabbana", "mujer", "Light Blue mujer -> Light_blue_mujer.png"),
    ]

    print("=" * 60)
    print("VERIFICACIÓN DE BÚSQUEDA DE IMÁGENES")
    print("=" * 60)

    for nombre, marca, genero, descripcion in casos:
        resultado = encontrar_imagen_perfume(nombre, marca, genero, 'imagenes_temp')
        if resultado:
            print(f"✓ {descripcion}")
            print(f"  → {resultado.name}")
        else:
            print(f"✗ {descripcion}")
            print(f"  → No encontrado")
        print()

if __name__ == "__main__":
    probar_casos()
