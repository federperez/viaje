import types
import unittest
from unittest.mock import patch

import main


class _FakeBrowser:
    def close(self):
        pass


class _FakePlaywrightContext:
    def __init__(self):
        self._browser = _FakeBrowser()

    def __enter__(self):
        return types.SimpleNamespace(
            chromium=types.SimpleNamespace(launch=lambda headless: self._browser)
        )

    def __exit__(self, exc_type, exc, tb):
        return False


class MainRunTests(unittest.TestCase):
    def test_run_no_results_does_not_fail(self):
        with (
            patch("main.sync_playwright", return_value=_FakePlaywrightContext()),
            patch("main.despegar.scrape", return_value=[]),
            patch("main.almundo.scrape", return_value=[]),
            patch("main.booking.scrape", return_value=[]),
            patch("main.guardar_resultados") as guardar_resultados,
            patch("main.marcar_mejor_oferta") as marcar_mejor_oferta,
        ):
            main.run()

        guardar_resultados.assert_not_called()
        marcar_mejor_oferta.assert_not_called()


if __name__ == "__main__":
    unittest.main()
