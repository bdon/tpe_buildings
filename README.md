data source
---

https://github.com/sheethub/tpe3d/issues/1

workflow
---
KML/KMZ is converted to a postgis table of all buildings

buildings are then divided into a 0.002x0.002 degree grid (roughly 3300)

example X040_Y050.geojson

a geojson file and OSM changeset is then generated for each grid
