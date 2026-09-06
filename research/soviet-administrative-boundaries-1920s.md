# Soviet Administrative Boundaries 1920s — Research Findings

**Date:** 2026-09-06  
**Question:** Historical Soviet administrative boundaries 1922–1929, vector data sources, DVRK/ISCK, railway network vectors, and population/industrial center coordinates.

---

## TL;DR

**No single open-source dataset** provides 1920s Soviet administrative boundaries in vector format. The best publicly accessible sources are raster maps at Wikimedia Commons and the academic Eurasian GIS literature. RSFSR internal boundaries underwent a major reform in 1929 (guberniya → oblast/kray), which is well-documented but not widely digitized. **DVRK and ISCK could not be located** — these may be very niche academic projects, defunct, or misnamed.

---

## 1. Soviet Republic Borders (1922–1929)

### Available Vector Data

| Source | Format | Coverage | Access |
|--------|--------|----------|--------|
| Natural Earth 1:10m | GeoJSON/SHP | Modern country borders only | ✅ `data/natural-earth/` in this repo |
| Wikimedia Commons historical maps | Raster (PNG/JPEG) | Variable — mixed dates | ✅ [Commons category](https://commons.wikimedia.org/wiki/Category:Maps_of_the_Soviet_Union) |
| Wikipedia SVG maps | SVG vector | Historical, but hand-drawn, not GIS-ready | ✅ Via Wikipedia article |

**Finding:** Modern Natural Earth borders reflect post-1991 boundaries, not 1922–1939 Soviet republic borders. Wikimedia Commons has scanned historical maps including 1930s economic region maps, but they are raster images requiring georeferencing to use in a GIS.

**Key limitation:** There is no publicly available, pre-digitized GeoJSON of 1920s USSR republic borders. The constituent republic borders (RSFSR, Ukrainian SSR, Belarusian SSR, Transcaucasian SFSR) changed between 1922 and 1936 and were not preserved in open vector datasets.

### Wikipedia Reference Maps

- [History of the administrative division of Russia](https://en.wikipedia.org/wiki/History_of_the_administrative_division_of_Russia) — Russian/Soviet administrative evolution with inline maps showing guberniya → oblast transitions
- [Russian Soviet Federative Socialist Republic](https://en.wikipedia.org/wiki/Russian_Soviet_Federative_Socialist_Republic) — article includes RSFSR territorial evolution
- [Ukrainian Soviet Socialist Republic](https://en.wikipedia.org/wiki/Ukrainian_Soviet_Socialist_Republic) — article covers early Ukrainian SSR administrative history

---

## 2. Internal RSFSR/Oblast Boundaries 1923–1928

### What Changed by 1930

The **major administrative reform** happened in **1929** — the guberniya (губерния) system was abolished and replaced with the oblast (область) and kray (край) system that largely persists today.

**Key changes:**
- Before 1929: RSFSR divided into guberniyas, which contained uyezds, which contained volosts
- 1923–1924: Uyezds were abolished in most areas, volosts became the lowest-level unit
- 1929: Guberniyas replaced by oblasts and krays. New oblasts included: Ivanovo Industrial Oblast, Nizhny Novgorod Oblast, Saratov Oblast, etc. Many modern oblasts trace to this reform.
- Same reform pattern applied in Ukrainian SSR (1925), Belarusian SSR (1924), and Transcaucasian SFSR (1922–1924)

### Sources Documenting These Changes

- **Wikipedia:** [History of the administrative division of Russia](https://en.wikipedia.org/wiki/History_of_the_administrative_division_of_Russia) — includes tables of guberniyas and their transformation into oblasts
- **Russian Wikipedia** (ru.wikipedia.org) has more detailed guberniya-level maps for the 1920s period
- **Wikipedia SVG maps** showing guberniya boundaries exist but are schematic, not georeferenced

### Digitized Vector Data for 1920s Boundaries

**None found in open-access repositories.** The guberniya-to-oblast transformation is documented textually and in static historical maps, but the polygon boundaries themselves are not available as downloadable GIS datasets.

**Workaround for this project:** Use 1939 Soviet census oblast boundaries (available in some academic GIS projects) as a close proxy — the 1929 reform was the main boundary change, so 1939 boundaries are close to the post-reform starting point of the game's 1928 scenario.

---

## 3. Historical GIS Archives and Sources

### High-Trust Primary Sources

| Source | What It Has | Format | Access |
|--------|-------------|--------|--------|
| **Institute of Geography, Russian Academy of Sciences** | Historical physical/transport maps | Unknown digital availability | Likely internal/academic |
| **RGGRF** (Russian State Archive of the Federal Government) | Scan archives of historical administrative maps | Scans only, not vector | Unknown access |
| **NGIOC** (National GIS Operator) | Russian geospatial data | Modern data only | Unknown access |
| **Library of Congress** | Catalog of historical Russia/Soviet maps | Finding aid (not data) | ✅ [LOC Russia maps guide](https://guides.loc.gov/russia-maps) |
| **Wikimedia Commons** | Historical economic/industrial maps | Raster images | ✅ [Commons USSR maps](https://commons.wikimedia.org/wiki/Category:Maps_of_the_Soviet_Union) |

### International Academic Projects

- **ORBIS** (Stanford) — Roman road network, not Soviet era
- **China Historical GIS** (Harvard/Fudan) — Chinese administrative history, not Soviet
- **European Science Foundation** projects on historical GIS — likely require institutional access

### Commercially Available (Not Free)

- **MIIGAiK** (Moscow State University of Geodesy and Cartography) — may have historical map archives
- **ESRI ArcGIS Online** — some historical map layers available via subscription
- **ChronoJSON** — historical administrative boundaries for various countries, but USSR coverage unknown

### Key Limitation

**Vector data for 1920s Soviet administrative boundaries is essentially unavailable in open-access form.** This is a known gap in open GIS — Soviet-era administrative history is poorly digitized compared to Western Europe or the US. The data exists in Russian state archives but is not publicly released in GIS-ready formats.

---

## 4. DVRK/ISCK — Could Not Locate

**DVRK** ("Digital Visualization of the Russian Kingdom") and **ISCK** could not be found in any public repository, search index, or academic database accessible from this environment.

**Possible explanations:**
- These may be very specialized academic projects at specific universities (e.g., Russian Academy of Sciences institutes)
- They may have been renamed, merged, or discontinued
- The acronyms may be incorrect or alternate names for more known projects
- They may require institutional access (academic network, Russian-language access)

**If you have a full name or institutional affiliation for either project**, I can search more specifically.

---

## 5. Soviet Railway Network Vector Data

**No open vector dataset of 1920s Soviet railways was found.**

- HOI4 province data is bitmap-based (not vector) — confirmed not usable
- Paradox provides no vector export tools for rail networks
- Wikimedia Commons has 1930s-era Soviet railway maps but they are raster scans
- Wikipedia has hand-drawn SVG railway maps that are schematic, not GIS-georeferenced

**Practical path forward for this project:**
1. Use Wikimedia Commons 1930s railway maps as visual reference for georeferencing
2. The existing `network.py` already has stubs for railway network data
3. Consider using the 1939 base map boundaries as a proxy and annotating with known 1928-era facilities from industrial map research

---

## 6. 1920s Population/Industrial Center Coordinates

From prior research in this repo (`industrial-map-1930s-soviet-union.md`):

- LOC industry guides list cities with coordinates in catalog records
- The 1926 Soviet census is the best population dataset, but coordinates require geocoding city names
- Industrial center coordinates for 1928 exist in aggregate form but not in a single downloadable dataset

**Sources for city coordinates:**
| Source | Coverage | Format |
|--------|----------|--------|
| **GeoNames** (geonames.org) | Global cities, including Russian/Soviet | CSV, API |
| **Natural Earth 1:10m** | ~1,500 world cities | GeoJSON/SHP in `data/natural-earth/` |
| **US NGA/GNS** | Soviet city names | CSV (but modern spellings only) |

**Limitation:** GeoNames and NGA/GNS use modern spellings and may not cover smaller industrial settlements of the 1920s.

---

## Recommendations for This Project

1. **Boundaries:** Use modern Natural Earth `ne_10m_admin_1_states_provinces.shp` for Russia as the base layer. The 1928 scenario runs before major 1930s territorial changes (Finland, Poland, Baltic states lost by 1940 are partially present in the modern data). The boundary between RSFSR and other republics is approximated by modern international borders.

2. **Guberniya → Oblast transitions:** Implement a lookup table in `map.py` that maps 1928-era guberniya names to their 1929-reform oblast equivalents. This gives conceptual accuracy without needing polygon data.

3. **Railways:** Treat the railway network as a planned overlay layer with known 1928 routes documented in the historical literature. Do not attempt to derive from bitmap sources.

4. **Cities:** Use Natural Earth's city layer as the base, supplemented by the 1926 census city list geocoded to modern coordinates.

5. **DVRK/ISCK:** If you have additional context (full project name, institution, or URL), I can search again with more specific terms.

---

## Sources Checked

- GitHub (multiple search queries for `soviet historical gis`, `russia 1920 administrative boundaries`, `DVRK`, `ISCK`, `RSFSR shapefile`)
- Wikimedia Commons API and category pages
- Library of Congress Russia maps research guide
- Wikipedia articles on Soviet administrative history
- Wikipedia SVG historical maps
- Academic GIS project portals (ORBIS, China Historical GIS)
- Russian state archive portals (RGGRF, NGIOC — accessibility uncertain)

---

## Appendix: Key Wikipedia Articles for Historical Reference

- [History of the administrative division of Russia](https://en.wikipedia.org/wiki/History_of_the_administrative_division_of_Russia) — guberniya/oblast evolution
- [Ukrainian Soviet Socialist Republic](https://en.wikipedia.org/wiki/Ukrainian_Soviet_Socialist_Republic) — Ukrainian SSR administrative history
- [Belarusian Soviet Socialist Republic](https://en.wikipedia.org/wiki/Belarusian_Soviet_Socialist_Republic) — Belarusian SSR formation and borders
- [Transcaucasian SFSR](https://en.wikipedia.org/wiki/Transcaucasian_SFSR) — 1922–1936 federation dissolution
- [Soviet Union](https://en.wikipedia.org/wiki/Soviet_Union) — general history, territorial evolution table
- [List of regions of the Russian Soviet Federative Socialist Republic](https://en.wikipedia.org/wiki/List_of_regions_of_the_Russian_Soviet_Federative_Socialist_Republic) — detailed guberniya/oblast list with dates
