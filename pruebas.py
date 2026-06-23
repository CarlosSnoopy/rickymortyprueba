import requests

def diagnostico_temporadas():
    url = "https://rickandmortyapi.com/api/episode"
    # Consultamos la primera página de episodios
    res = requests.get(url).json()
    
    # Extraemos el código de temporada (ej: S01 del código S01E01)
    temporadas = {ep['episode'][:3] for ep in res['results']}
    
    print(f"Temporadas detectadas: {sorted(list(temporadas))}")

diagnostico_temporadas()