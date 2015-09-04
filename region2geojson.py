from zipfile import ZipFile
from lxml import etree
from util import xpath, xpatht, xpathf
from collada import Collada
from collada.common import DaeMalformedError, DaeBrokenRefError
import StringIO
import re
import numpy as np

from shapely.geometry import Polygon
from shapely.ops import unary_union

region = 'kmzs/3357/3156_r14.kmz'

ns = {'c':"http://www.collada.org/2005/11/COLLADASchema"}

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

with ZipFile(region,'r') as myzip:
  root = etree.parse(myzip.open("3156_r14.kml"))
  for placemark in xpath(root,"n:Document/n:Placemark"):
    name = xpatht(placemark,"n:name")
    lon = xpathf(placemark,"n:Model/n:Location/n:longitude")
    lat = xpathf(placemark,"n:Model/n:Location/n:latitude")
    link = xpatht(placemark,"n:Model/n:Link/n:href")
    print name, lon, lat, link
    # assert location transformation is identity
    xml = myzip.open(link)
    model = etree.parse(xml)
    repairDAE(model)
    c = Collada(StringIO.StringIO(etree.tostring(model)))

    tris = []
    for geom in c.geometries:
      assert len(geom.primitives) == 1
      triset = geom.primitives[0]
      if len(np.unique(np.hstack([[point[2] for point in tri] for tri in triset.vertex[triset.vertex_index]]))) == 1:
        # the mesh is parallel to the xy plane
        for tri in triset.vertex[triset.vertex_index]:
          tris.append(Polygon([(tri[0][0],tri[0][1]),(tri[1][0],tri[1][1]),(tri[2][0],tri[2][1])]))
    footprint = unary_union(tris)
    print footprint

