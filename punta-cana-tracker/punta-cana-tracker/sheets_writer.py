"""
Escribe los resultados de cada corrida en Google Sheets.

Requiere una cuenta de servicio de Google Cloud con acceso a Sheets API
y Drive API, y que hayas compartido tu planilla con el email de esa
cuenta de servicio. Ver README.md para el paso a paso.
"""
import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_SHEET_NAME, GOOGLE_SHEET_TAB, GOOGLE_CREDENTIALS_FILE

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["Fecha chequeo", "Fuente", "Hotel", "Precio", "Moneda", "Régimen", "Link"]


def _get_worksheet():
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME)

    try:
        worksheet = sheet.worksheet(GOOGLE_SHEET_TAB)
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=GOOGLE_SHEET_TAB, rows=1000, cols=len(HEADERS))
        worksheet.append_row(HEADERS)

    # Si la hoja está vacía (recién creada), agregar encabezados
    if worksheet.row_count == 0 or not worksheet.get_all_values():
        worksheet.append_row(HEADERS)

    return worksheet


def guardar_resultados(resultados_con_fecha):
    """
    resultados_con_fecha: lista de filas ya formateadas con
    ScrapeResult.as_row(fecha_chequeo)
    """
    if not resultados_con_fecha:
        print("[Sheets] No hay resultados para guardar.")
        return

    worksheet = _get_worksheet()
    worksheet.append_rows(resultados_con_fecha, value_input_option="USER_ENTERED")
    print(f"[Sheets] Se guardaron {len(resultados_con_fecha)} filas.")


def marcar_mejor_oferta(mejor_oferta, fecha_chequeo):
    """
    Opcional: escribe en una pestaña separada "Mejor oferta" la mejor
    oferta encontrada en el día, para tener un resumen rápido sin
    tener que revisar todo el historial.
    """
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME)

    try:
        resumen = sheet.worksheet("Mejor oferta")
    except gspread.WorksheetNotFound:
        resumen = sheet.add_worksheet(title="Mejor oferta", rows=1000, cols=len(HEADERS))
        resumen.append_row(HEADERS)

    resumen.append_row(mejor_oferta.as_row(fecha_chequeo), value_input_option="USER_ENTERED")
    print("[Sheets] Mejor oferta del día registrada.")
