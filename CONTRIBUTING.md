# Cómo contribuir

`acento-latino` mejora con cada persona que lo usa. La forma más útil de ayudar es contar **qué palabra sonó mal y qué lectura sí funcionó**, siempre diciendo con qué modelo de voz lo probaste: una lectura que suena perfecta en un modelo puede sonar mal en otro.

## Si una palabra suena mal

1. **Arréglala en tu proyecto al tiro**, sin esperar a nadie. Crea un archivo `mis_excepciones.txt`:

   ```
   gateway = puerta de enlace
   Kubernetes = kubernetis
   ```

   y úsalo así:

   ```
   acento-latino guion.txt gen.txt -e mis_excepciones.txt
   ```

2. **Cuéntanos** con el formulario ["Una palabra suena mal"](../../issues/new/choose) para que la mejora llegue a todos.

## Cómo encontrar una lectura que funcione

Es lo que hicimos para validar las lecturas incluidas, y toma unos minutos:

1. Escribe un texto de prueba con **varias formas de la misma palabra**, una por línea y numeradas, dentro de una frase corta:

   ```
   Uno. Revisa el dashbord.
   Dos. Revisa el dáchbord.
   Tres. Revisa el dash bord.
   Cuatro. Revisa el panel de control.
   ```

2. Pásalo por tu modelo de voz y escucha. Quédate con el número que suene mejor.

Lo que hemos aprendido con modelos entrenados solo en español:

- **Usa solo sílabas del español**: `sófgüer` funciona, `sofwer` o `sóftwer` no. Sonidos como *w*, *th* o *sh* se deforman.
- **La tilde ayuda** a marcar dónde va la fuerza: `ráuter`, `dáchbord`.
- **Si nada funciona, usa la palabra en español**: `IoT` sonaba "aioti" y quedó como *internet de las cosas*; `big data` quedó como *datos masivos*.
- **Las siglas deletreadas** (*eme cu te te*) a veces se pegan; prueba separarlas con comas o usar la forma en español.

## Proponer el cambio directamente

Si te manejas con GitHub, edita [`src/acento_latino/excepciones.txt`](src/acento_latino/excepciones.txt) y abre un *pull request*:

- Si la **escuchaste** y sonó bien, ponla en la sección `VALIDADAS` del modelo que usaste (o crea la sección, por ejemplo `# --- VALIDADAS con XTTS v2, nov-2026 ---`).
- Si es una **idea sin escuchar**, va en `PROPUESTAS`.
- La lectura no debe cambiar si se convierte dos veces: evita *c* antes de *e/i*, *z*, *x* y *ll* en el lado derecho (escribe `blútut`, no `blutuz`). Las pruebas lo revisan solas.

Para correr las pruebas:

```
pip install -e . pytest
pytest
```

## Otras ayudas bienvenidas

- Variantes regionales (México, Caribe, Río de la Plata).
- Unidades, abreviaturas o formatos de número que falten.
- Textos reales donde el resultado se lea mal.
