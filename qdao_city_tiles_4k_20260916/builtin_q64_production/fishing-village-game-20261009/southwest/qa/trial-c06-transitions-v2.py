import sys
sys.dont_write_bytecode=True
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest");q=z/'qa'
def mod(p,n):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
f=mod(q/'repair-compose.py','repairtrial');h=mod(z/'tools/seam_helpers.py','helpertrial')
m=json.loads((q/'repair-r09_c06-v1.manifest.json').read_text(encoding='utf-8-sig'))
for group in ['a','b']:
 rows=[r for r in m['repairs'] if r['id'].startswith(group+'-')]
 cur=np.array(Image.open(rows[0]['source']['path']).convert('RGB'))
 for r in rows:
  p=r['repair']['path']
  if r['id'] in ['a-upper-left-post','a-upper-rail-face','b-upper-center-post','b-lower-center-post']:p=p.replace('_v1.png','_v2.png')
  new=np.array(Image.open(p).convert('RGB'));mask,_=f.closed_mask(cur,new,r['repairBounds'],r['margin'],r['contextBox'],h._minimum_vertical_seam)
  cur=np.where(mask[:,:,None].astype(bool),new,cur)
 path=q/f'repair-r09_c06-{group}-transition-v2-trial-100pct.png';Image.fromarray(cur).save(path)
 print(path)

