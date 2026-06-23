import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RickAndMortyClient:
    def __init__(self):
        self.base_url = "https://rickandmortyapi.com/api"
        # Sesión con reintentos automáticos ante fallos de red
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def _fetch_all(self, endpoint: str, params: dict = None):
        """Recorre todas las páginas y devuelve todos los registros."""
        all_results = []

        # Primera petición: usamos la URL base + params del filtro
        next_url = f"{self.base_url}/{endpoint}"
        current_params = dict(params) if params else None

        while next_url:
            response = self.session.get(next_url, params=current_params, timeout=10)
            response.raise_for_status()
            data = response.json()

            all_results.extend(data.get("results", []))

            # La URL "next" ya lleva los filtros embebidos → no repetir params
            next_url = data.get("info", {}).get("next")
            current_params = None  # solo se usan en la primera petición

            time.sleep(0.05)

        return {"total_records": len(all_results), "data": all_results}

    def get_characters(self, name=None, status=None, species=None, type=None, gender=None):
        params = {k: v for k, v in locals().items() if v is not None and k != "self"}
        try:
            return self._fetch_all("character", params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"total_records": 0, "data": []}
            raise

    def get_locations(self, name=None, type=None, dimension=None):
        params = {k: v for k, v in locals().items() if v is not None and k != "self"}
        try:
            return self._fetch_all("location", params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"total_records": 0, "data": []}
            raise

    def get_episodes(self, name=None, episode=None):
        params = {k: v for k, v in locals().items() if v is not None and k != "self"}
        try:
            return self._fetch_all("episode", params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"total_records": 0, "data": []}
            raise