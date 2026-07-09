"""
Configuración central del tracker de hoteles.
Modificá estos valores según tu viaje.
"""

# --- Destino y fechas ---
DESTINO = "Bayahibe"
CHECK_IN = "2026-08-09"
CHECK_OUT = "2026-08-15"
ADULTOS = 2
HABITACIONES = 1

# --- Google Sheets ---
# Nombre exacto de la planilla de Google Sheets (ya creada por vos)
GOOGLE_SHEET_NAME = "Ofertas Bayahibe"
# Nombre de la hoja/pestaña donde se guarda el historial
GOOGLE_SHEET_TAB = "Historial"
# Ruta al archivo de credenciales de la cuenta de servicio (ver README)
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# --- Scraping ---
# Delay entre pedidos para no gatillar bloqueos anti-bot (segundos)
DELAY_MIN = 3
DELAY_MAX = 7
# Timeout máximo por página (ms) para Playwright
PAGE_TIMEOUT_MS = 30000
# Si es True, guarda screenshot + HTML de cada página en /debug cuando un scraper falla
DEBUG_ON_FAILURE = True
