CREATE EXTENSION postgis;
CREATE EXTENSION hstore;

DROP TABLE buildings;

CREATE TABLE buildings(id int, height float, row int, col int);
SELECT AddGeometryColumn('buildings', 'geom', 4326, 'Geometry', 2);
CREATE INDEX buildings_idx ON buildings USING GIST (geom);
CREATE INDEX buildings_row_idx on buildings(row);
CREATE INDEX buildings_col_idx on buildings(col);
