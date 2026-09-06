# Map Source Assessment: LOC and Wikimedia Commons

**Research date:** 2026-09-04  
**Question:** Are the Library of Congress industry guide and the Wikimedia Commons economic-map category useful for the Soviet industrialization sandbox map?

## Short answer

Yes, but for different purposes:

- The **Library of Congress (LOC) guide is useful as a curated discovery index** for authoritative map records and digitized map images. It can help identify historical industry, mines, oil, power, railroads, transportation, waterways, cities, and regional maps relevant to the launch map.
- The **Wikimedia Commons category is useful as a visual-reference and source-discovery index**, not as a canonical dataset. Its members mix original maps, derivative graphics, different dates, different territorial definitions, and files copied from other institutions.
- Neither page by itself justifies adding quantitative locations, network geometry, or 1928 industrial capacity directly to `map.py`. Those values should be extracted from the linked catalog record or underlying primary map and recorded with date, scope, and provenance.

## Library of Congress guide

The LOC page identifies itself as a research guide for finding maps and atlases of Russia and territories formerly governed by Russia in the Library's Geography and Map Division. Its metadata names the Library of Congress as publisher, Amelia Raines as creator, and gives a 2019 creation date with a 2025 modification date. The page links to subject-specific guides for cities, mines, oil, power, railroads, regional maps, transportation, and waterways, in addition to industry. [LOC Industry guide](https://guides.loc.gov/russia-maps/industry)

The guide links to an LOC item with identifier `2018693938` and to catalog records including LCCN `2014593324` and `2020585329`. These links are more valuable than the guide prose for implementation because they can lead to the map title, creator, publication date, scale, geographic coverage, and digital image. [Linked LOC item](https://www.loc.gov/item/2018693938/) [LOC LCCN 2014593324](https://lccn.loc.gov/2014593324) [LOC LCCN 2020585329](https://lccn.loc.gov/2020585329)

The guide therefore maps well to the project's future source needs:

| Map concern | LOC guide path to investigate | Likely use in the model |
| --- | --- | --- |
| Regional boundaries and names | General, administrative, regional, and oblasts | Define the national-region vocabulary and historical territorial scope |
| Launch cities | Cities | Verify city names and map-era spelling before adding city records |
| Industrial sites and minerals | Industry, mines, oil | Candidate sites and resource geography, subject to date-specific verification |
| Legacy networks | Railroads, transportation, waterways, roads, power | Identify corridors and network layers; do not infer commissioning status from a map symbol alone |

The guide is not itself a 1928 database. It is a finding aid, and the individual map record remains the source of truth for any claim. This matters because the game starts in 1928 and must not silently mix later Soviet boundaries, facilities, or networks into the starting state.

## Wikimedia Commons category

The Commons category is explicitly titled **Economic maps of the Soviet Union** and is licensed at the category-page level under CC BY-SA 4.0. Its first-party category API lists a mixed collection that includes regional maps, coal and minerals, oil and gas, power centers and transmission, waterways, machine-tool plants, shipbuilding, and economic-region maps. [Commons category](https://commons.wikimedia.org/wiki/Category:Economic_maps_of_the_Soviet_Union) [Commons category API](https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Economic_maps_of_the_Soviet_Union&cmlimit=100&format=json)

Useful candidate files visible in the category include:

- `U.S.S.R. (Including Latvia, Lithuania, Estonia, Tannu Tuva, and Island Possessions) - Economic Regions`, useful for comparing regional classification.
- `Soviet Union Coal and Major Minerals`, useful as a visual lead for resource geography.
- `Urals Area - Electric Power Centers and High Tension Transmission Network - 1951`, useful as a later network-layer reference, not as 1928 starting data.
- `Principal Waterways of the Union of Soviet Socialist Republics`, useful for identifying a possible transport layer.
- `U.S.S.R. - Machine-Tool Producing Plants`, useful for a later industrial-site layer.

The same category also contains files dated or depicting periods such as 1938, 1951, 1953-55, 1962, 1968, 1971, and 1982. It includes material attributed to DPLA, LOC, CIA, RIAN, and Wikimedia contributors. Those dates and attributions make the category unsuitable as an unfiltered source for the 1928 baseline. Each file's own description, source, creator, date, license, and original institutional record must be checked before reuse.

## Recommendation for `map.py`

The links are helpful for the next map-data slice, but they should inform a source-backed data import rather than be copied into the domain model as-is.

1. Keep `Region`, `cities`, `industrial_sites`, and `legacy_networks` as domain concepts, but add source metadata when real historical records are introduced: publication date, source URL or identifier, and the map's territorial scope.
2. Use LOC records first for the 1928 baseline and historical launch layers. Start with the LOC industry, mines, oil, power, railroads, cities, and regional guides, then verify each candidate against its underlying catalog record.
3. Use Commons to discover scans and compare visual conventions. Treat a Commons file as an implementation source only after its file page points to an authoritative original record and the relevant date matches the model's scenario.
4. Do not add coordinates, route geometry, industrial capacity, or commissioning status from the two landing pages alone. Those require the individual map record or a separate primary statistical/administrative source.
5. Preserve the existing scope boundary: agricultural maps in the Commons category may be historically interesting, but they are not playable agriculture or industrial financing inputs in this project.

## Limitations

The LOC item endpoint returned HTTP 403 from this environment during this pass, so this note does not assert metadata from the linked item beyond the identifier and links exposed by the LOC guide itself. The Commons category page and its first-party API were accessible. Before encoding historical map data, retrieve the individual LOC records and Commons file pages and preserve their exact citations.
