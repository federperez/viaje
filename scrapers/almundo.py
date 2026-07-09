"""
Scraper de Almundo.com para hoteles en Bayahibe / Punta Cana.

⚠️ Mismo aviso que en despegar.py: los selectores son una estimación
y probablemente necesiten ajuste. Usá /debug/almundo_*.html para calibrar.
"""
from urllib.parse import quote

from scrapers.utils import ScrapeResult, new_context, save_debug_evidence, human_delay
from config import CHECK_IN, CHECK_OUT, ADULTOS, HABITACIONES

# TODO: verificar/ajustar estos selectores
SELECTORS = {
    "result_card": "[data-testid='hotel-result'], .hotel-item, .result-card",
    "hotel_name": ".hotel-name, h3, [data-testid='hotel-name']",
    "price": ".price, .price-amount, [data-testid='price']",
    "link": "a",
}

BASE_URL = "https://www.almundo.com.ar/hoteles/resultados"


def _build_search_url(destino):
    query = quote(destino)
    return f"{BASE_URL}?destino={query}&checkin={CHECK_IN}&checkout={CHECK_OUT}&adultos={ADULTOS}&habitaciones={HABITACIONES}"


def scrape(destino, browser):
    resultados = []
    context = new_context(browser)
    page = context.new_page()

    try:
        url = _build_search_url(destino)
        page.goto(url, wait_until="networkidle")
        human_delay()

        cards = page.query_selector_all(SELECTORS["result_card"])
        if not cards:
            print(f"[Almundo] No se encontraron resultados para '{destino}'. Guardando debug.")
            save_debug_evidence(page, "almundo")
            return resultados

        for card in cards:
            try:
                nombre_el = card.query_selector(SELECTORS["hotel_name"])
                precio_el = card.query_selector(SELECTORS["price"])
                link_el = card.query_selector(SELECTORS["link"])

                if not nombre_el or not precio_el:
                    continue

                nombre = nombre_el.inner_text().strip()
                precio_texto = precio_el.inner_text().strip()
                link = link_el.get_attribute("href") if link_el else url
                if link and link.startswith("/"):
                    link = "https://www.almundo.com.ar" + link

                resultados.append(
                    ScrapeResult(
                        fuente="Almundo",
                        hotel=nombre,
                        precio=precio_texto,
                        moneda="ARS",
                        regimen="Ver en sitio",
                        link=link,
                    )
                )
            except Exception as e:
                print(f"[Almundo] Error parseando una card: {e}")
                continue

    except Exception as e:
        print(f"[Almundo] Error general de scraping: {e}")
        save_debug_evidence(page, "almundo")
    finally:
        context.close()

    return resultados
