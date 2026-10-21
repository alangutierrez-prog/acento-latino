import pytest

from acento_latino import convertir, convertir_con_avisos, palabras_a_revisar
from acento_latino.cli import main


@pytest.mark.parametrize("entrada, esperado", [
    ("proceso", "proseso"),
    ("decisión", "desisión"),
    ("Gracias", "Grasias"),
    ("razón", "rasón"),
    ("acceso", "akseso"),
    ("acción", "aksión"),
    ("excelente", "ekselente"),
    ("escena", "esena"),
    ("próximo", "próksimo"),
    ("xilófono", "silófono"),
    ("Llega", "Yega"),
    ("falla", "faya"),
    ("campo concreto", "campo concreto"),   # c antes de a/o/u no cambia
])
def test_reglas(entrada, esperado):
    assert convertir(entrada) == esperado


@pytest.mark.parametrize("entrada, esperado", [
    ("Usamos IoT y MQTT.", "Usamos internet de las cosas y eme cu te te."),
    ("El hardware y el software.", "El jardwer y el sófgüer."),
    ("Viajó a México.", "Viajó a Méjico."),
    ("¿Por qué? Porque sí.", "¿Por qué? Porke sí."),
    ("IoT. IoT", "Internet de las cosas. Internet de las cosas"),   # mayuscula al inicio de frase
    ("Es para ti, no para TI.", "Es para ti, no para te i."),   # sigla solo en mayusculas
])
def test_excepciones(entrada, esperado):
    assert convertir(entrada) == esperado


def test_excepciones_del_usuario_ganan():
    assert convertir("El edge.", excepciones={"edge": "borde"}) == "El borde."
    assert convertir("El edge.", excepciones={"Nodo": "nodo"}, solo_mis_excepciones=True) == "El edge."


def test_excepciones_desde_archivo(tmp_path):
    archivo = tmp_path / "mias.txt"
    archivo.write_text("# comentario\nKubernetes = kubernetis\n", encoding="utf-8")
    assert convertir("Kubernetes", excepciones=archivo) == "Kubernetis"


@pytest.mark.parametrize("entrada, esperado", [
    ("Módulo 1.", "Módulo uno."),
    ("Tenemos 21 sensores", "Tenemos veintiún sensores"),
    ("La clase 1 y la 2", "La clase uno y la dos"),
    ("gira a 1.500 rpm", "gira a mil quinientas revolusiones por minuto"),
    ("vibra a 4,5 mm/s", "vibra a cuatro coma sinco milímetros por segundo"),
    ("a 50 Hz", "a sincuenta herts"),
    ("El 20-10-2026", "El veinte de octubre de dos mil veintiséis"),
    ("a las 14:30", "a las catorse treinta"),
    ("a las 9:00", "a las nueve en punto"),
    ("a las 9:00 en punto", "a las nueve en punto"),
    ("bajó a -5 °C", "bajó a menos sinco grados Selsius"),
    ("del 10-20 %", "del dies a veinte por siento"),
    ("cuesta $1.000.000", "cuesta un miyón de pesos"),
    ("el 1º lugar", "el primer lugar"),
    ("la 3ª clase", "la tersera clase"),
    ("dura 0,05 s", "dura sero coma sero sinco s"),
    ("código 007", "código sero sero siete"),
    ("red 5G", "red sinko ge"),
])
def test_numeros(entrada, esperado):
    assert convertir(entrada) == esperado


def test_numeros_sin_convertir_y_avisos():
    texto, avisos = convertir_con_avisos("La norma ISO 20816-3, el equipo IP67 y 1 clase.")
    assert "ISO veinte mil ochosientos diesiséis guion tres" in texto
    assert "IP67" in texto and "un clase" in texto
    assert any("IP67" in a for a in avisos)
    assert any("1 clase" in a for a in avisos)


@pytest.mark.parametrize("texto", [
    "La próxima decisión llega en 2026 con 1.500 rpm.",
    "Usamos IoT, hardware y el 20-10-2026 a las 9:00.",
])
def test_idempotente(texto):
    una = convertir(texto)
    assert convertir(una) == una


def test_palabras_a_revisar():
    assert palabras_a_revisar("Usamos Kubernetes, IoT y NASA.") == ["Kubernetes", "NASA"]


def test_cli(tmp_path, capsys):
    entrada = tmp_path / "guion.txt"
    salida = tmp_path / "gen.txt"
    entrada.write_text("La próxima función.\n", encoding="utf-8")
    assert main([str(entrada), str(salida)]) == 0
    assert salida.read_text(encoding="utf-8") == "La próksima funsión.\n"
    assert main([str(entrada), "-q"]) == 0
    assert capsys.readouterr().out == "La próksima funsión.\n"
