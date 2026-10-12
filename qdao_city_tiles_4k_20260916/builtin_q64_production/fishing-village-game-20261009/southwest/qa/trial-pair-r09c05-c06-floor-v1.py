import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];QA=Z/'qa'
def mod(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=mod('pair_floor_trial',QA/'repair-compose.py');h=mod('helper',Z/'tools/seam_helpers.py')
a=np.asarray(Image.open(QA/'pair-r09c05-c06-floor-source-native-v1.png').convert('RGB'));b=np.asarray(Image.open(Z/'native/r09_c05_c06_floor_join_repair_v1.png').convert('RGB'))
bounds=[330,285,925,885];margin=60
mask,paths=c.closed_mask(a,b,bounds,margin,[3585,2305,4839,3559],h._minimum_vertical_seam);after=np.where(mask.astype(bool)[:,:,None],b,a)
out=QA/'pair-r09c05-c06-floor-v1-trial-100pct.png';assert not out.exists();Image.fromarray(after).save(out);np.save(QA/'pair-r09c05-c06-floor-v1-trial-mask.npy',mask)
(QA/'pair-r09c05-c06-floor-v1-trial.json').write_text(json.dumps({'bounds':bounds,'margin':margin,'paths':paths,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'nativePixelsResampled':False},indent=2)+'\n',encoding='utf-8')
