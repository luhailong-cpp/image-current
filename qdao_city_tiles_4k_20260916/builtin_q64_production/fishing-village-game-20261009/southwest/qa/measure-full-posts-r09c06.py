import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parents[1]; im=Image.open(Z/'qa/full-tile-r09_c06-context-native.png')
boxes={'a-upper-posts-measure-top':[500,-115,1100,535], 'a-upper-posts-measure-bottom':[500,735,1100,1235], 'b-centerpost-measure-top':[1820,300,2180,800], 'b-centerpost-measure-bottom':[1820,2400,2180,2800]}
for name,b in boxes.items():
 p=Z/'qa'/('repair-r09_c06-'+name+'-100pct.png'); assert not p.exists(); im.crop(tuple(v+115 for v in b)).save(p)
 print(name,b)
