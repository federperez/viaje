"""
Utilidades comunes para todos los scrapers:
- Manejo de errores con guardado de evidencia para debug
- Delay aleatorio "humano" entre requests
- Config de contexto de navegador con user-agent realista
"""
import os
import random
import time
from datetime import datetime

from config import DELAY_MIN, DELAY_MAX, DEBUG_ON_FAILURE, PAGE_TIMEOUT_MS

DEBUG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debug")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def human_delay():
    """Espera un tiempo aleatorio para simular navegación humana."""
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def new_context(browser):
    """Crea un contexto de navegador con configuración anti-detección básica."""
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1366, "height": 768},
        locale="es-AR",
        timezone_id="America/Argentina/Buenos_Aires",
    )
    context.set_default_timeout(PAGE_TIMEOUT_MS)
    return context


def save_debug_evidence(page, source_name):
    """
    Si un scraper falla (no encuentra los selectores esperados), guarda
    screenshot + HTML de la página para que puedas revisar qué cambió
    y ajustar los selectores en el scraper correspondiente.
    """
    if not DEBUG_ON_FAILURE:
        return
    os.makedirs(DEBUG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.join(DEBUG_DIR, f"{source_name}_{timestamp}")
    try:
        page.screenshot(path=f"{base}.png", full_page=True)
        with open(f"{base}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"[DEBUG] Evidencia guardada en {base}.png / .html")
    except Exception as e:
        print(f"[DEBUG] No se pudo guardar evidencia: {e}")


class ScrapeResult:
    """Estructura estándar que devuelve cada scraper."""

    def __init__(self, fuente, hotel, precio, moneda, regimen, link):
        self.fuente = fuente
        self.hotel = hotel
        self.precio = precio
        self.moneda = moneda
        self.regimen = regimen
        self.link = link

    def as_row(self, fecha_chequeo):
        return [
            fecha_chequeo,
            self.fuente,
            self.hotel,
            self.precio,
            self.moneda,
            self.regimen,
            self.link,
        ]
