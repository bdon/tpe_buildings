# start with a full building database.
# find the extent of the dataset

import psycopg2
import json
from shapely.wkt import loads
from shapely.geometry import box, mapping

conn = psycopg2.connect(dbname="tpe_buildings")
cur = conn.cursor()
cur.execute("SELECT ST_AsText(ST_Extent(geom)) from buildings")
extent = loads(list(cur)[0][0]).bounds
print extent
# roughly 0.2 x 0.2 degrees
# create grid of 0.002 x 0.002 squares

#verify that sum of all tiles = # of buildings

#update buildings set col = floor((ST_X(ST_Centroid(geom))-121.45086028606)/0.002);
#update buildings set row = floor((ST_Y(ST_Centroid(geom))-24.9626010373178)/0.002);

def fname(tup):
  return "%03dX_%03dY" % tup

GRIDSIZE = 0.002
cur.execute("select distinct col,row from buildings order by row, col asc")

tasks = []
for task in cur:
  min_x = 121.45086028606 + task[0] * 0.002
  max_x = min_x + 0.002
  min_y = 24.9626010373178 + task[1] * 0.002
  max_y = min_y + 0.002
  tasks.append({
    'type':'Feature',
    'properties':{'filename':fname((task[0],task[1]))},
    'geometry': mapping(box(min_x, min_y, max_x, max_y))
  })

with open('tasks.geojson','w') as f:
  f.write(json.dumps({'type':'FeatureCollection','features':tasks}))

