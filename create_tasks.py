import psycopg2
import json
from shapely.wkb import loads
from shapely.geometry import box, mapping

conn = psycopg2.connect(dbname="tpe_buildings")
cur = conn.cursor()

def fname(tup):
  return "%03dX_%03dY" % tup

current_task = None
current_buildings = []
cur.execute("select col, row, id, ST_AsBinary(geom), height from buildings order by (col, row) asc")
for building in cur:
  task = (building[0],building[1])
  if current_task and current_task != task:
    with open('tasks/' + fname(current_task) + '.geojson','w') as f:
      f.write(json.dumps({'type':'FeatureCollection','features':current_buildings}))
    current_buildings = []
  current_task = task
  current_buildings.append({
    'type':'Feature',
    'properties':{'height':building[4]},
    'id':building[2],
    'geometry':mapping(loads(str(building[3])))
  })





