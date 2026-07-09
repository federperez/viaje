# Tracker de ofertas de hoteles — Bayahibe (9-15 ago 2026)

Chequea diariamente Despegar, Almundo y Booking para 2 adultos / 1 habitación
y guarda el historial completo + la mejor oferta del día en Google Sheets.

## ⚠️ Antes de usar esto, leé esto

- **Los selectores de scraping son una primera versión, no un producto terminado.**
  Estos sitios cambian su HTML seguido. La primera vez que lo corras, es muy
  probable que algún scraper no encuentre resultados. Cuando eso pase, revisá
  la carpeta `debug/` (se genera automáticamente) que va a tener un
  screenshot y el HTML de la página en el momento del fallo — con eso podés
  ver qué cambió y ajustar el selector correspondiente en
  `scrapers/despegar.py`, `scrapers/almundo.py` o `scrapers/booking.py`.
- **Booking.com es el más propenso a bloquear.** Si falla seguido, considerá
  bajarle la frecuencia solo a ese sitio (editar el workflow) o directamente
  sacarlo del pipeline y quedarte con Despegar/Almundo.
- Este scraping es para **uso personal** (monitorear precios para tu propio
  viaje). Revisá los Términos de Servicio de cada sitio si pensás escalar
  esto a un uso más intensivo.

## Paso 1: Crear la cuenta de servicio de Google (para escribir en Sheets)

1. Andá a [Google Cloud Console](https://console.cloud.google.com/)
2. Creá un proyecto nuevo (o usá uno existente)
3. Activá las APIs: **Google Sheets API** y **Google Drive API**
   (menú "APIs & Services" → "Enable APIs")
4. "APIs & Services" → "Credentials" → "Create Credentials" → "Service Account"
5. Una vez creada, entrá a la cuenta de servicio → pestaña "Keys" →
   "Add Key" → "Create new key" → tipo **JSON** → se descarga un archivo
6. Guardá ese archivo como `credentials.json` en la raíz del proyecto
   (NO lo subas a GitHub en texto plano — ver Paso 3)
7. Abrí el archivo JSON descargado y copiá el valor de `"client_email"`
   (algo como `nombre@proyecto.iam.gserviceaccount.com`)

## Paso 2: Preparar tu Google Sheet

1. Creá una planilla nueva en Google Sheets, nombrala **exactamente**
   `Ofertas Bayahibe` (o cambiá `GOOGLE_SHEET_NAME` en `config.py`)
2. Compartila (botón "Compartir") con el email de la cuenta de servicio
   del Paso 1, dándole permiso de **Editor**
3. No hace falta crear pestañas manualmente, el script las crea solo

## Paso 3: Correrlo localmente (para probar antes de automatizar)

```bash
git clone <este-repo>
cd punta-cana-tracker
pip install -r requirements.txt
playwright install chromium
# Pegá tu archivo credentials.json en esta carpeta
python main.py
```

Revisá tu Google Sheet — debería aparecer una pestaña "Historial" con los
resultados y una pestaña "Mejor oferta" con el resumen del día.

## Paso 4: Automatizarlo con GitHub Actions (chequeo diario sin que hagas nada)

1. Subí este proyecto a un repositorio de GitHub (puede ser **privado**)
2. En el repo: Settings → Secrets and variables → Actions → "New repository secret"
3. Nombre del secret: `GOOGLE_CREDENTIALS_JSON`
   Valor: pegá **todo el contenido** de tu `credentials.json`
4. El workflow en `.github/workflows/daily-check.yml` ya está configurado
   para correr todos los días a las 09:00 (hora Argentina). Podés cambiar
   el horario editando la línea `cron: "0 12 * * *"`
5. También podés correrlo manualmente en cualquier momento desde la pestaña
   **Actions** de tu repo → "Chequeo diario de ofertas Bayahibe" →
   "Run workflow"

## Estructura del proyecto

```
punta-cana-tracker/
├── config.py                  # fechas, destino, config de Sheets
├── main.py                    # orquesta todo el pipeline
├── sheets_writer.py            # escribe en Google Sheets
├── scrapers/
│   ├── despegar.py
│   ├── almundo.py
│   ├── booking.py
│   └── utils.py                # helpers compartidos (delays, debug, etc.)
└── .github/workflows/
    └── daily-check.yml         # cron job diario
```

## Ajustar fechas o destino

Todo está centralizado en `config.py`. Si cambian tus fechas de viaje o
querés monitorear otro destino, solo editá ese archivo.

## Si algo deja de funcionar

Lo más común va a ser que un sitio cambió su HTML. Pasos:
1. Mirá el log de la corrida (en Actions, o en la terminal si corrés local)
2. Buscá el mensaje `[NombreDelSitio] No se encontraron resultados`
3. Abrí el archivo `debug/nombresitio_fecha.html` en un navegador
4. Con "Inspeccionar elemento" del navegador, buscá el selector real
   del contenedor de cada hotel, del nombre y del precio
5. Actualizá el diccionario `SELECTORS` en el scraper correspondiente
