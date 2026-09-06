# HOI4 Province Map Data Research

**Date:** 2026-09-06  
**Question:** Where to find Hearts of Iron 4 (HOI4) province map data in vector format (geoJSON, shapefile)?

---

## TL;DR

**HOI4 province boundary data in vector format does not exist publicly.** HOI4 uses a bitmap/raster-based province system, not vector polygons. There are no community projects converting it, no Paradox export tools, and no downloadable geoJSON. For Soviet-era region data, use Natural Earth country boundaries + historical administrative divisions from alternative sources.

---

## 1. HOI4 Province Data — Available Formats?

**Short answer: Bitmap only, not vector.**

HOI4's map system is built on:
- A **bitmap image** (`.bmp`) defining province pixels — each pixel color = province ID
- A **definition file** (`.txt`) mapping color → province ID, terrain type, etc.
- **No vector polygons** in the base game format

Paradox stores provinces as a pixel grid, not as geometric shapes. This is fundamental to how the Clausewitz engine works across all Paradox games (EU4, HOI4, Vic3, etc.).

**Official formats from Paradox:**
| Format | Extension | Vector? |
|---|---|---|
| Province bitmap | `.bmp` | ❌ (raster) |
| Province definition | `.txt` | ❌ (text lookup) |
| Terrain data | `.txt` | ❌ (text) |
| Map positions | `.txt` | ❌ (point coordinates only) |

**Source:** HOI4 modding documentation at `hoi4.paradoxwikis.com/Modding` — the map system is described as bitmap-based.

---

## 2. Community Projects Converting HOI4 to GeoJSON?

**None found.**

Searches across GitHub for `hoi4 province geojson`, `hoi4 map vector`, `hoi4 shapefile` returned **zero results**. The HOI4 modding community works exclusively with the bitmap + text format. There are:

- Modding tools for texture/map painting (e.g., Paint.NET province texture plugins)
- Tools to extract province definitions to CSV
- **No tools to convert to vector polygon formats**

The fundamental blocker is that Paradox never published the underlying polygon data — only the rasterized pixel map. Without the vector boundaries, community conversion is impossible.

---

## 3. Paradox Modding Tools for Vector Export?

**No.**

Paradox provides:
- **Clausewitz SDK** — for reading/writing the bitmap map format, not exporting vector data
- **Vanilla modding tools** — text editors, bitmap editors, not GIS export

There is no `export to geoJSON` or `export to shapefile` functionality anywhere in the official Paradox toolchain.

---

## 4. Alternative Sources: 1930s Soviet Union Boundary/Region Data

Since HOI4 province data is unavailable in vector form, here are practical substitutes for mapping Soviet industrialization:

### A. Natural Earth Data (Recommended — Available Now)

**URL:** https://www.naturalearthdata.com/downloads/10m-cultural-vectors/

- **Admin 0 Countries** — Download: `ne_10m_admin_0_countries.zip` (4.7 MB, Shapefile/GeoDB/TIFF)
  - Contains all country boundaries including USSR
- **Admin 1 (States/Provinces)** — Download: `ne_10m_admin_1_states_provinces.zip`
  - Contains first-level administrative divisions (oblasts, territories) for Russia/USSR
- **Populated Places** — cities/towns for locating facilities
- **Railroads** — `ne_10m_railroads.zip` — major rail lines

**Format:** Shapefile, FileGDB, GeoJSON (via conversion)  
**License:** Public domain  
**Soviet-era usability:** ⚠️ Modern boundaries only — Soviet Union borders differed in 1928-1939

### B. Historical Soviet Administrative Divisions

For 1930s-specific boundaries (oblasts, krays, ASSR divisions):

1. **USSR Census boundaries (1926, 1939)**  
   - Source: Russian Academy of Sciences GIS lab
   - Search: `ruissh data gis 1926 census boundaries shapefile`

2. **Stanford University GIS Archive**  
   - URL: https://geodata.stanford.edu/
   - Contains Soviet historical boundary data

3. **CShapes / GISCO Historical Boundaries**  
   - URL: https://icr.ethz.ch/data/cshapes/ (CShapes)
   - Contains historical state boundaries (including USSR 1945-1991)

### C. Convert HOI4 Province Bitmap to Vector (DIY Option)

If you have the HOI4 map bitmap and definition file:

1. Use **Python + rasterio** or **GDAL** to polygonize the province bitmap
2. Map each province color to its ID/name from the definition file
3. Output as GeoJSON or Shapefile

```python
import rasterio
from rasterio.features import shapes
import geopandas as gpd

# Load province bitmap
with rasterio.open('provinces.bmp') as src:
    image = src.read(1)
    results = list(shapes(image, connectivity=4))
    
# Convert to GeoDataFrame with province IDs
# Then join with HOI4 province definition to get names
```

**This would be a custom conversion project** — no pre-built tool exists.

---

## Summary Table

| Source | Format | 1930s Soviet Data? | Downloadable? |
|---|---|---|---|
| HOI4 base game | Bitmap (.bmp) + .txt | Yes (in-game provinces) | Game files only |
| Paradox SDK | Proprietary Clausewitz | No vector export | Yes (SDK download) |
| Community projects | None found | — | — |
| Natural Earth | Shapefile/GeoDB | ⚠️ Modern only | ✅ Yes, free |
| Historical GIS archives | Shapefile | ✅ Yes | ⚠️ Varies by source |
| DIY raster conversion | GeoJSON | ✅ Yes | Possible with HOI4 files |

---

## Practical Recommendation for This Project

Since the project needs a **playable Soviet industrialization map** and vector HOI4 province data doesn't exist publicly:

1. **Use Natural Earth Admin 1 states/provinces for Russia** as region polygons — available in shapefile format, mappable with Leaflet/D3
2. **Overlay HOI4-style region IDs** by matching oblast names to your simulation regions
3. **Accept that province-level detail** (as in HOI4's ~500 Soviet provinces) **requires either:**
   - A custom raster-to-vector conversion from HOI4 game files, or
   - Using historical Soviet administrative division shapefiles from academic sources

**Natural Earth download links:**
- Countries: https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip
- States/Provinces: https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_1_states_provinces.zip
- Railroads: https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_railroads.zip
