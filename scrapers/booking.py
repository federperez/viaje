"""
Scraper de Booking.com para hoteles en Bayahibe.

⚠️ AVISO ESPECIAL PARA BOOKING:
Booking.com tiene protecciones anti-bot bastante más agresivas que
Despegar/Almundo (Cloudflare, fingerprinting, a veces CAPTCHA). Es
posible que este scraper funcione de forma intermitente: un día
anda, otro día Booking te tira una pantalla de verificación y este
script no va a poder resolverla (ni yo puedo ni voy a ayudar a
evadir ese tipo de bloqueo).

Alternativas si esto falla seguido:
- Reducir la frecuencia de chequeo específicamente para Booking
  (por ejemplo, cada 2-3 días en vez de diario).
- Usar el buscador de Booking manualmente y dejar que el tracker
  se enfoque en Despegar/Almundo, que suelen ser más permisivos.
- Evaluar Booking Demand API (partner program oficial) si esto se
  vuelve una necesidad estable a largo plazo: requiere aprobación
  de Booking como partner, no es un simple registro.
"""
from urllib.parse import quote

from scrapers.utils import ScrapeResult, new_context, save_debug_evidence, human_delay
from config import CHECK_IN, CHECK_OUT, ADULTOS, HABITACIONES

# TODO: verificar/ajustar estos selectores
SELECTORS = {
    "result_card": "[data-testid='property-card']",
    "hotel_name": "[data-testid='title']",
    "price": "[data-testid='price-and-discounted-price']",
    "link": "a[data-testid='title-link']",
}

BASE_URL = "https://www.booking.com/searchresults.es-ar.html"


def _build_search_url(destino):
    query = quote(destino)
    return (
        f"{BASE_URL}?ss={query}&checkin={CHECK_IN}&checkout={CHECK_OUT}"
        f"&group_adults={ADULTOS}&no_rooms={HABITACIONES}&group_children=0"
    )


def scrape(destino, browser):
    resultados = []
    context = new_context(browser)
    page = context.new_page()

    try:
        url = _build_search_url(destino)
        page.goto(url, wait_until="networkidle")
        human_delay()

        # Detección básica de bloqueo/CAPTCHA
        content = page.content().lower()
        if "captcha" in content or "verify you are human" in content:
            print("[Booking] Detección de bloqueo/CAPTCHA. Guardando debug y abortando.")
            save_debug_evidence(page, "booking")
            return resultados

        cards = page.query_selector_all(SELECTORS["result_card"])
        if not cards:
            print(f"[Booking] No se encontraron resultados para '{destino}'. Guardando debug.")
            save_debug_evidence(page, "booking")
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

                resultados.append(
                    ScrapeResult(
                        fuente="Booking",
                        hotel=nombre,
                        precio=precio_texto,
                        moneda="ARS",
                        regimen="Ver en sitio",
                        link=link,
                    )
                )
            except Exception as e:
                print(f"[Booking] Error parseando una card: {e}")
                continue

    except Exception as e:
        print(f"[Booking] Error general de scraping: {e}")
        save_debug_evidence(page, "booking")
    finally:
        context.close()

    return resultados
