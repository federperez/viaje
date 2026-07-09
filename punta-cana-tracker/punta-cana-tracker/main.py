"""
Orquesta el chequeo diario:
1. Corre los 3 scrapers (Despegar, Almundo, Booking)
2. Guarda todos los resultados en Google Sheets (historial)
3. Calcula y registra la mejor oferta del día
"""
import re
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from config import DESTINO
from scrapers import despegar, almundo, booking
from sheets_writer import guardar_resultados, marcar_mejor_oferta


def _precio_a_numero(precio_texto):
    """
    Intenta extraer un número comparable de un string de precio
    (ej: "$ 123.456" -> 123456.0, "ARS 45.000,50" -> 45000.50).
    Devuelve None si no puede parsear.
    """
    if not precio_texto:
        return None
    limpio = re.sub(r"[^\d.,]", "", precio_texto)
    if not limpio:
        return None
    # Formato es-AR: punto = miles, coma = decimales
    limpio = limpio.replace(".", "").replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        return None


def run():
    fecha_chequeo = datetime.now().strftime("%Y-%m-%d %H:%M")
    todos_los_resultados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for nombre_scraper, modulo in [
            ("Despegar", despegar),
            ("Almundo", almundo),
            ("Booking", booking),
        ]:
            print(f"--- Corriendo scraper: {nombre_scraper} ---")
            try:
                resultados = modulo.scrape(DESTINO, browser)
                if not resultados:
                    print(f"[{nombre_scraper}] Sin resultados para '{DESTINO}'. Revisá /debug.")
                todos_los_resultados.extend(resultados)
            except Exception as e:
                print(f"[{nombre_scraper}] Falló completamente: {e}")

        browser.close()

    if not todos_los_resultados:
        print("No se obtuvo ningún resultado de ningún sitio. Revisá /debug para diagnosticar.")
        sys.exit(1)

    # Guardar historial completo
    filas = [r.as_row(fecha_chequeo) for r in todos_los_resultados]
    guardar_resultados(filas)

    # Calcular mejor oferta del día (menor precio parseable)
    con_precio_numerico = [
        (r, _precio_a_numero(r.precio)) for r in todos_los_resultados
    ]
    con_precio_numerico = [(r, p) for r, p in con_precio_numerico if p is not None]

    if con_precio_numerico:
        mejor, precio_min = min(con_precio_numerico, key=lambda x: x[1])
        print(f"Mejor oferta del día: {mejor.hotel} ({mejor.fuente}) - {mejor.precio}")
        marcar_mejor_oferta(mejor, fecha_chequeo)
    else:
        print("No se pudo determinar la mejor oferta (precios no parseables).")


if __name__ == "__main__":
    run()
