"""acento-latino: preprocesador de texto para que un TTS hable con acento latinoamericano.

    >>> from acento_latino import convertir
    >>> convertir("La próxima función empieza a las 9:00.")
    'La próksima funsión empiesa a las nueve en punto.'
"""

from .reglas import aplicar, compilar_excepciones, sospechosas

__version__ = "0.1.0"
__all__ = ["convertir", "convertir_con_avisos", "palabras_a_revisar", "__version__"]


def convertir_con_avisos(texto, excepciones=None, solo_mis_excepciones=False, que=False):
    """Como convertir(), pero devuelve (texto, avisos).

    Los avisos son casos que el paquete no puede resolver solo: codigos como
    IP67, numeros despues de una sigla (ISO 9001) y "1 palabra" cuando la
    palabra podria ser femenina ("1 clase" se lee "un clase").
    """
    return aplicar(texto, compilar_excepciones(excepciones, solo_mis_excepciones), que)


def convertir(texto, excepciones=None, solo_mis_excepciones=False, que=False):
    """Reescribe texto en espanol para que un TTS lo lea con acento latinoamericano.

    excepciones: dict {palabra: lectura} o ruta a un archivo 'palabra = lectura'.
        Se suman a las que trae el paquete y ganan sobre ellas.
    solo_mis_excepciones: si es True, no usa las excepciones del paquete.
    que: si es True, ademas escribe que/qui como ke/ki (para modelos que lo cecean).
    """
    return convertir_con_avisos(texto, excepciones, solo_mis_excepciones, que)[0]


def palabras_a_revisar(texto, excepciones=None, solo_mis_excepciones=False):
    """Siglas y posibles anglicismos del texto que no tienen excepcion definida."""
    return sospechosas(texto, compilar_excepciones(excepciones, solo_mis_excepciones))
