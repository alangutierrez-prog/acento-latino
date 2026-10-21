"""Linea de comandos: acento-latino guion.txt [salida.txt]"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .reglas import aplicar, compilar_excepciones, sospechosas


def leer(ruta, ap):
    """Lee UTF-8; si el archivo viene en ANSI de Windows, lo lee igual y avisa."""
    try:
        return ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        ap.exit(1, f"No encuentro el archivo: {ruta}\n")
    except IsADirectoryError:
        ap.exit(1, f"{ruta} es una carpeta, no un archivo de texto.\n")
    except UnicodeDecodeError:
        print(f"Aviso: {ruta} no esta en UTF-8; se leyo como ANSI de Windows (cp1252).",
              file=sys.stderr)
        return ruta.read_text(encoding="cp1252")


def main(argv=None):
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(
        prog="acento-latino",
        description="Reescribe un texto en espanol para que un TTS lo lea con acento latinoamericano.")
    ap.add_argument("entrada", help="archivo de texto, o - para leer de la entrada estandar")
    ap.add_argument("salida", type=Path, nargs="?", help="archivo de salida (si falta, se muestra en pantalla)")
    ap.add_argument("-e", "--excepciones", type=Path, help="archivo extra 'palabra = lectura'")
    ap.add_argument("--solo-mis-excepciones", action="store_true", help="no usar las excepciones incluidas")
    ap.add_argument("--que", action="store_true", help="escribir que/qui como ke/ki")
    ap.add_argument("-q", "--silencioso", action="store_true", help="no mostrar avisos")
    ap.add_argument("-V", "--version", action="version", version=f"acento-latino {__version__}")
    args = ap.parse_args(argv)

    if args.entrada == "-":
        original = sys.stdin.read()
    else:
        entrada = Path(args.entrada)
        if args.salida and args.salida.resolve() == entrada.resolve():
            ap.error("la salida no puede ser el mismo archivo de entrada")
        original = leer(entrada, ap)

    excepciones = compilar_excepciones(args.excepciones, args.solo_mis_excepciones)
    resultado, avisos = aplicar(original, excepciones, args.que)

    if args.salida:
        args.salida.write_text(resultado, encoding="utf-8")
    else:
        sys.stdout.write(resultado)

    if args.silencioso:
        return 0
    revisar = sospechosas(original, excepciones)
    if revisar:
        print("\nRevisar (siglas o anglicismos sin excepcion; agregarlos con --excepciones):",
              file=sys.stderr)
        print("  " + ", ".join(revisar), file=sys.stderr)
    if avisos:
        print("\nRevisar numeros:", file=sys.stderr)
        for aviso in avisos:
            print(f"  {aviso}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
