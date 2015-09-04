dev:
	python -m SimpleHTTPServer 8000 .

regions.geojson:
	python regions.py

clean:
	rm regions.geojson

sql:
	psql tpe_buildings -f setup.sql 
	
