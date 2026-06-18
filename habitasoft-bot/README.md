# Bot de alta de propiedades en HabitatSoft

Automatiza el alta de inmuebles en el panel de **HabitatSoft** (`gestion.habitatsoft.com`)
controlando un navegador real con [Playwright]. Lee la info de cada propiedad de un
archivo YAML, inicia sesión, rellena el formulario de alta y sube las fotos.

> ⚠️ **Uso autorizado.** Esta herramienta automatiza tu propia cuenta. Asegúrate de
> que el uso de bots está permitido por los términos de servicio de HabitatSoft
> (el usuario confirmó que sí). Las credenciales **nunca** se guardan en el repo:
> van en un archivo `.env` local (ignorado por git) que puedes revocar.

## Por qué un navegador y no una API

HabitatSoft **no ofrece una API pública de entrada** para crear propiedades. Sus
integraciones (XML, plugins) son de *salida* (publicar en portales/web). Además el
login es una app .NET con un campo `Fingerprint` generado por JavaScript y un
**captcha condicional**. Por eso se automatiza un navegador real en vez de hacer
peticiones HTTP directas.

## Instalación

```bash
cd habitasoft-bot
python -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium
```

## Configuración

1. **Credenciales** (no se suben al repo):
   ```bash
   cp .env.example .env
   # edita .env con tu usuario y contraseña
   ```
2. **Config**:
   ```bash
   cp config.example.yaml config.yaml
   ```
   El bloque `login` ya viene con los selectores reales. El bloque
   `alta_propiedad` trae **placeholders** que hay que calibrar (siguiente paso).

## Uso

### 1. Verificar el login
```bash
habitasoft-bot login --headful
```
Si aparece un captcha, resuélvelo en la ventana (modo `--headful`).

### 2. Calibrar el formulario de alta
Como el formulario está detrás del login, este comando inicia sesión, navega al
alta y vuelca **todos sus campos reales** (id, name, tipo, opciones de los
desplegables) para que los mapees en `config.yaml`.
```bash
habitasoft-bot calibrar --headful
# Genera ./calibracion/calibracion.json, formulario.html y formulario.png
```
Copia los selectores de `calibracion.json` al bloque `alta_propiedad.campos`,
`fotos.selector_input_file` y `guardar.*` de tu `config.yaml`.

### 3. Crear una propiedad
Primero en seco (rellena pero NO guarda):
```bash
habitasoft-bot crear propiedades/ejemplo-piso.yaml --dry-run --headful
```
Cuando el `--dry-run` se vea correcto, lánzalo de verdad:
```bash
habitasoft-bot crear propiedades/ejemplo-piso.yaml --headful
```

## Estructura

```
habitasoft-bot/
├── config.example.yaml      # selectores y mapeo de campos
├── .env.example             # plantilla de credenciales
├── propiedades/
│   ├── ejemplo-piso.yaml    # una ficha por inmueble
│   └── fotos/               # imágenes (no se suben al repo)
└── src/habitasoft_bot/
    ├── config.py            # carga de config y credenciales
    ├── session.py           # navegador + login (selectores confirmados)
    ├── calibrate.py         # volcado de campos del formulario
    ├── property_form.py     # motor genérico de relleno + fotos
    └── cli.py               # comandos: login / calibrar / crear
```

## Notas

- **Captcha**: no se resuelve automáticamente. Usa `--headful` para resolverlo a mano.
- **Robustez**: si HabitatSoft cambia su formulario, basta con re-calibrar y
  actualizar los selectores en `config.yaml` (no hay que tocar código).
- **Lotes**: para varias propiedades, crea un YAML por cada una y llama a `crear`
  en un bucle.

[Playwright]: https://playwright.dev/python/
