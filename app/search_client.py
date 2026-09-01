"""Cliente de búsqueda web vía Serper.dev (capa gratuita: 2500 búsquedas).
Requiere SERPER_API_KEY en variable de entorno o archivo .env.
"""
import os
import time
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SERPER_URL = "https://google.serper.dev/search"


class SearchClientError(Exception):
    pass


def _api_key() -> str:
    key = os.environ.get("SERPER_API_KEY")
    if not key:
        raise SearchClientError(
            "Falta SERPER_API_KEY. Conseguila gratis en https://serper.dev y ponela en "
            "un archivo .env (SERPER_API_KEY=tu_key) o como variable de entorno."
        )
    return key


def buscar(query: str, gl: str = "ar", hl: str = "es", num: int = 20, retries: int = 3) -> dict:
    """Devuelve el JSON crudo de Serper.dev (organic results, etc.)."""
    key = _api_key()
    headers = {"X-API-KEY": key, "Content-Type": "application/json"}
    payload = {"q": query, "gl": gl, "hl": hl, "num": num}

    last_error = None
    for intento in range(retries):
        try:
            resp = requests.post(SERPER_URL, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 401:
                raise SearchClientError("SERPER_API_KEY inválida (401). Revisá la key en https://serper.dev")
            if resp.status_code == 429:
                time.sleep(2 ** intento)
                last_error = "rate limited (429)"
                continue
            last_error = f"status {resp.status_code}: {resp.text[:200]}"
        except requests.RequestException as e:
            last_error = str(e)
            time.sleep(1 + intento)
    raise SearchClientError(f"Búsqueda falló tras {retries} intentos: {last_error}")


def probar_conexion() -> bool:
    try:
        r = buscar("test", num=1)
        return "organic" in r or "searchParameters" in r
    except SearchClientError:
        return False
