ns = { 'n':'http://www.opengis.net/kml/2.2' }

def xpath(elem,query):
  return elem.xpath(query,namespaces=ns)

def xpatht(elem,query):
  return xpath(elem,query)[0].text

def xpathf(elem,query):
  return float(xpatht(elem,query))
