"""Escribe con palabras los numeros de un texto, para que el TTS no los lea mal.

Se ejecuta antes de las reglas de acento: aqui se escribe en espanol normal
("cinco", "ciento") y las reglas luego lo pasan a "sinco", "siento".

Convenciones: punto = miles (1.500), coma = decimal (3,5), fechas
dia-mes-ano (20-10-2026), $ = pesos. Es lo habitual en Chile, Argentina,
Colombia y gran parte de Sudamerica; en Mexico y Centroamerica el punto es
decimal, asi que conviene escribir "3,5" o "tres punto cinco" a mano.
Lo que no convierte lo deja tal cual y lo informa para revisarlo a mano:
codigos con letras y numeros pegados (IP67, M12, 4610D) y numeros terminados
en 1 antes de una palabra (el
script no sabe si va "un" o "una": "1 clase" debe escribirse "una clase").
"""

import re

UNIDADES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
            "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete",
            "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidós", "veintitrés",
            "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"]
DECENAS = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta",
           8: "ochenta", 9: "noventa"}
CENTENAS = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos",
            6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
ORDINALES = ["", "primer", "segund", "tercer", "cuart", "quint", "sext", "séptim", "octav",
             "noven", "décim"]

# Unidad: (singular, plural, femenino). Ajustar aqui si en el audio suena mejor otra forma.
UNIDADES_MEDIDA = {
    "%": ("por ciento", "por ciento", False),
    "°C": ("grado Celsius", "grados Celsius", False),
    "°": ("grado", "grados", False),
    "mm/s": ("milímetro por segundo", "milímetros por segundo", False),
    "m/s": ("metro por segundo", "metros por segundo", False),
    "km/h": ("kilómetro por hora", "kilómetros por hora", False),
    "mm": ("milímetro", "milímetros", False),
    "cm": ("centímetro", "centímetros", False),
    "km": ("kilómetro", "kilómetros", False),
    "m": ("metro", "metros", False),
    "kg": ("kilo", "kilos", False),
    "mg": ("miligramo", "miligramos", False),
    "g": ("gramo", "gramos", False),
    "ml": ("mililitro", "mililitros", False),
    "l": ("litro", "litros", False),
    "L": ("litro", "litros", False),
    "lb": ("libra", "libras", True),
    "oz": ("onza", "onzas", True),
    "m²": ("metro cuadrado", "metros cuadrados", False),
    "m2": ("metro cuadrado", "metros cuadrados", False),
    "km²": ("kilómetro cuadrado", "kilómetros cuadrados", False),
    "m³": ("metro cúbico", "metros cúbicos", False),
    "m3": ("metro cúbico", "metros cúbicos", False),
    "°F": ("grado Fahrenheit", "grados Fahrenheit", False),
    "Hz": ("hertz", "hertz", False),
    "kHz": ("kilohertz", "kilohertz", False),
    "MHz": ("megahertz", "megahertz", False),
    "GHz": ("gigahertz", "gigahertz", False),
    "rpm": ("revolución por minuto", "revoluciones por minuto", True),
    "ms": ("milisegundo", "milisegundos", False),
    "min": ("minuto", "minutos", False),
    "seg": ("segundo", "segundos", False),
    "hrs": ("hora", "horas", True),
    "hr": ("hora", "horas", True),
    "h": ("hora", "horas", True),
    "V": ("volt", "volts", False),
    "kV": ("kilovolt", "kilovolts", False),
    "W": ("watt", "watts", False),
    "kW": ("kilowatt", "kilowatts", False),
    "kWh": ("kilowatt hora", "kilowatts hora", False),
    "dB": ("decibel", "decibeles", False),
    "MB": ("megabait", "megabaits", False),
    "GB": ("gigabait", "gigabaits", False),
    "TB": ("terabait", "terabaits", False),
}
MONEDAS = {"US$": ("dólar", "dólares"), "$": ("peso", "pesos")}

LETRA = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
_UNIDAD_RE = "|".join(re.escape(u) for u in sorted(UNIDADES_MEDIDA, key=len, reverse=True))
_MONEDA_RE = "|".join(re.escape(m) for m in sorted(MONEDAS, key=len, reverse=True))

ROMANO_VALIDO = re.compile(r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})")
VALOR_ROMANO = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
# Romanos que se leen como numero solo despues de estas palabras: "siglo XXI".
ROMANO_CONTEXTO = re.compile(
    r"(?<![\w])((?:[Ss]iglos?|[Cc]ap[íi]tulos?|[Tt]omos?|[Vv]ol[úu]men(?:es)?|[Pp]artes?|[Ff]ases?"
    r"|[Nn]iveles?|[Aa]ctos?|[Ll]ibros?|[Tt][íi]tulos?|[Uu]nidad(?:es)?|[Mm][óo]dulos?|[Ll]ecci[óo]n)\s+)"
    r"([IVXLCDM]+)(?![\w])")
TELEFONO = re.compile(r"(?<![\w+])\+\d{1,3}(?:[\s-]?\d{1,4}){2,5}(?!\d)")
VERSION = re.compile(r"(?<![\d.,\w])(v)?(\d+(?:\.\d+){2,})(?![\d]|\.\d)")
NUMERO_SIGNO = re.compile(r"(?<![\w])[Nn](?:°|º|\.º|ro\.?)\s?(?=\d)")
ORD_ABREV = re.compile(r"(?<![\d\w])(\d{1,2})\.?(er|era|ero|ra|ro|do|da|to|ta|vo|va|no|na|mo|ma)(?![\w])")
FRACCION = re.compile(r"(?<![\d/.,])([1-3])/([2-4])(?![\d/])")
FRACCIONES = {(1, 2): "medio", (1, 3): "un tercio", (2, 3): "dos tercios",
              (1, 4): "un cuarto", (3, 4): "tres cuartos"}
DECADA = re.compile(r"(?<![\w])([1-9]0)'?s(?![\w])")
MAS = re.compile(r"(?<=\d)\s?\+\s?(?=\d)")
POR = re.compile(r"(?<=\d)\s?[x×]\s?(?=\d)")
IGUAL = re.compile(r"(?<=\s)=(?=\s)")
FECHA = re.compile(r"(?<![\d.,/-])(\d{1,2})[-/](\d{1,2})[-/](\d{4})(?![\d/-])")
HORA = re.compile(r"(?<![\d.,:])([01]?\d|2[0-3]):([0-5]\d)(?![\d:])"
                  r"(?P<suf>\s?(?:hrs?|horas|h)(?![\w]))?")
RANGO = re.compile(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+|\d+)\s?-\s?(?=\d)")
# Solo º y ª son ordinales (1º, 2ª); el signo ° se lee como grados.
ORDINAL = re.compile(rf"(?<![\d{LETRA}])(\d{{1,2}})\s?([ºª])")
NUMERO = re.compile(
    rf"(?:(?P<moneda>{_MONEDA_RE})\s?)?"
    rf"(?<![\d.,{LETRA}])(?P<signo>-)?(?<!\w-)(?P<entero>\d{{1,3}}(?:\.\d{{3}})+|\d+)"
    r"(?:(?P<sep>[.,])(?P<decimal>\d+))?"
    rf"(?:\s?(?P<unidad>{_UNIDAD_RE}))?"
    rf"(?![\d{LETRA}])"
)
SIGLA_ANTES = re.compile(r"(?<![\w])[A-Z][A-Z0-9]+[\s-]?$")
PALABRA_DESPUES = re.compile(rf"\s+([{LETRA}]+)")
# Despues de estas palabras no va apocope: "1 y 2", "1 de octubre".
SIN_APOCOPE = {"y", "o", "u", "e", "a", "al", "de", "del", "en", "con", "por", "para", "es",
               "son", "más", "menos", "que", "se", "sin", "hasta", "desde", "entre", "como",
               "el", "la", "los", "las", "lo", "le", "les", "un", "una", "unos", "unas", "mi",
               "tu", "su", "no", "ni", "pero", "sino", "cuando", "donde", "ya", "vs", "contra",
               "ante", "bajo", "tras", "sobre", "según", "durante", "hacia", "fue", "era", "está",
               "estaba", "ha", "había", "va", "iba", "ganó", "perdió", "empató", "veces"}
CODIGO = re.compile(rf"(?<![\w-])(?=[\w-]*\d)(?=[\w-]*[{LETRA}])[\w-]+")


def cardinal(n, apocope=False, femenino=False):
    """0 <= n < 10**18. apocope: uno -> un (antes de un sustantivo masculino)."""
    if n < 30:
        palabra = UNIDADES[n]
    elif n < 100:
        palabra = DECENAS[n // 10] + ("" if n % 10 == 0 else " y " + UNIDADES[n % 10])
    elif n < 1000:
        if n == 100:
            palabra = "cien"
        else:
            resto = n % 100
            palabra = CENTENAS[n // 100] + ("" if resto == 0 else " " + cardinal(resto))
    elif n < 10**6:
        miles, resto = divmod(n, 1000)
        palabra = "mil" if miles == 1 else cardinal(miles, apocope=True, femenino=femenino) + " mil"
        return palabra + (" " + cardinal(resto, apocope, femenino) if resto else "")
    elif n >= 10**12:
        billones, resto = divmod(n, 10**12)
        palabra = ("un billón" if billones == 1
                   else cardinal(billones, apocope=True) + " billones")
        return palabra + (" " + cardinal(resto, apocope, femenino) if resto else "")
    else:
        millones, resto = divmod(n, 10**6)
        palabra = ("un millón" if millones == 1
                   else cardinal(millones, apocope=True) + " millones")
        return palabra + (" " + cardinal(resto, apocope, femenino) if resto else "")
    if femenino:
        palabra = re.sub(r"ientos\b", "ientas", palabra)    # quinientas revoluciones
        return re.sub(r"(uno|veintiuno)$", lambda m: m.group(1)[:-1] + "a", palabra)
    if apocope:
        return re.sub(r"veintiuno$", "veintiún", re.sub(r"(?<!veinti)uno$", "un", palabra))
    return palabra


def valor_romano(rom):
    total = 0
    for i, letra in enumerate(rom):
        valor = VALOR_ROMANO[letra]
        siguiente = VALOR_ROMANO[rom[i + 1]] if i + 1 < len(rom) else 0
        total += -valor if valor < siguiente else valor
    return total


def cifras(texto):
    """Lee digito por digito: 007 -> cero cero siete."""
    return " ".join(UNIDADES[int(d)] for d in texto)


def decimales(texto):
    ceros = len(texto) - len(texto.lstrip("0"))
    resto = texto[ceros:]
    partes = ["cero"] * ceros + ([cardinal(int(resto))] if resto and len(resto) <= 3 else
                                 [cifras(resto)] if resto else [])
    return " ".join(partes)


def convertir(texto, conocidas=()):
    """Devuelve (texto con numeros escritos, lista de avisos para revisar).
    conocidas: claves de excepciones_voz.txt (en minuscula) que no se avisan."""
    avisos = []

    def fecha(m):
        dia, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (1 <= dia <= 31 and 1 <= mes <= 12):
            return m.group(0)
        return f"{cardinal(dia)} de {MESES[mes - 1]} de {cardinal(ano)}"

    def romano(m):
        rom = m.group(2)
        if not ROMANO_VALIDO.fullmatch(rom):
            return m.group(0)
        return m.group(1) + cardinal(valor_romano(rom))

    def telefono(m):
        grupos = re.split(r"[\s-]+", m.group(0)[1:])
        return "más " + ", ".join(cifras(g) for g in grupos)

    def version(m):
        partes = m.group(2).split(".")
        if len(partes[0]) <= 3 and all(len(p) == 3 for p in partes[1:]) and not m.group(1):
            return m.group(0)                       # 1.000.000 son miles, no una version
        return ("versión " if m.group(1) else "") + " punto ".join(
            cardinal(int(p)) if len(p) <= 15 else cifras(p) for p in partes)

    def ord_abrev(m):
        n, suf = int(m.group(1)), m.group(2)
        if not 1 <= n <= 10:
            avisos.append(f"{m.group(0)}: ordinal sin convertir, escribirlo con palabras")
            return m.group(0)
        if suf == "er":
            # "1er lugar" -> primer lugar; "quedo 1er en la tabla" -> primero
            siguiente = PALABRA_DESPUES.match(m.string, m.end())
            antes_de_sustantivo = siguiente and siguiente.group(1).lower() not in SIN_APOCOPE
            return ORDINALES[n] + ("" if n in (1, 3) and antes_de_sustantivo else "o")
        return ORDINALES[n] + ("a" if suf.endswith("a") else "o")

    def fraccion(m):
        a, b = int(m.group(1)), int(m.group(2))
        if (a, b) not in FRACCIONES:
            return m.group(0)
        palabras = FRACCIONES[(a, b)]
        siguiente = PALABRA_DESPUES.match(m.string, m.end())
        if (a, b) == (1, 2) and siguiente:
            avisos.append(f"{m.group(0)} {siguiente.group(1)}: se leyo 'medio'; "
                          "si la palabra es femenina escribir 'media'")
        return palabras

    def hora(m):
        h, mi = int(m.group(1)), int(m.group(2))
        if m.group("suf"):
            return cardinal(h) + ("" if mi == 0 else " " + cardinal(mi)) + " horas"
        if mi == 0:
            ya_dice = m.string[m.end():m.end() + 9].lower().startswith(" en punto")
            return cardinal(h) + ("" if ya_dice else " en punto")
        return f"{cardinal(h)} {cardinal(mi) if mi >= 10 else 'cero ' + cardinal(mi)}"

    def ordinal(m):
        n, marca = int(m.group(1)), m.group(2)
        if not 1 <= n <= 10:
            avisos.append(f"{m.group(0)}: ordinal sin convertir, escribirlo con palabras")
            return m.group(0)
        if marca == "ª":
            return ORDINALES[n] + "a"
        siguiente = PALABRA_DESPUES.match(m.string, m.end())
        if n in (1, 3) and siguiente and siguiente.group(1).lower() not in SIN_APOCOPE:
            return ORDINALES[n]                     # primer lugar, tercer modulo
        return ORDINALES[n] + "o"

    def numero(m):
        entero_txt = m.group("entero").replace(".", "")
        unidad, moneda = m.group("unidad"), m.group("moneda")
        sep, dec = m.group("sep"), m.group("decimal")
        # "3.5" es decimal; "1.500" ya se tomo como miles en el patron. Una cifra
        # larga sin puntos suele ser un identificador: se lee digito por digito.
        con_puntos = "." in m.group("entero")
        por_cifras = (len(entero_txt) > (18 if con_puntos else 15)
                      or (len(entero_txt) > 1 and entero_txt.startswith("0")))
        if por_cifras:
            palabras = cifras(entero_txt)
        else:
            n = int(entero_txt)
            siguiente = PALABRA_DESPUES.match(m.string, m.end())
            sigue_palabra = (not unidad and not dec and not moneda and siguiente
                             and siguiente.group(1).lower() not in SIN_APOCOPE)
            fem = bool(unidad) and UNIDADES_MEDIDA[unidad][2]
            apoc = (bool(unidad) and not fem and unidad != "%") or bool(moneda) or bool(sigue_palabra)
            if dec:
                fem = apoc = False
            palabras = cardinal(n, apocope=apoc, femenino=fem)
            if sigue_palabra and n % 10 == 1 and n % 100 != 11:
                avisos.append(f"{m.group('entero')} {siguiente.group(1)}: se leyo '{palabras}'; "
                              "si la palabra es femenina escribir 'una'")
        if dec:
            palabras += (" coma " if sep == "," else " punto ") + decimales(dec)
        if m.group("signo"):
            palabras = "menos " + palabras
        uno = not dec and entero_txt.lstrip("0") == "1"
        millones_justos = (not dec and not por_cifras and len(entero_txt) >= 7
                           and int(entero_txt) % 10**6 == 0)
        if (unidad or moneda) and millones_justos and unidad != "%":
            palabras += " de"                       # un millon de pesos
        if unidad:
            sing, plur, _ = UNIDADES_MEDIDA[unidad]
            palabras += " " + (sing if uno else plur)
        if moneda:
            sing, plur = MONEDAS[moneda]
            palabras += " " + (sing if uno else plur)
        return palabras

    def rango(m):
        previo = m.string[max(0, m.start() - 12):m.start()]
        if SIGLA_ANTES.search(previo):
            return m.group(1) + " guion "           # ISO 20816-3 no es un rango
        return m.group(1) + " a "

    for codigo in CODIGO.findall(texto):
        if (codigo.lower() in conocidas or re.fullmatch(rf"\d+(?:{_UNIDAD_RE})", codigo)
                or ORD_ABREV.fullmatch(codigo) or DECADA.fullmatch(codigo)):
            continue
        avisos.append(f"{codigo}: codigo con letras y numeros, se deja tal cual")
    texto = ROMANO_CONTEXTO.sub(romano, texto)
    texto = TELEFONO.sub(telefono, texto)
    texto = FECHA.sub(fecha, texto)
    texto = HORA.sub(hora, texto)
    texto = VERSION.sub(version, texto)
    texto = NUMERO_SIGNO.sub(lambda m: "Número " if m.group(0)[0] == "N" else "número ", texto)
    texto = ORD_ABREV.sub(ord_abrev, texto)
    texto = FRACCION.sub(fraccion, texto)
    texto = DECADA.sub(lambda m: cardinal(int(m.group(1))), texto)
    texto = MAS.sub(" más ", texto)
    texto = POR.sub(" por ", texto)
    texto = IGUAL.sub("igual a", texto)
    texto = RANGO.sub(rango, texto)
    texto = ORDINAL.sub(ordinal, texto)
    texto = NUMERO.sub(numero, texto)
    return texto, list(dict.fromkeys(avisos))
