"""Reescritura del texto con seseo y yeismo para que un TTS suene latinoamericano.

Orden: 1) se apartan intactos URLs, correos y @menciones, 2) abreviaturas,
3) numeros a palabras (numeros.py), 4) excepciones (siglas, anglicismos,
nombres propios), 5) se apartan siglas cortas, romanos y codigos, 6) reglas
automaticas. Lo apartado y el resultado de una excepcion no se vuelven a tocar.
"""

import re
import unicodedata
from importlib import resources
from pathlib import Path

from . import numeros

E_I = "eiéíEIÉÍ"
LETRA = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"

# Reglas en orden: las de dos letras van antes que las de una.
REGLAS = [
    (re.compile(rf"[xX][cC](?=[{E_I}])"), "ks"),   # excelente -> ekselente
    (re.compile(rf"[cC][cC](?=[{E_I}])"), "ks"),   # acceso -> akseso
    (re.compile(rf"[sS][cC](?=[{E_I}])"), "s"),    # escena -> esena
    (re.compile(rf"[cC](?=[{E_I}])"), "s"),        # proceso -> proseso
    (re.compile(r"[zZ]"), "s"),                    # razon -> rason
    (re.compile(rf"(?<![{LETRA}])[xX]"), "s"),     # xilofono -> silofono
    (re.compile(r"[xX]"), "ks"),                   # proximo -> proksimo
    (re.compile(r"[lL][lL]"), "y"),                # llega -> yega
]
REGLA_QUE = (re.compile(rf"[qQ][uU](?=[{E_I}])"), "k")

PALABRA = re.compile(rf"[{LETRA}0-9&'-]+")
# Marcador interno de lo protegido: el indice va en caracteres privados, sin
# digitos ni letras, para que ninguna regla ni la conversion de numeros lo toque.
MARCA_RE = re.compile("\uE000([\uE100-\uE109]+)\uE001")

_FIN_WEB = r"(?=[.,;:!?)\]»”\"']*(?:\s|$))"
WEB = re.compile(
    rf"(?:https?://|www\.)\S+?{_FIN_WEB}"                           # URLs
    r"|(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"                                 # correos
    r"|(?<![\w@])@\w+"                                               # @menciones
    rf"|(?<![\w@.-])[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|ai|dev|app|edu|gov|cl|mx|ar|co|pe"
    rf"|es|uy|py|bo|ec|ve|cr|gt|hn|sv|ni|pa|do|cu|pr)(?:/\S*?)?{_FIN_WEB}")  # dominios

# Abreviaturas: se escriben completas y luego pasan por las reglas.
ABREVIATURAS = {
    "sr": "señor", "sra": "señora", "srta": "señorita", "sres": "señores", "dr": "doctor",
    "dra": "doctora", "ing": "ingeniero", "lic": "licenciado", "prof": "profesor",
    "profa": "profesora", "etc": "etcétera", "aprox": "aproximadamente", "pág": "página",
    "págs": "páginas", "av": "avenida", "depto": "departamento", "dpto": "departamento",
    "tel": "teléfono", "vs": "versus", "ej": "ejemplo",
}
ABREVIATURA = re.compile(
    rf"(?<![{LETRA}])({'|'.join(sorted(ABREVIATURAS, key=len, reverse=True))})\.(?=[\s,;:)]|$)",
    re.IGNORECASE)
EEUU = re.compile(r"(?<![\w])EE\.\s?UU\.?|(?<![\w])EEUU(?![\w])")
# Siglas cortas o sin vocales (CEO, XML, ONU) y romanos sueltos (XXI, XL):
# las reglas los dejan como estan; se avisan para agregar su lectura.
MAYUSCULAS = re.compile(rf"(?<![{LETRA}0-9])[A-ZÁÉÍÓÚÜÑ]{{2,}}(?![{LETRA}0-9])")
CODIGO = re.compile(rf"(?<![\w-])(?=[\w-]*\d)(?=[\w-]*[{LETRA}])[\w-]+")
INICIO_FRASE = re.compile(r"(?:^|[.!?¿¡:]\s*|\n)\s*$")
CORTAS_CON_Y = {"y", "hoy", "muy", "ley", "rey", "hay", "soy", "doy", "voy", "estoy", "buey"}


def leer_excepciones(texto, origen="excepciones"):
    """Lee lineas 'palabra = lectura' (con # para comentarios) y devuelve un dict."""
    pares = {}
    for n, linea in enumerate(texto.splitlines(), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if "=" not in linea:
            raise ValueError(f"{origen} linea {n}: falta '=' en: {linea}")
        clave, valor = (p.strip() for p in linea.split("=", 1))
        pares[clave] = valor
    return pares


def excepciones_incluidas():
    """Las excepciones que trae el paquete (siglas, anglicismos, nombres)."""
    texto = resources.files("acento_latino").joinpath("excepciones.txt").read_text(encoding="utf-8")
    return leer_excepciones(texto, "excepciones.txt")


def compilar_excepciones(extra=None, solo_extra=False):
    """Une las excepciones del paquete con las del usuario (estas ganan).

    extra: dict {palabra: lectura}, o ruta a un archivo con el mismo formato.
    """
    pares = {} if solo_extra else excepciones_incluidas()
    if isinstance(extra, (str, Path)):
        ruta = Path(extra)
        extra = leer_excepciones(ruta.read_text(encoding="utf-8"), ruta.name)
    if extra:
        claves = {c.lower(): c for c in pares}
        for c, v in extra.items():
            pares.pop(claves.get(c.lower(), c), None)
            pares[c] = v
    # Frases largas primero, para que "machine learning" gane sobre "machine".
    orden = sorted(pares.items(), key=lambda p: len(p[0]), reverse=True)
    return [(_patron(c), v, c) for c, v in orden]


def _patron(clave):
    """Una sigla en mayusculas (TI, IA, PC) solo coincide en mayusculas, para no
    atrapar palabras como "ti" o "ia"; lo demas ignora mayusculas."""
    bandera = 0 if clave.isupper() else re.IGNORECASE
    return re.compile(rf"(?<![{LETRA}0-9]){re.escape(clave)}(?![{LETRA}0-9])", bandera)


def _marca(i):
    return "\uE000" + "".join(chr(0xE100 + int(d)) for d in str(i)) + "\uE001"


def _indice(marca):
    return int("".join(str(ord(c) - 0xE100) for c in marca))


def normalizar(texto):
    """Acentos en forma compuesta (NFC), sin la marca BOM de Windows al inicio y sin
    los caracteres privados que se usan como marcadores internos."""
    texto = unicodedata.normalize("NFC", texto).lstrip("\ufeff")
    return re.sub("[\uE000-\uE1FF]", "", texto)


def expandir_abreviaturas(texto):
    def _sub(m):
        original = m.group(1)
        lectura = con_mayuscula(original, ABREVIATURAS[original.lower()])
        # "etc." al final de la frase conserva el punto
        if original.lower() == "etc" and not re.match(r"\s*[,;:)]", m.string[m.end():]):
            return lectura + "."
        return lectura
    return EEUU.sub("Estados Unidos", ABREVIATURA.sub(_sub, texto))


def es_sigla_corta(palabra):
    romano = set(palabra) <= set("IVXLCDM") and numeros.ROMANO_VALIDO.fullmatch(palabra)
    return len(palabra) <= 3 or not re.search("[AEIOUÁÉÍÓÚ]", palabra) or bool(romano)


def con_mayuscula(original, reemplazo, inicio_frase=False):
    """Respeta la mayuscula inicial de una palabra normal (Llega -> Yega) y el
    inicio de frase; una sigla (IoT, MQTT) no impone mayuscula a su lectura."""
    titulo = original[:1].isupper() and (len(original) == 1 or original[1:].islower())
    if titulo or (inicio_frase and original[:1].isupper()):
        return reemplazo[:1].upper() + reemplazo[1:]
    return reemplazo


def mayuscula_de_regla(original, reemplazo):
    """LLAMA -> YAMA, Llama -> Yama, llama -> yama."""
    if len(original) > 1 and original.isupper():
        return reemplazo.upper()
    if original[:1].isupper():
        return reemplazo[:1].upper() + reemplazo[1:]
    return reemplazo


def aplicar(texto, excepciones, que=False):
    """Devuelve (texto convertido, avisos de lo que conviene revisar a mano)."""
    protegidos = []

    def guardar(valor):
        protegidos.append(valor)
        return _marca(len(protegidos) - 1)

    texto = normalizar(texto)
    texto = WEB.sub(lambda m: guardar(m.group(0)), texto)
    texto = expandir_abreviaturas(texto)
    texto, avisos = numeros.convertir(texto, {c.lower() for _, _, c in excepciones})

    def excepcion(valor):
        def _sub(m):
            previo = m.string[max(0, m.start() - 3):m.start()]
            inicio = m.start() == 0 or bool(INICIO_FRASE.search(previo))
            return guardar(con_mayuscula(m.group(0), valor, inicio))
        return _sub

    for patron, valor, _ in excepciones:
        texto = patron.sub(excepcion(valor), texto)

    texto = MAYUSCULAS.sub(
        lambda m: guardar(m.group(0)) if es_sigla_corta(m.group(0)) else m.group(0), texto)
    texto = CODIGO.sub(lambda m: guardar(m.group(0)), texto)

    reglas = REGLAS + ([REGLA_QUE] if que else [])
    for patron, valor in reglas:
        texto = patron.sub(lambda m, v=valor: mayuscula_de_regla(m.group(0), v), texto)

    # Una marca puede quedar dentro de otra (un codigo que contenia una excepcion).
    while MARCA_RE.search(texto):
        texto = MARCA_RE.sub(lambda m: protegidos[_indice(m.group(1))], texto)
    return texto, avisos


def sospechosas(texto, excepciones):
    """Palabras que probablemente necesitan una excepcion a mano."""
    texto = WEB.sub(" ", normalizar(texto))
    texto = numeros.convertir(expandir_abreviaturas(texto))[0]
    for patron, _, _ in excepciones:
        texto = patron.sub(" ", texto)
    de_unidades = {w for formas in numeros.UNIDADES_MEDIDA.values() for f in formas[:2] for w in f.split()}
    encontradas = set()
    for p in PALABRA.findall(texto):
        letras = p.strip("'-")
        if any(c.isdigit() for c in letras) or letras in de_unidades:
            continue                                # los avisa o los escribe numeros.py
        if len(letras) >= 2 and letras.isupper():
            encontradas.add(letras)                 # sigla
        elif (re.search(r"w|k|sh|th|ck|oo|ee|y$", letras, re.IGNORECASE)
              and letras.lower() not in CORTAS_CON_Y):
            encontradas.add(letras)                 # posible anglicismo
    return sorted(encontradas, key=str.lower)
