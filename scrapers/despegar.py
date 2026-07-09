"""
Scraper de Despegar.com para hoteles en Bayahibe / Punta Cana.

⚠️ IMPORTANTE - LEER ANTES DE USAR:
Los selectores CSS de abajo son mi mejor estimación basada en cómo suelen
armar sus resultados de búsqueda los sitios de este estilo (atributos
data-testid, clases con "card", "price", etc.). Despegar puede haber
cambiado su estructura. Si al correr esto no aparece ningún resultado:

1. Corré con DEBUG_ON_FAILURE=True (ya está por default en config.py).
2. Abrí el HTML guardado en /debug/despegar_*.html
3. Buscá en el navegador (botón derecho > Inspeccionar) el nombre real
   del contenedor de cada resultado de hotel y actualizá SELECTORS abajo.

Esta función siempre va a devolver una lista (vacía si no encontró nada),
nunca rompe el resto del pipeline.
"""
from urllib.parse import quote

from scrapers.utils import ScrapeResult, new_context, save_debug_evidence, human_delay
from config import CHECK_IN, CHECK_OUT, ADULTOS, HABITACIONES

# TODO: verificar/ajustar estos selectores inspeccionando la página real
SELECTORS = {
    "result_card": "[data-testid='hotel-card'], .hotel-card, article",
    "hotel_name": "[data-testid='hotel-name'], h3, .hotel-card-name",
    "price": "[data-testid='price-value'], .price-value, .final-price",
    "link": "a",
}

BASE_URL = "https://www.despegar.com.ar/hoteles/resultados"


def _build_search_url(destino):
    # Despegar arma la URL de búsqueda con slugs específicos por ciudad.
    # Si esta URL no lleva directo a resultados, hay que buscar manualmente
    # una vez en el navegador, copiar la URL real de resultados para
    # Bayahibe y pegarla acá como plantilla con las fechas parametrizadas.
    query = quote(destino)
    return f"{BASE_URL}?destination={query}&checkin={CHECK_IN}&checkout={CHECK_OUT}&adults={ADULTOS}&rooms={HABITACIONES}"


def scrape(destino, browser):
    """
    Busca hoteles en Despegar para el destino dado.
    Devuelve lista de ScrapeResult (puede ser vacía).
    """
    resultados = []
    context = new_context(browser)
    page = context.new_page()

    try:
        url = _build_search_url(destino)
        page.goto(url, wait_until="networkidle")
        human_delay()

        cards = page.query_selector_all(SELECTORS["result_card"])
        if not cards:
            print(f"[Despegar] No se encontraron resultados para '{destino}'. Guardando debug.")
            save_debug_evidence(page, "despegar")
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
                    link = "https://www.despegar.com.ar" + link

                resultados.append(
                    ScrapeResult(
                        fuente="Despegar",
                        hotel=nombre,
                        precio=precio_texto,
                        moneda="ARS",
                        regimen="Ver en sitio",
                        link=link,
                    )
                )
            except Exception as e:
                print(f"[Despegar] Error parseando una card: {e}")
                continue

    except Exception as e:
        print(f"[Despegar] Error general de scraping: {e}")
        save_debug_evidence(page, "despegar")
    finally:
        context.close()

    return resultados
