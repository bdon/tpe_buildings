import os
import json

from lxml import etree
from shapely.geometry import box, mapping

# Gather all directories from the root KML file.
root = etree.parse("kmzs/Taipei3DBuilding_nl.kml")
ns = { 'n':'http://www.opengis.net/kml/2.2' }

features = []

def xpatht(elem,query):
  return elem.xpath(query,namespaces=ns)[0].text

def xpathf(elem,query):
  return float(xpatht(elem,query))

for folder in root.xpath("/n:kml/n:Document/n:NetworkLink",namespaces=ns):
  folder_name = xpatht(folder,"n:name")
  print "Traversing folder " + folder_name
  folder_link = xpatht(folder,"n:Link/n:href").replace("\\","/")
  folder_root = etree.parse("kmzs/" + folder_link)
  for superregion in folder_root.xpath("/n:kml/n:Folder/n:NetworkLink",namespaces=ns):
    sr_name = xpatht(superregion,"n:name")
    print "Traversing super region " + sr_name
    sr_link  = xpatht(superregion,"n:Link/n:href").replace("\\","/")
    sr_north = xpathf(superregion,"n:Region/n:LatLonAltBox/n:north")
    sr_south = xpathf(superregion,"n:Region/n:LatLonAltBox/n:south")
    sr_east  = xpathf(superregion,"n:Region/n:LatLonAltBox/n:east")
    sr_west  = xpathf(superregion,"n:Region/n:LatLonAltBox/n:west")
    #print north, south, east, west, link, name
    sr_path = "kmzs/" + folder_name + "/" + sr_link
    sr_root = etree.parse(sr_path)
    for region in sr_root.xpath("/n:kml/n:Document/n:NetworkLink",namespaces=ns):
      # altitude?
      r_name = xpatht(region,"n:name")
      r_link  = xpatht(region,"n:Link/n:href").replace("\\","/")
      r_north = xpathf(region,"n:Region/n:LatLonAltBox/n:north")
      r_south = xpathf(region,"n:Region/n:LatLonAltBox/n:south")
      r_east  = xpathf(region,"n:Region/n:LatLonAltBox/n:east")
      r_west  = xpathf(region,"n:Region/n:LatLonAltBox/n:west")

      features.append({
        'type':'Feature',
        'properties': {
          'folder':folder_name,
          'superregion_name':sr_name,
          'r_name':r_name
        },
        'geometry':mapping(box(r_west,r_south,r_east,r_north))
      })

with open('regions.geojson','w') as f:
  f.write(json.dumps({'type':'FeatureCollection','features':features}))
