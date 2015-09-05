dev:
	python -m SimpleHTTPServer 8000 .

regions.geojson:
	python regions.py

clean:
	rm regions.geojson

sql:
	psql tpe_buildings -f setup.sql 
	
tasks:
	output all tasks GeoJSONs

compress:
	cd tasks
	find . -name '*.geojson' -exec gzip "{}" \;

sync:
	s3cmd sync --exclude '.DS_Store' --exclude '*.swp' tasks/ s3://tpe-buildings/geojsons/ --add-header='Content-Encoding: gzip'
