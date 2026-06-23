import io
import pandas as pd
from fastapi import FastAPI, Query, HTTPException, Response
from services.api_client import RickAndMortyClient

app = FastAPI(
    title="Rick & Morty - API Total",
    description="Endpoints síncronos que descargan absolutamente todos los registros de golpe.",
    version="3.0.0"
)

rm_client = RickAndMortyClient()


@app.get("/api/v1/personajes", tags=["Personajes"])
def obtener_todos_los_personajes(
    name: str = Query(None, description="Nombre del personaje (ej. Rick)"),
    status: str = Query(None, description="Estado: alive, dead, unknown"),
    species: str = Query(None, description="Especie (ej. Human, Alien)"),
    type: str = Query(None, description="Subespecie o tipo"),
    gender: str = Query(None, description="Género: Female, Male, Genderless, unknown")
):
    """
    Trae **todos** los personajes que cumplan con los filtros.
    Internamente hace todas las peticiones necesarias a la API original.
    """
    try:
        resultado = rm_client.get_characters(
            name=name, status=status, species=species, type=type, gender=gender
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")


@app.get("/api/v1/ubicaciones", tags=["Ubicaciones"])
def obtener_todas_las_ubicaciones(
    name: str = Query(None, description="Nombre de la ubicación (ej. Earth)"),
    type: str = Query(None, description="Tipo (ej. Planet, Cluster)"),
    dimension: str = Query(None, description="Dimensión (ej. Dimension C-137)")
):
    """Trae **todas** las ubicaciones sin límite de paginación."""
    try:
        return rm_client.get_locations(name=name, type=type, dimension=dimension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")


@app.get("/api/v1/episodios", tags=["Episodios"])
def obtener_todos_los_episodios(
    name: str = Query(None, description="Nombre del episodio (ej. Pilot)"),
    episode: str = Query(None, description="Código del episodio (ej. S01E01)")
):
    """Trae **todos** los episodios de la serie de golpe."""
    try:
        return rm_client.get_episodes(name=name, episode=episode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")
    
@app.get("/api/v1/exportar/csv", tags=["Exportación Única"])
def exportar_recurso_csv(
    recurso: str = Query(..., enum=["personajes", "ubicaciones", "episodios"], description="El recurso que deseas descargar"),
    # Filtros compartidos y específicos
    name: str = Query(None, description="Filtro por nombre (aplica a todos)"),
    status: str = Query(None, description="Filtro por estado (solo personajes)"),
    species: str = Query(None, description="Filtro por especie (solo personajes)"),
    type: str = Query(None, description="Filtro por tipo (personajes y ubicaciones)"),
    gender: str = Query(None, description="Filtro por género (solo personajes)"),
    dimension: str = Query(None, description="Filtro por dimensión (solo ubicaciones)"),
    episode: str = Query(None, description="Filtro por código de episodio (solo episodios)")
):
    """
    Endpoint único para la descarga de archivos CSV. 
    Detecta el recurso solicitado, aplica los filtros correspondientes y genera el archivo sobre la marcha.
    """
    try:
        if recurso == "personajes":
            resultado = rm_client.get_characters(name=name, status=status, species=species, type=type, gender=gender)
            filename = "personajes_filtrados.csv"
        
        elif recurso == "ubicaciones":
            resultado = rm_client.get_locations(name=name, type=type, dimension=dimension)
            filename = "ubicaciones_filtradas.csv"
        
        elif recurso == "episodios":
            resultado = rm_client.get_episodes(name=name, episode=episode)
            filename = "episodios_filtrados.csv"
        
        data = resultado.get("data", [])
        if not data:
            raise HTTPException(status_code=404, detail=f"No se encontraron {recurso} con los filtros aplicados.")

        df = pd.DataFrame(data)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        
        response = Response(content=stream.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte de {recurso}: {str(e)}")