import io
import re
import math
import json
from zipfile import ZipFile
from itertools import zip_longest
import glob
from lxml import etree
from pyproj import Proj

nskml = { 'n':'http://www.opengis.net/kml/2.2' }
nsdae = { 'n':'http://www.collada.org/2005/11/COLLADASchema' }
twd97 = Proj('epsg:3826')
inch_to_meters = 0.0254

all_feats = []

def grouper(n, iterable, padvalue=None):
  "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
  return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

def xpath(elem,query,ns):
  return elem.xpath(query,namespaces=ns)

def xpatht(elem,query,ns):
  return xpath(elem,query,ns)[0].text

def xpathf(elem,query,ns):
  return float(xpatht(elem,query,ns))

def makeShape(l,height,lon,lat):
  def unproject_twd97(x,y):
    x_meters = x * inch_to_meters
    y_meters = y * inch_to_meters
    # convert the model origin to TWD97
    x0,y0 = twd97(lon,lat)
    return twd97(x0 + x_meters,y0+y_meters,inverse=True)
  if len(l) < 4:
    return
  geog = [unproject_twd97(*p) for p in l]
  all_feats.append({'type':'Feature','properties':{'height':height*inch_to_meters},'geometry':{'coordinates':[geog],'type':'Polygon'}})

def region2features(region):
  features = []
  m = re.search('/([\d_r]+).kmz',region)
  kml_name = m.group(1) + ".kml"
  with ZipFile(region,'r') as myzip:
    root = etree.parse(myzip.open(kml_name))
    for placemark in xpath(root,"n:Document/n:Placemark",nskml):
      name = xpatht(placemark,"n:name",nskml)
      lon = xpathf(placemark,"n:Model/n:Location/n:longitude",nskml)
      lat = xpathf(placemark,"n:Model/n:Location/n:latitude",nskml)
      link = xpatht(placemark,"n:Model/n:Link/n:href",nskml)
      xml = myzip.open(link)
      model = etree.parse(xml)
      inst_geom = model.find('.//{http://www.collada.org/2005/11/COLLADASchema}instance_geometry')
      #for inst_geom in model.findall('.//{http://www.collada.org/2005/11/COLLADASchema}instance_geometry'):
      geom_url = inst_geom.get('url')[1:]
      geom = model.find(".//{http://www.collada.org/2005/11/COLLADASchema}geometry[@id='" + geom_url + "']")
      # the first oen is a mesh
      vals = [float(v) for v in geom.findtext(".//{http://www.collada.org/2005/11/COLLADASchema}float_array").split(' ') if len(v) > 0]
      points = list(grouper(3,vals))

      triindexes = [int(v) for v in geom.findtext(".//{http://www.collada.org/2005/11/COLLADASchema}triangles/{http://www.collada.org/2005/11/COLLADASchema}p").split(' ') if len(v) > 0]
      tris = list(grouper(3,(triindexes[::2])))

      # the first geom is always the "roof planar set of triangles"
      height = points[tris[0][0]][2]
      for tri in tris:
        assert points[tri[0]][2] == height

      makeShape([(p[0],p[1]) for p in points], height,lon,lat)

if __name__ == '__main__':
  for d in glob.glob('kmzs/*'):
    dirname = d[5:9]
    for thing in glob.glob('kmzs/'+dirname+'/*.kmz'):
      region2features(thing)
  print(json.dumps({'type':'FeatureCollection','features':all_feats}))

