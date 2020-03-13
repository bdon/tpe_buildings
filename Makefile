dev:
	python -m http.server 9000

regions.geojson:
	python kmz2geojson.py > tpe_buildings.geojson
	tippecanoe --force -z14 -e vector_tiles_uncompressed --no-tile-compression tpe_buildings.geojson

clean:
	rm tpe_buildings.geojson

