"""Natural Earth oblast data and region-to-oblast mappings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OBLAST_GEOJSON_PATH = Path(__file__).parent / "static" / "ussr_oblasts_simplified.geojson"

# Region → Natural Earth oblast name(s) mapping
# Note: Oblast set filtered to 1930s USSR borders (removed Tuva, Grodno, Gomel, Mogilev, Vitebsk)
REGION_OBLASTS: dict[str, list[str]] = {
    "Donbas": ["Donets'k", "Luhans'k", "Dnipropetrovs'k", "Zaporizhzhya", "Rostov"],
    "Moscow": ["Moskva", "Moskovskaya", "Tula", "Ryazan'", "Vladimir", "Kaluga", "Tver'", "Ivanovo", "Yaroslavl'", "Kostroma"],
    "Leningrad": ["Leningrad", "City of St. Petersburg", "Novgorod", "Pskov", "Karelia", "Murmansk"],
    "Belarus": ["Minsk", "City of Minsk"],  # Removed Gomel, Grodno, Mogilev, Vitebsk (outside 1930s border)
    "Volga": ["Nizhegorod", "Samara", "Saratov", "Ul'yanovsk", "Penza", "Udmurt", "Tatarstan", "Orenburg", "Orel", "Kursk", "Lipetsk", "Tambov"],
    "Urals": ["Sverdlovsk", "Chelyabinsk", "Perm'", "Tyumen'", "Kurgan"],
    "Caucasus": ["Rostov", "Krasnodar", "Stavropol'", "Adygey", "Karachay-Cherkess", "Kabardin-Balkar", "North Ossetia", "Chechnya", "Ingush", "Dagestan"],
    "Siberia": ["Kemerovo", "Novosibirsk", "Irkutsk", "Krasnoyarsk", "Altay", "Tomsk", "Omsk"],
    "Far East": ["Khabarovsk", "Primor'ye", "Sakhalin", "Amur", "Kamchatka", "Sakha (Yakutia)", "Chukchi Autonomous Okrug"],
    "Kazakhstan": [
        "Orenburg", "Chelyabinsk", "Kurgan", "Altay",
        "Akmola", "Aktobe", "Almaty", "Atyrau", "East Kazakhstan",
        "Jambyl", "Karaganda", "Kostanay", "Kyzylorda", "Mangystau",
        "North Kazakhstan", "Pavlodar", "Turkistan", "West Kazakhstan", "Nur-Sultan",
    ],
    "Central Asia": [
        "Orenburg", "Astrakhan'",
        "Fergana", "Tashkent", "Namangan", "Andijan", "Jizzakh",
        "Samarqand", "Bukhara", "Navoiy", "Qashqadaryo", "Surxondaryo",
        "Xorazm", "Sirdaryo", "Karakalpakstan",
        "Osh", "Jalal-Abad", "Chuy", "Batken", "Talas", "Issyk-Kul", "Naryn", "Bishkek",
        "Khatlon", "Khujand", "districts of Republican Subordination", "Gorno-Badakhshan", "Dushanbe",
        "Ahal", "Balkan", "Lebap", "Mary", "Daşoguz",
    ],
}


def get_oblast_centroids() -> dict[str, dict[str, float]]:
    with open(OBLAST_GEOJSON_PATH) as f:
        geojson = json.load(f)
    centroids: dict[str, dict[str, float]] = {}
    for feature in geojson["features"]:
        name = feature["properties"].get("name", "")
        if not name:
            continue
        geom = feature.get("geometry")
        if geom is None:
            continue
        coords = _polygon_centroid(geom)
        if coords:
            lon, lat = coords
            centroids[name] = {"lon": lon, "lat": lat, "name": name}
    return centroids


def _polygon_centroid(geom: dict[str, Any]) -> tuple[float, float] | None:
    import shapely.geometry as sg
    try:
        shape = sg.shape(geom)
        if shape.is_empty:
            return None
        centroid = shape.centroid
        return (centroid.x, centroid.y)
    except Exception:
        return None


# Hardcoded fallbacks (lat, lon) for each region — used when oblast matching fails
_FALLBACK_CENTROIDS: dict[str, tuple[float, float]] = {
    "Donbas": (47.8, 37.8),
    "Moscow": (55.8, 37.6),
    "Leningrad": (60.0, 32.3),
    "Belarus": (53.5, 27.5),
    "Volga": (53.2, 50.0),
    "Urals": (56.8, 60.6),
    "Caucasus": (44.5, 43.0),
    "Siberia": (56.0, 88.0),
    "Far East": (55.0, 140.0),
    "Kazakhstan": (48.0, 67.0),
    "Central Asia": (41.0, 65.0),
}


def get_region_centroid(region_name: str) -> tuple[float, float]:
    oblasts = REGION_OBLASTS.get(region_name, [])
    if not oblasts:
        return _FALLBACK_CENTROIDS.get(region_name, (55.0, 65.0))
    centroids = get_oblast_centroids()
    matched = []
    for obl in oblasts:
        c = centroids.get(obl)
        if c is None:
            for name, data in centroids.items():
                if obl.lower() in name.lower() or name.lower() in obl.lower():
                    c = data
                    break
        if c:
            matched.append((c["lon"], c["lat"]))
    if matched:
        avg_lon = sum(lon for lon, _ in matched) / len(matched)
        avg_lat = sum(lat for _, lat in matched) / len(matched)
        return (avg_lat, avg_lon)
    return _FALLBACK_CENTROIDS.get(region_name, (55.0, 65.0))
