import glob
import mercantile
import os
import re
import subprocess
import pathlib
from PIL import Image

pattern = re.compile("(\\d+)/(\\d+)/(\\d+).pbf")
cwd = os.getcwd()

def renderTile(x,y,z):
    env = mercantile.bounds(x,y,z)
    center = ((env.west+env.east)/2.0,(env.north+env.south)/2.0)

    folder = "raster_tiles/{0}/{1}".format(z,x)
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    subprocess.check_call(
        ['mbgl-render',
        '--style','buildinglabels.json',
        '--lon',str(center[0]),
        '--lat',str(center[1]),
        '--zoom',str(z),
        '--output',folder+"/{0}.png".format(y),
        '--assets',cwd])


def renderChildren(x,y,z,maxzoom):
    if z >= maxzoom:
        return
    for child in mercantile.children(x,y,z):
        renderTile(child.x,child.y,child.z)
        renderChildren(child.x,child.y,child.z,maxzoom)

for x in glob.glob('vector_tiles_uncompressed/**/**/**.pbf'):
    result = pattern.search(x)
    grp = result.groups(0)
    z = int(grp[0])
    x = int(grp[1])
    y = int(grp[2])
    renderTile(x,y,z)

    if z == 14:
        renderChildren(x,y,z,16)

