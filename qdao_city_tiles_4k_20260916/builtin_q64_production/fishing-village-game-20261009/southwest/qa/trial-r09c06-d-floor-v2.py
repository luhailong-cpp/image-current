import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
Z=Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=load('rep',Z/'qa/repair-compose.py');h=load('help',Z/'tools/seam_helpers.py')
a=np.asarray(Image.open(Z/'qa/repair-r09_c06-d-floor-source-native-v2.png').convert('RGB'));b=np.asarray(Image.open(Z/'native/r09_c06_repair_d_floor_v2.png').convert('RGB'))
bounds=[285,560,875,1180];margin=45
mask,paths=c.closed_mask(a,b,bounds,margin,[2715,2955,3969,4209],h._minimum_vertical_seam)
after=np.where(mask.astype(bool)[:,:,None],b,a)
stem=Z/'qa/repair-r09_c06-d-floor-v2-wide-trial'; assert not stem.with_suffix('.png').exists()
Image.fromarray(after).save(stem.with_suffix('.png'));np.save(stem.with_suffix('.npy'),mask)
stem.with_suffix('.json').write_text(json.dumps({'bounds':bounds,'margin':margin,'paths':paths,'outputSha256':hashlib.sha256(stem.with_suffix('.png').read_bytes()).hexdigest(),'maskSha256':hashlib.sha256(stem.with_suffix('.npy').read_bytes()).hexdigest(),'nativePixelsResampled':False},indent=2)+'\n',encoding='utf-8')
print(str(stem.with_suffix('.png')))
