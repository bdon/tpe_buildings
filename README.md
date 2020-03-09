data source
---

https://github.com/sheethub/tpe3d/issues/1

workflow
---
KML/KMZ Collada models are converted to a GeoJSON of all building footprints, with a height value based on the highest vertex

Create a vector tileset using Tippecanoe labeled by height value:

tippecanoe --no-tile-compression --force -z14 -d18 -pS -e tiles out.geojson

Convert vector to raster tiles for use as a background in iD editor
