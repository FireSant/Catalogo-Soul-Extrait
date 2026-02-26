"""
Módulo de utilidades para generar descripciones variadas de perfumes.
"""

import random

# Plantillas de descripción por tipo de fragancia - AMPLIADAS y MEJOR ESTRUCTURADAS
DESCRIPCIONES_TEMPLATES = {
    "citrico": [
        "Una explosión cítrica vibrante que despierta los sentidos con su frescura radiante.",
        "Apertura cítrica chispeante que baila sobre la piel con alegría luminosa.",
        "Fragancia cítrica cristalina que evoca mañanas soleadas y aire libre.",
        "Composición fresca y revitalizante donde los cítricos brillan con pureza.",
        "Esencias de frutas cítricas que crean una estela luminosa y optimista.",
        "Vértigo de cítricos jugosos que se funden en una sinfonía de luz y energía.",
        "Aroma de primavera en frasco, donde limón, bergamota y naranja dialogan en perfecta armonía.",
        "Chispa de sol capturada: cítricos brillantes que iluminan el día con su presencia.",
        "Frescura instantánea que transporta a jardines mediterráneos en pleno esplendor.",
        "Esencias doradas de frutas cítricas que bailan con vitalidad sobre la piel.",
    ],
    "floral": [
        "Un ramillete floral exuberante que envuelve en elegancia atemporal.",
        "Poesía floral en cada nota, con pétalos que se despliegan con suavidad.",
        "Jardín en flor capturado en frasco, con flores que se abren lentamente.",
        "Composición floral sofisticada que celebra la belleza de la naturaleza.",
        "Aroma floral delicado pero persistente, como un bouquet recién cortado.",
        "Coro de flores en perfecta sintonía: rosas, jazmines y violetas tejen una historia de amor.",
        "Atardecer en un jardín de rosas, donde cada nota es un pétalo que se despliega con gracia.",
        "Bouquet de flores silvestres que captura la esencia de la primavera en su máximo esplendor.",
        "Lirio, gardenia y magnolia se entrelazan en una danza floral de elegancia incomparable.",
        "Poema olfativo dedicado a la belleza efímera de las flores en su momento perfecto.",
    ],
    "amaderado": [
        "Calidez amaderada que se funde con la piel creando una estela sofisticada.",
        "Profundidad de maderas nobles que evocan bosques ancestrales.",
        "Estructura amaderada intensa, con vetas de sándalo y cedro.",
        "Fragancia de maderas preciosas que se desarrolla con elegancia.",
        "Acordes terrosos y ahumados que recuerdan a talleres de ebanistería.",
        "Sándalo, cedro y vetiver se entrelazan como raíces que se hunden en la tierra firme.",
        "Calor de hogar: maderas nobles que envuelven en confort y distinción.",
        "Bosque lluvioso en otoño: hojas secas, madera húmeda y tierra fértil en cada inhalación.",
        "Esencias de árboles centenarios que cuentan historias con su aroma profundo y sereno.",
        "Taller de ebanista: virutas de sándalo, cedro pulido y un toque de cuero envejecido.",
    ],
    "gourmand": [
        "Delicia gourmand que envuelve en una nube de dulzura tentadora.",
        "Postre en frasco: notas dulces que despiertan recuerdos de infancia.",
        "Fragancia comestible que huele a repostería fina y tentación.",
        "Calidez azucarada que se adhiere a la piel como un abrazo.",
        "Composición golosa donde la vainilla y el caramelo reinan.",
        "Pastelería francesa en frasco: praliné, chocolate y crema pastelera se funden en tentación.",
        "Dulce de leche y canela: aroma que evoca meriendas de la abuela y momentos de felicidad.",
        "Café recién molido con toques de chocolate y avellanas: el desayuno de los dioses.",
        "Helado de vainilla con caramelo salado: frescura dulce que perdura en la piel.",
        "Mermelada de frutas rojas y merengue: ligereza azucarada que alegra el espíritu.",
    ],
    "especiado": [
        "Baile de especias exóticas que calientan y estimulan los sentidos.",
        "Viaje olfativo a mercados lejanos con pimienta, canela y clavo.",
        "Aroma especiado que se entrelaza con la piel de forma seductora.",
        "Composición picante y cálida que no deja indiferente.",
        "Especias raras y preciosas en un elixir de carácter fuerte.",
        "Bazar de Oriente: cardamomo, pimienta rosa y azafrán tejen una trama cautivadora.",
        "Pimienta negra y jengibre se encienden en la piel como una chispa de energía.",
        "Canela y clavo de olor: especias de invierno que abrazan con su calor reconfortante.",
        "Ruta de las especias: pimienta de Sichuan, nuez moscada y cilantro en aventura olfativa.",
        "Mercado de especias al atardecer: el aire huele a historia, misterio y sensualidad.",
    ],
    "oriental": [
        "Misterio oriental con notas ricas y embriagadoras.",
        "Opulencia de ámbar y almizcle en una composición seductora.",
        "Fragancia de ensueño que evoca palacios y noches exóticas.",
        "Calidez envolvente con matices ambarados y balsámicos.",
        "Elixir sensual que se adhiere a la piel como un segundo aroma.",
        "Noche en el desierto: ámbar, oud y mirra bajo un manto de estrellas.",
        "Palacio de las mil y una noches: cortinas de terciopelo, incienso y misterio.",
        "Opulencia barroca: resinas preciosas, bálsamos y un toque de animalidad refinada.",
        "Seda y especias: fragancia que se desliza sobre la piel como un vestido de noche.",
        "Templo lejano: incienso quemándose, ámbar gris y un eco de lejanos cánticos sagrados.",
    ],
    "acuatico": [
        "Ola fresca que transporta a costas mediterráneas y mares cristalinos.",
        "Fragancia acuática que huele a sal, algas y libertad.",
        "Apertura marina con notas saladas y verdes que refrescan.",
        "Composición húmeda y transparente como el agua de manantial.",
        "Brisa oceánica capturada en frasco con toques de yodo y espuma.",
        "Primer chapuzón del verano: agua fría, piel mojada y sol brillando sobre las olas.",
        "Arrecife de coral: notas marinas, algas verdes y el rumor lejano de la marea.",
        "Puerto al amanecer: redes de pesca, madera húmeda y la promesa de aventura.",
        "Lluvia tropical en selva: gotas sobre hojas grandes, tierra mojada y purificación.",
        "Marea baja en playa desierta: conchas, arena húmeda y el infinito horizonte azul.",
    ],
    "cuero": [
        "Aroma a cuero nuevo y pulido, elegante y rebelde a la vez.",
        "Notas de piel curtida que evocan lujo y distinción.",
        "Fragancia con carácter, donde el cuero es el protagonista absoluto.",
        "Composición ahumada y animal que recuerda a un automóvil de lujo.",
        "Cuero fino y tabaco en una mezcla de sofisticación ruda.",
        "Guante de boxeo antiguo: cuero encerado, sudor seco y determinación.",
        "Interior de automóvil clásico: cuero tostado, madera noble y un toque de gasolina.",
        "Silla de montar curtida: cuero bronceado por el sol, tabaco y campo abierto.",
        "Biblioteca victoriana: libros antiguos, cuero oscuro y el olor a madera de roble.",
        "Club de caballeros: pipa, cuero y brandy en ambiente de conversaciones serias.",
    ],
    "verde": [
        "Hojas verdes crujientes y brotes frescos que huelen a primavera.",
        "Fragancia herbácea que recuerda a prados recién cortados.",
        "Aroma de naturaleza viva: hierbas, tallos y savia.",
        "Composición verde y crujiente como un jardín después de la lluvia.",
        "Notas de vegetación fresca que purifican el aire y el espíritu.",
        "Prado recién segado: hierba fresca, trébol y el olor a tierra mojada.",
        "Bosque de hayas en primavera: brotes tiernos, savia y luz filtrándose entre hojas.",
        "Jardín botánico al amanecer: rocío en hojas, tallos verdes y pureza absoluta.",
        "Hierbabuena y albahaca: huerto familiar donde la vida brota con fuerza renovada.",
        "Camino de montaña: pino joven, helechos y el aliento fresco del amanecer.",
    ],
    "frutal": [
        "Cesta de frutas maduras y jugosas que estallan en frescura.",
        "Fragancia frutal que huele a verano y días de picnic.",
        "Dulzura natural de frutas del bosque y frutas exóticas.",
        "Composición afrutada que alegra el ánimo con su optimismo.",
        "Néctar de frutas en cada nota, desde cítricos hasta bayas.",
        "Mercado de frutas tropicales: mango, papaya y maracuyá en explosión de jugosidad.",
        "Tarta de frutas del bosque: frambuesas, fresas y arándanos en armonía dulce.",
        "Sorbete de frutas rojas: ligereza, frescura y un toque de azúcar glas.",
        "Huerto familiar en verano: melocotón maduro, pera jugosa y albaricoque soleado.",
        "Cóctel de frutas exóticas: lichi, mango y maracuyá bailando en perfecta sincronía.",
    ],
    "aromatico": [
        "Hierbas aromáticas que se entrelazan en una sinfonía fresca.",
        "Fragancia de campo de lavanda y romero al atardecer.",
        "Composición herbácea con un toque medicinal y refrescante.",
        "Aroma a plantas silvestres y especias del jardín.",
        "Esencia de hierbas frescas cortadas con el rocío de la mañana.",
        "Prado de hierbas medicinales: tomillo, salvia y menta en armonía natural.",
        "Jardín de hierbas provenzales: lavanda, romero y tomillo bajo el sol del mediodía.",
        "Infusión de hierbas frescas: manzanilla, hierbabuena y un toque de miel.",
        "Camino de montaña: tomillo silvestre, romero y el aire puro de las alturas.",
        "Botica antigua: hierbas secas, raíces y el saber de generaciones de curanderos.",
    ],
}

# Adjetivos variados para mezclar
ADJETIVOS_VARIADOS = [
    "vibrante", "sofisticada", "misteriosa", "sensual", "clásica", "moderna",
    "audaz", "delicada", "fuerte", "sutil", "opulenta", "minimalista",
    "energizante", "relajante", "embriagadora", "refrescante", "cálida",
    "etérea", "terrosa", "líquida", "ahumada", "dulce", "seca",
    "afrutada", "floral", "amaderada", "especiada", "gourmand", "mineral"
]

# Verbos de acción para descripciones
VERBOS_ACCION = [
    "despierta", "envuelve", "transporta", "sorprende", "conquista",
    "evoca", "recuerda", "invita", "seduce", "fascina", "hipnotiza"
]

# Sustantivos poéticos
SUSTANTIVOS_POETICOS = [
    "poema", "canción", "viaje", "sueño", "recuerdo", "instante",
    "abrazo", "susurro", "destello", "huella", "constelación"
]


def generar_descripcion_variada(notas: dict, genero: str, familia: str) -> str:
    """
    Genera una descripción variada basada en las notas y características del perfume.

    Args:
        notas: Dict con notas de salida, corazón y fondo
        genero: "Hombre", "Mujer" o "Unisex"
        familia: Familia olfativa (Cítrico, Floral, etc.)

    Returns:
        Descripción única y variada
    """
    # Determinar el tipo principal basado en la familia
    tipo_principal = familia.lower() if familia else "floral"

    # Mapear familias a categorías de plantillas
    categoria = "floral"  # por defecto
    for key in DESCRIPCIONES_TEMPLATES.keys():
        if key in tipo_principal:
            categoria = key
            break

    # Si no se encuentra, usar la familia como está o default
    if categoria not in DESCRIPCIONES_TEMPLATES:
        categoria = "floral"

    # Obtener plantillas de la categoría
    plantillas = DESCRIPCIONES_TEMPLATES[categoria]

    # Seleccionar una plantilla aleatoria
    plantilla = random.choice(plantillas)

    # Añadir variación extra mezclando adjetivos
    if random.random() < 0.3:
        adj = random.choice(ADJETIVOS_VARIADOS)
        # Insertar adjetivo en un lugar aleatorio
        palabras = plantilla.split()
        if len(palabras) > 3:
            idx = random.randint(1, len(palabras) - 2)
            palabras.insert(idx, adj)
            plantilla = " ".join(palabras)

    # Añadir un toque de las notas principales
    notas_principales = []
    if notas.get("salida"):
        notas_principales.extend(notas["salida"][:2])
    if notas.get("fondo"):
        notas_principales.extend(notas["fondo"][:1])

    if notas_principales and random.random() < 0.4:
        nota_ejemplo = random.choice(notas_principales)
        # Añadir al final o integrado
        if plantilla.endswith("."):
            plantilla = plantilla[:-1] + f", con toques de {nota_ejemplo}."

    return plantilla


def mezclar_descripciones(desc1: str, desc2: str) -> str:
    """
    Mezcla dos descripciones para crear una tercera única.
    """
    if not desc1 or not desc2:
        return desc1 or desc2

    # Dividir en frases
    frases1 = desc1.split(". ")
    frases2 = desc2.split(". ")

    # Tomar partes de cada una
    resultado = []
    if frases1:
        resultado.append(frases1[0])
    if frases2 and len(frases2) > 1:
        resultado.append(frases2[-1])

    return ". ".join(resultado) + "."


if __name__ == "__main__":
    # Prueba
    notas_test = {
        "salida": ["Bergamota", "Limón"],
        "corazon": ["Rosa", "Jazmín"],
        "fondo": ["Vainilla", "Sándalo"]
    }
    for i in range(5):
        print(f"{i+1}. {generar_descripcion_variada(notas_test, 'Hombre', 'Cítrico')}")
