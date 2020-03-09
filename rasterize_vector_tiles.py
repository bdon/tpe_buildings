import glob
from sphericalmercator import SphericalMercator
import os
import re
import subprocess

merc = SphericalMercator(levels=16, size=256)
pattern = re.compile("(\\d+)/(\\d+)/(\\d+).pbf")
cwd = os.getcwd()

for x in glob.glob('tiles/**/**/**.pbf'):
    result = pattern.search(x)
    grp = result.groups(0)
    z = int(grp[0])
    x = int(grp[1])
    y = int(grp[2])
    env = merc.xyz_to_envelope(x=x,y=y,zoom=z)
    center = ((env[0]+env[2])/2.0,(env[1]+env[3])/2.0)
    subprocess.check_call(['mbgl-render','--style','buildinglabels.json','--lon',str(center[0]),'--lat',str(center[1]),'--zoom',str(z),'--output',"rasterized/{0}_{1}_{2}.png".format(z,x,y),'--assets',cwd])
