"""Pruebas con texto de cualquier tipo: que nunca se caiga, que no rompa lo que
no debe tocar y que convertir dos veces no cambie nada."""

import random
import time

import pytest

from acento_latino import convertir, convertir_con_avisos
from acento_latino.reglas import REGLAS, excepciones_incluidas

PRIVADOS = {chr(c) for c in range(0xE000, 0xE200)}


@pytest.mark.parametrize("entrada, esperado", [
    # web y redes: intactos
    ("Visita https://www.acento.cl/precios?id=2024.",
     "Visita https://www.acento.cl/precios?id=2024."),
    ("Escribe a juan.perez@correo.cl o a @CanalExacto",
     "Escribe a juan.perez@correo.cl o a @CanalExacto"),
    ("Entra a acento.cl/ayuda y listo.", "Entra a acento.cl/ayuda y listo."),
    # siglas, romanos y mayusculas
    ("En el siglo XXI y el capítulo IV.", "En el siglo veintiuno y el capítulo cuatro."),
    ("Juan Pablo II compró talla XL.", "Juan Pablo II compró taya XL."),
    ("BIENVENIDOS AL PROCESO DE SELECCIÓN. LLAMA YA.",
     "BIENVENIDOS AL PROSESO DE SELEKSIÓN. YAMA YA."),
    ("El CEO revisó el XML.", "El si i o revisó el ekis eme ele."),
    # abreviaturas
    ("El Sr. Pérez y la Dra. Cruz.", "El Señor Péres y la Doctora Crus."),
    ("Frutas, verduras, etc.", "Frutas, verduras, etsétera."),
    ("Pág. 12, aprox. 30 personas.", "Página dose, aproksimadamente treinta personas."),
    ("N° 5 y Nº 7.", "Número sinco y Número siete."),
    ("Viajó a EE.UU. en 2020.", "Viajó a Estados Unidos en dos mil veinte."),
    # recetas, deportes, noticias
    ("Agrega 250 g de harina y 1/4 de taza de agua.",
     "Agrega dosientos sincuenta gramos de harina y un cuarto de tasa de agua."),
    ("Colo-Colo ganó 3-1 el 05/11/2025.",
     "Colo-Colo ganó tres a uno el sinco de noviembre de dos mil veintisinco."),
    ("El partido empezó a las 20:00 hrs.", "El partido empesó a las veinte horas."),
    ("El 1er lugar y la 2da vuelta.", "El primer lugar y la segunda vuelta."),
    ("Colo-Colo quedó 1er en la tabla.", "Colo-Colo quedó primero en la tabla."),
    ("Los años 80s.", "Los años ochenta."),
    ("La versión 2.0.1 salió.", "La versión dos punto sero punto uno salió."),
    ("Llama al +56 9 8765 4321.", "Yama al más sinco seis, nueve, ocho siete seis sinco, cuatro tres dos uno."),
    ("Hay 1.000.000.000.000 de estrellas.", "Hay un biyón de estreyas."),
    ("¿Cuánto es 2+2? 3 x 4 = 12.", "¿Cuánto es dos más dos? tres por cuatro igual a dose."),
    ("La norma ISO 9001 y la RTX 4090.", "La norma ISO nueve mil uno y la RTX cuatro mil noventa."),
    ("RUT 12.345.678-9", "RUT dose miyones tresientos cuarenta y sinco mil seisientos setenta y ocho guion nueve"),
    ("a = = b", "a igual a igual a b"),
    # chat
    ("q onda, xq no viniste?", "ke onda, porke no viniste?"),
    # archivos raros
    ("﻿Texto con proceso.", "Teksto con proseso."),
    ("decisión en México", "desisión en Méjico"),
    ("Línea uno\r\nLínea con acción\r\n", "Línea uno\r\nLínea con aksión\r\n"),
    ("Hola 😂👍 ¿qué tal?", "Hola 😂👍 ¿qué tal?"),
    ("", ""),
    ("   \n\t ", "   \n\t "),
])
def test_textos_de_todo_tipo(entrada, esperado):
    assert convertir(entrada) == esperado


def test_lecturas_de_excepciones_son_estables():
    """Si una lectura cambiara con las reglas, convertir dos veces la romperia."""
    inestables = []
    for clave, lectura in excepciones_incluidas().items():
        resultado = lectura
        for patron, valor in REGLAS:
            resultado = patron.sub(valor, resultado)
        if resultado != lectura:
            inestables.append(f"{clave} = {lectura} -> {resultado}")
    assert not inestables, inestables


TEXTOS_REALES = [
    "El Presidente anunció ayer que el IPC subió 0,8% en septiembre, según el INE.",
    "Receta: bate 3 huevos, agrega 1/2 taza de azúcar y hornea 25 min a 180 °C.",
    "¡Golazo! Ganamos 2-0 y quedamos 1ros en la tabla. Próximo partido: 12/10/2026 a las 18:30.",
    "Hoy en el video les enseño a configurar el Wi-Fi del router en 5 pasos, ¡suscríbanse!",
    "La Sra. González llegó a las 9:15 con el Dr. Pérez; traían 2 cajas y 1 maleta.",
    "En el siglo XIX, la población creció un 300% y la ciudad alcanzó 1.200.000 habitantes.",
    "Capítulo III: la decisión. Llovía cuando Ximena cruzó la plaza de Oaxaca.",
    "Precio final: $19.990 (IVA incluido). Envío gratis sobre US$ 50.",
    "Descarga la app en www.ejemplo.com o escríbenos a hola@ejemplo.com.",
    "LLAMA AHORA AL 600 600 1234 Y RECIBE UN 20% DE DESCUENTO EN TU PRIMERA COMPRA.",
]


@pytest.mark.parametrize("texto", TEXTOS_REALES)
def test_convertir_dos_veces_no_cambia(texto):
    una = convertir(texto)
    assert convertir(una) == una


PALABRAS = ("el la de que proceso acción llega México gracias decisión hace cielo zapato excelente "
            "conexión taxi siglo XXI capítulo IV Sr. Dra. etc. hardware IoT CEO ONU LLAMA PROCESO "
            "y o en con por para 1 21 1.500 4,5 rpm mm/s 20-10-2026 9:00 14:30 hrs $1.000 US$ 3 x 4 "
            "2+2 = 1/2 1/4 1º 3ª 1er 2da 80s +56 9 8765 4321 2.0.1 www.ejemplo.com a@b.cl @yo "
            "EE.UU. q xq ok N° 5 -5 °C 25° 10-20 % Ximena Oaxaca pizza escena excelso").split()


def test_convertir_dos_veces_no_cambia_frases_al_azar():
    rnd = random.Random(7)
    for _ in range(3000):
        frase = " ".join(rnd.choice(PALABRAS) for _ in range(rnd.randint(1, 14)))
        una = convertir(frase)
        assert convertir(una) == una, repr(frase)


ALFABETO = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúüñÁÉÍÓÚÜÑ"
    "0123456789      .,;:!?¿¡-—–_/\\@#$%&*+=()[]{}<>«»\"'°ºª²³×\n\r\t"
    "😂👍🇨🇱€£¥ßçãõâêôàèìòù漢字中文﻿́"
)
TROZOS = ["proceso", "LLAMA", "XXI", "1.500", "4,5", "rpm", "mm/s", "20-10-2026", "9:00",
          "https://a.cl/x", "a@b.cl", "@yo", "Sr.", "etc.", "1/2", "+56 9 1234", "2.0.1",
          "IoT", "CEO", "1º", "3ª", "1er", "80s", "$1.000", "-5 °C", " x ", "EE.UU."]


def texto_aleatorio(rnd):
    partes = []
    for _ in range(rnd.randint(0, 25)):
        if rnd.random() < 0.3:
            partes.append(rnd.choice(TROZOS))
        else:
            partes.append("".join(rnd.choice(ALFABETO) for _ in range(rnd.randint(1, 12))))
    return rnd.choice(["", " ", "  ", "\n"]).join(partes)


def test_fuzz_nunca_se_cae_ni_deja_marcadores():
    rnd = random.Random(20261020)
    for _ in range(3000):
        texto = texto_aleatorio(rnd)
        resultado, avisos = convertir_con_avisos(texto)
        assert isinstance(resultado, str) and isinstance(avisos, list)
        assert not (set(resultado) & PRIVADOS), repr(texto)


@pytest.mark.parametrize("entrada", [
    "a" * 200_000,
    "1" * 200_000,
    "1." * 100_000,
    "@" * 100_000,
    "a." * 100_000,
    "a-" * 100_000,
    "x" * 100_000,
    ("palabra " * 50_000),
    ("El proceso de 1.500 rpm en www.sitio.cl con IoT. " * 20_000),   # ~1 MB
])
def test_rendimiento_textos_grandes_y_patologicos(entrada):
    inicio = time.perf_counter()
    convertir(entrada)
    assert time.perf_counter() - inicio < 10


def test_cli_archivo_inexistente_y_ansi(tmp_path, capsys):
    from acento_latino.cli import main
    with pytest.raises(SystemExit) as salida:
        main([str(tmp_path / "no_existe.txt")])
    assert salida.value.code == 1
    assert "No encuentro el archivo" in capsys.readouterr().err
    ansi = tmp_path / "ansi.txt"
    ansi.write_bytes("La decisión.".encode("cp1252"))
    assert main([str(ansi), "-q"]) == 0
    captura = capsys.readouterr()
    assert captura.out == "La desisión."
    assert "ANSI" in captura.err
