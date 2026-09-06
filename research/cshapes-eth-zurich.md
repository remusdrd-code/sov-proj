# CShapes — ETH Zurich Historical State Boundaries Dataset

**Primary source**: [ICR ETH Zurich — CShapes](https://icr.ethz.ch/data/cshapes/) (archived page: [2024](https://web.archive.org/web/2024/https://icr.ethz.ch/data/cshapes/))
**Current version**: 2.0
**License**: CC BY-NC-SA 4.0

---

## 1. What is CShapes?

CShapes is a historical GIS dataset of **state borders and capitals** maintained by the [International Conflict Research (ICR)](https://icr.ethz.ch/) group at ETH Zurich. It maps the borders and capitals of independent states and dependent territories from **1886 to 2019**.

The dataset comes in two variants based on different state-coding schemes:
- **Gleditsch & Ward (1999)** coding
- **Correlates of War (COW)** coding

Border changes were coded using the Territorial Change Dataset (Tir et al.), *Encyclopedia of International Boundaries* (Biger), and *Encyclopedia of African Boundaries* (Brownlie).

**Reference**: Schvitz, Rüegger, Girardin, Cederman, Weidmann, Gleditsch — "[CShapes 2.0](https://icr.ethz.ch/publications/cshapes-2/)"

---

## 2. Years Covered

| Version | Coverage |
|---------|----------|
| CShapes 2.0 | **1886 – 2019** |
| Previous (0.x.x) | Varies |

---

## 3. Available Formats

| Format | File | Notes |
|--------|------|-------|
| **GeoJSON** | `CShapes-2.0.geojson` | Full dataset, one FeatureCollection |
| **Shapefile** | `CShapes-2.0.zip` | Zipped Shapefile bundle |
| **CSV** | `CShapes-2.0.csv` | UTF-8 encoded country-year rows |
| **SQL** | `CShapes-2.0.sql` | Insert statements |
| **R package** | `cshapes` | On CRAN: `install.packages("cshapes", dependencies = TRUE)` |

**Download URLs** (from archived page):
- `https://icr.ethz.ch/data/cshapes/CShapes-2.0.geojson`
- `https://icr.ethz.ch/data/cshapes/CShapes-2.0.zip`
- `https://icr.ethz.ch/data/cshapes/CShapes-2.0.csv`
- `https://icr.ethz.ch/data/cshapes/CShapes-2.0.sql`

Note: The live `icr.ethz.ch` domain returned 404 at time of writing. Use the [Wayback Machine archive](https://web.archive.org/web/2024/https://icr.ethz.ch/data/cshapes/) to access the page and download files.

---

## 4. Administrative Levels

> **⚠️ Critical limitation for this project**: CShapes is a **country-level** dataset only.

CShapes contains:
- **State borders** (national boundaries between sovereign/semi-sovereign states)
- **Capital locations** (point coordinates)

It does **NOT** contain internal administrative divisions such as:
- Oblasts
- Krays
- Republics (Soviet SFSR, Ukrainian SSR, etc.)
- Provinces, districts, or any subnational units

CShapes models the USSR as a single state entity from 1945 onward. It cannot distinguish between individual Soviet republics, oblasts, or krays.

---

## 5. Soviet Union Coverage (1928–1939)

| Question | Answer |
|----------|--------|
| Does CShapes cover 1928–1939? | **No** — The dataset begins coverage of the USSR only from **1945** (when it was a founding member of the UN system). Earlier years are not present. |
| Does it have internal USSR boundaries? | No — USSR is a single country record, not subdivided into republics/oblasts. |
| Are there Soviet-adjacent states? | Yes — Finland, Poland, Romania, Turkey, Iran, Afghanistan, China, Mongolia, Japan, Estonia, Latvia, Lithuania (when independent) appear with their borders. |
| What about 1928–1939 period? | **Not covered.** CShapes is not usable for the early Soviet industrialization period. |

---

## 6. Data Structure (GeoJSON/CSV Attributes)

Sample GeoJSON feature properties:

```json
{
  "cntry_name": "United States of America",
  "area": 7940050,
  "capname": "Washington",
  "caplong": -77.0367,
  "caplat": 38.895,
  "gwcode": 2,
  "gwsdate": "31.12.1885 23:00:00",
  "gwsyear": 1886,
  "gwsmonth": 12,
  "gwsday": 31,
  "gwedate": "",
  "gweyear": null,
  "gwemonth": null,
  "gweday": null,
  "cap_geom": "POINT(...)"
}
```

### Key fields

| Field | Description |
|-------|-------------|
| `cntry_name` | Country name string |
| `area` | Area in km² |
| `capname` | Capital city name |
| `caplong` / `caplat` | Capital coordinates |
| `gwcode` | Gleditsch & Ward numeric country code |
| `gwsdate` | State start date (day.month.year hour:min:sec) |
| `gwsyear` / `gwsmonth` / `gwsday` | Start year/month/day |
| `gwedate` | State end date (empty if still existing) |
| `gweyear` / `gwemonth` / `gweday` | End year/month/day |
| `cap_geom` | Capital geometry (point) |

The **shapefile/GeoJSON geometry** is the country border polygon.

---

## 7. Relevance to This Project

**Not suitable** for the Soviet industrialization map project because:

1. ❌ **No subnational data** — no oblasts, krays, or republics
2. ❌ **No 1928–1939 coverage** — USSR appears only from 1945
3. ❌ **Country-level only** — cannot support region-level simulation

**Alternatives to consider** (per `research/hoi4-province-map-data.md`):
- **Natural Earth** Admin 1 states/provinces — covers modern Russia, usable with Leaflet/D3
- **Russian Academy of Sciences GIS lab** — USSR Census boundaries (1926, 1939) in shapefile format
- **Stanford GIS Archive** — Soviet historical boundary data
- **DIY raster-to-vector** from HOI4 game files using Python + rasterio/GDAL

---

## 8. Related Links

- [CShapes interactive visualizer](https://cshapes.ethz.ch/) (live)
- [GROW<sup>up</sup> Research Front-End](https://growup.ethz.ch/rfe) — country-year statistics 1946–2017
- [cshapes R package on CRAN](https://cran.r-project.org/package=cshapes)
- [Precomputed dyadic distance data](https://icr.ethz.ch/data/cshapes/Dyadic_distance_data/)
- [Change log](https://icr.ethz.ch/data/cshapes/ChangeLog.txt)
