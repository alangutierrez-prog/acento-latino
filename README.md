# acento-latino

**Haz que tu voz sintética hable como latinoamericana, no como de España.**

Los modelos de voz en español (F5-TTS y otros que leen letras) aprendieron sobre todo con audio de España: dicen *"grazias"*, *"prozeso"*, *"dezisión"*. `acento-latino` reescribe tu texto **antes** de mandarlo al modelo para que salga con seseo y yeísmo, lea bien los números y pronuncie siglas y anglicismos como se dicen en Latinoamérica.

No necesita GPU, ni reentrenar nada, ni dependencias: es Python puro y funciona con cualquier modelo.

**Sirve para cualquier proyecto con voz sintética en español latino:** videos de YouTube, TikTok o Reels, podcasts, audiolibros, cursos, publicidad, presentaciones, asistentes de voz, juegos o accesibilidad. Úsalo libremente, también en proyectos comerciales.

```
pip install git+https://github.com/alangutierrez-prog/acento-latino
```

## Antes y después

| Escribes | El modelo recibe |
|---|---|
| El nodo edge procesa los datos de vibración cerca de la máquina. | El nodo ech prosesa los datos de vibrasión serca de la máquina. |
| La próxima clase explica por qué el acceso remoto necesita una conexión segura. | La próksima clase eksplica por qué el akseso remoto nesesita una coneksión segura. |
| Llegamos el 15-03-2026 a las 10:00 con 3 sensores. | Yegamos el quinse de marso de dos mil veintiséis a las dies en punto con tres sensores. |
| El motor gira a 1.500 rpm y vibra a 4,5 mm/s. | El motor gira a mil quinientas revolusiones por minuto y vibra a cuatro coma sinco milímetros por segundo. |
| Usamos IoT, MQTT y un gateway en la nube. | Usamos internet de las cosas, eme cu te te y un geituey en la nube. |

El texto se ve raro, pero **el audio suena bien**: esa es la idea.

## Uso

### Desde la terminal

```
acento-latino guion.txt gen.txt
```

Convierte `guion.txt` y lo guarda en `gen.txt`. Sin el segundo archivo, muestra el resultado en pantalla. Al final te avisa lo que conviene revisar a mano:

```
Revisar (siglas o anglicismos sin excepcion; agregarlos con --excepciones):
  Kubernetes, NASA

Revisar numeros:
  1 clase: se leyo 'un'; si la palabra es femenina escribir 'una'
```

Opciones:

| Opción | Para qué |
|---|---|
| `-e mis_excepciones.txt` | Suma tus propias lecturas (ganan sobre las incluidas) |
| `--solo-mis-excepciones` | Usa solo tus lecturas |
| `--que` | Escribe *que/qui* como *ke/ki*, si tu modelo los cecea |
| `-q` | Sin avisos |
| `-` como entrada | Lee de la entrada estándar: `echo "Hola" \| acento-latino -` |

### Desde Python

```python
from acento_latino import convertir

convertir("La próxima función empieza a las 9:00.")
# 'La próksima funsión empiesa a las nueve en punto.'

convertir("El edge decide.", excepciones={"edge": "borde"})
# 'El borde deside.'
```

También están `convertir_con_avisos(texto)`, que devuelve `(texto, avisos)`, y `palabras_a_revisar(texto)`.

### Con F5-TTS

```
acento-latino guion.txt gen.txt
f5-tts_infer-cli -c config.toml     # con gen_file = "gen.txt" en el .toml
```

Un consejo de la práctica: **una idea por línea**. Cada salto de línea le da al modelo una pausa natural.

## Qué hace

**1. Números a palabras**, con concordancia y apócope: *21 sensores* → *veintiún sensores*, *1.500 rpm* → *mil quinientas revoluciones por minuto*, *1º lugar* → *primer lugar*. Entiende decimales (*4,5*), fechas (*20-10-2026*), horas (*14:30*, *20:00 hrs*), rangos y marcadores (*10-20 %*, *3-1*), negativos, fracciones (*1/2*, *3/4*), operaciones (*2+2*, *3 x 4*), montos (*$*, *US$*), teléfonos (*+56 9 8765 4321*), versiones (*2.0.1*), ordinales (*1º*, *3ª*, *1er*, *2da*), décadas (*los 80s*), romanos con contexto (*siglo XXI* → *siglo veintiuno*) y unidades de cocina, ciencia y técnica (*g, kg, ml, L, m², °C, mm/s, Hz, V, kW, rpm, km/h, GB*...).

**2. Abreviaturas**: *Sr.* → *señor*, *Dra.* → *doctora*, *etc.* → *etcétera*, *aprox.*, *pág.*, *N°*, *EE.UU.*...

**3. Excepciones**: siglas (*CEO* → *si i o*, *IoT* → *internet de las cosas*), anglicismos (*hardware* → *jardwer*, *Wi-Fi* → *uaifai*), lenguaje de chat (*q* → *ke*, *xq* → *porke*) y nombres propios que no siguen la regla (*México* → *Méjico*, *Ximena* → *Jimena*). Vienen [unas 100 incluidas](src/acento_latino/excepciones.txt) y puedes agregar las tuyas en un archivo:

```
# mis_excepciones.txt
Kubernetes = kubernetis
NASA = nasa
```

**4. Reglas de pronunciación latinoamericana**, respetando MAYÚSCULAS (*LLAMA YA* → *YAMA YA*):

| Regla | Ejemplo |
|---|---|
| c + e/i → s | proceso → proseso |
| z → s | razón → rasón |
| cc + e/i → ks | acceso → akseso |
| xc + e/i → ks | excelente → ekselente |
| sc + e/i → s | escena → esena |
| x → ks | próximo → próksimo |
| x inicial → s | xilófono → silófono |
| ll → y | llega → yega |

**Lo que no toca**: URLs, correos, @menciones y dominios (*www.sitio.cl*, *hola@sitio.cl*), códigos pegados (*IP67*), siglas cortas sin lectura definida y romanos sueltos (*Juan Pablo II*, *talla XL*), emojis y cualquier otro alfabeto.

**Probado con texto de todo tipo**: noticias, recetas, fútbol, redes sociales, chat, guiones de video y textos técnicos. Las pruebas incluyen decenas de miles de textos aleatorios (nunca se cae), textos de 1 MB y entradas patológicas (tiempo lineal), archivos de Windows con BOM o acentos descompuestos, y la garantía de que pasar el mismo texto dos veces no cambia nada.

## Límites conocidos

- **Punto y coma en los números**: usa la convención de Chile, Argentina, Colombia y gran parte de Sudamérica (*1.500* = mil quinientos, *3,5* = tres coma cinco). En México y Centroamérica el punto es decimal: ahí conviene escribir *3,5* o *tres punto cinco* a mano.
- **Género**: *1 clase* se lee *un clase*, porque el paquete no sabe si la palabra es femenina. Te avisa cada caso para que escribas *una*.
- **Códigos pegados** (*IP67*, *M12*, *PS5*) se dejan tal cual y se avisan. Separados, el número se lee: *ISO 9001* → *ISO nueve mil uno*.
- **Siglas cortas** (*BID*, *OEA*) y palabras de hasta tres letras escritas en MAYÚSCULAS no se tocan, para no deformar siglas: en un texto todo en mayúsculas, *VEZ* queda igual. Te las lista como "Revisar" para que agregues su lectura.
- Las lecturas de anglicismos son una propuesta: según el modelo y la voz, alguna puede sonar mejor de otra forma. Para eso están tus excepciones.

## Contribuir: mejora con cada usuario

Ninguna lista de palabras cubre todo, y cada modelo de voz lee el inglés a su manera. Por eso `acento-latino` está pensado para mejorar con el uso:

1. **Si una palabra suena mal, arréglala al tiro** en tu proyecto con `-e mis_excepciones.txt`.
2. **Cuéntanos qué funcionó** con el formulario ["Una palabra suena mal"](../../issues/new/choose), diciendo con qué modelo lo probaste.
3. Las lecturas validadas entran a la siguiente versión, y **todos** reciben el arreglo con `pip install --upgrade git+https://github.com/alangutierrez-prog/acento-latino`.

En [`excepciones.txt`](src/acento_latino/excepciones.txt) cada lectura está marcada como **VALIDADA** (escuchada con un modelo concreto) o **PROPUESTA** (aún sin escuchar). La guía [CONTRIBUTING.md](CONTRIBUTING.md) explica cómo probar variantes de una palabra en pocos minutos y lo que hemos aprendido.

También son bienvenidas variantes regionales (México, Caribe, Río de la Plata) y textos reales donde el resultado se lea mal.

## Licencia

MIT. Úsalo libremente en cualquier proyecto, personal o comercial: solo conserva el aviso de licencia.

Creado por **Alan Gutiérrez**. Nació narrando cursos con voz sintética y quedó libre para que cualquiera lo use en lo que quiera crear.
