data source
---

*Currently blocked on licensing issues*

https://github.com/sheethub/tpe3d/issues/1 (note: custom license)
https://data.taipei/#/dataset/detail?id=9b7d78d2-0d73-4b42-9b29-c1640efed0eb (OGL, but not KML format)

workflow
---
KML/KMZ Collada models are converted to a GeoJSON of all building footprints, with a height value based on the highest vertex

Create a vector tileset using Tippecanoe labeled by height value:

Convert vector to raster tiles for use as a background in iD editor
