import json
import os
from fastapi import APIRouter, Query, HTTPException

router = APIRouter()


def _load_cities():
    data_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "world_cities.json"))
    if not os.path.exists(data_path):
        raise FileNotFoundError("data/world_cities.json not found. Please download OpenWeather city list.")
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


_CITIES_CACHE = None


@router.get("/search_city")
def search_city(q: str = Query(..., min_length=2)):
    """
    Search cities by name substring. Returns up to 10 matches with name, country, lat, lon.
    Requires data/world_cities.json from OpenWeather bulk sample.
    """
    global _CITIES_CACHE
    try:
        if _CITIES_CACHE is None:
            _CITIES_CACHE = _load_cities()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    q_lower = q.lower()
    results = []
    for c in _CITIES_CACHE:
        name = c.get("name", "")
        if q_lower in name.lower():
            coord = c.get("coord", {})
            results.append({
                "id": c.get("id"),
                "name": name,
                "country": c.get("country"),
                "lat": coord.get("lat"),
                "lon": coord.get("lon"),
            })
            if len(results) >= 10:
                break
    return results


