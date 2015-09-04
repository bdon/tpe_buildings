import StringIO
import re
import math
import json
from zipfile import ZipFile

import glob

import numpy as np
from lxml import etree
from collada import Collada
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union, transform
from pyproj import Proj
import psycopg2

from util import xpath, xpatht, xpathf

ns = {'c':"http://www.collada.org/2005/11/COLLADASchema"}

conn = psycopg2.connect(dbname='tpe_buildings')
cur = conn.cursor()
inch_to_meters = 0.0254

def repairDAE(model):
  #for s in model.xpath("//c:mesh/c:source",namespaces=ns):
  #  fa_node = s.xpath("c:float_array",namespaces=ns)[0]
  #  vertex_count = len(fa_node.text.split(" "))
  #  fa_node.attrib['count'] = str(vertex_count)
  #  acc_node = s.xpath("c:technique_common/c:accessor",namespaces=ns)[0]
  #  acc_node.attrib['count'] = str(vertex_count / 3)

  # malformed DAE - delete normals, we don't need them anyways.
  for i in model.xpath("//c:input[@semantic='NORMAL']",namespaces=ns):
    i.getparent().remove(i)


def region2features(region):
  features = []
  print region
  # 1_4741
  m = re.search('/([\d_r]+).kmz',region)
  kml_name = m.group(1) + ".kml"
  with ZipFile(region,'r') as myzip:
    root = etree.parse(myzip.open(kml_name))
    for placemark in xpath(root,"n:Document/n:Placemark"):
      name = xpatht(placemark,"n:name")
      lon = xpathf(placemark,"n:Model/n:Location/n:longitude")
      lat = xpathf(placemark,"n:Model/n:Location/n:latitude")
      link = xpatht(placemark,"n:Model/n:Link/n:href")
      # assert location transformation is identity
      xml = myzip.open(link)
      model = etree.parse(xml)
      repairDAE(model)
      c = Collada(StringIO.StringIO(etree.tostring(model)))

      tris = []
      height = None
      for geom in c.geometries:
        assert len(geom.primitives) == 1
        triset = geom.primitives[0]
        heights = np.unique(np.hstack([[point[2] for point in tri] for tri in triset.vertex[triset.vertex_index]]))
        if len(heights) == 1:
          height = float(heights[0]) * inch_to_meters
          # the mesh is parallel to the xy plane
          for tri in triset.vertex[triset.vertex_index]:
            tri_p = Polygon([(tri[0][0],tri[0][1]),(tri[1][0],tri[1][1]),(tri[2][0],tri[2][1])])
            tris.append(tri_p)

      def r(t):
        try:
          if t.area > 0:
            return True
        except:
          pass
        return False

      valid_tris = filter(r,tris)
      footprint = unary_union(valid_tris)
      assert height is not None

      # http://spatialreference.org/ref/epsg/3826/html/
      twd97 = Proj(init='epsg:3826')

      def unproject_twd97(x,y):
        x_meters = x * inch_to_meters
        y_meters = y * inch_to_meters
        # convert the model origin to TWD97
        x0,y0 = twd97(lon,lat)
        return twd97(x0 + x_meters,y0+y_meters,inverse=True)

      unprojected = transform(unproject_twd97,footprint)
      cur.execute("INSERT INTO buildings(id, geom, height) VALUES (%s,ST_SetSRID(%s::geometry,4326),%s)",(name,unprojected.wkt,height))
      conn.commit()
  return features

if __name__ == '__main__':
  for d in glob.glob('kmzs/*'):
    dirname = d[5:9]
    for thing in glob.glob('kmzs/'+dirname+'/*.kmz'):
      region2features(thing)
