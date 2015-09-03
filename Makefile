dev:
	python -m SimpleHTTPServer 8000 .

regions.geojson:
	python regions.py

clean:
	rm regions.geojson
