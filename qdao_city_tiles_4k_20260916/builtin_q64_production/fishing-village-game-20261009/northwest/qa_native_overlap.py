from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
from assemble_r03_c03 import minimum_vertical_seam
B=Path(__file__).resolve().parent
tile,name,dirs=sys.argv[1:4];w=B/('work-'+tile);q=w/'qa'/name;q.mkdir(parents=True,exist_ok=True)
native=np.asarray(Image.open(B/'native'/(name+'.png')).convert('RGB'));guide=np.asarray(Image.open(w/'guides'/(name+'.authoritative.png')).convert('RGB'));out=native.copy();records=[]
for direction in dirs:
 if direction=='n':old,new=guide[:230].transpose(1,0,2),native[:230].transpose(1,0,2)
 elif direction=='s':old,new=guide[-230:].transpose(1,0,2),native[-230:].transpose(1,0,2)
 elif direction=='w':old,new=guide[:,:230],native[:,:230]
 else:old,new=guide[:,-230:],native[:,-230:]
 seam,cost=minimum_vertical_seam(old,new);take=np.arange(230)[None,:]>=seam[:,None] if direction in 'nw' else np.arange(230)[None,:]<seam[:,None];mixed=np.where(take[...,None],new,old)
 if direction=='n':out[:230]=mixed.transpose(1,0,2)
 elif direction=='s':out[-230:]=mixed.transpose(1,0,2)
 elif direction=='w':out[:,:230]=mixed
 else:out[:,-230:]=mixed
 records.append({'direction':direction,'path':seam.tolist(),'cost':cost,'meanAbsoluteDifference':float(np.abs(old.astype(float)-new).mean()),'blend':False})
Image.fromarray(out).save(q/'native-with-overlap.png')
for direction in dirs:
 for i in range(2):
  lo=i*627;hi=(i+1)*627
  crop=out[:480,lo:hi] if direction=='n' else out[-480:,lo:hi] if direction=='s' else out[lo:hi,:480] if direction=='w' else out[lo:hi,-480:]
  Image.fromarray(crop).save(q/f'{direction}-{i+1}.100pct.png')
(q/'mechanical.json').write_text(json.dumps({'native':str(B/'native'/(name+'.png')),'guide':str(w/'guides'/(name+'.authoritative.png')),'purpose':'native-scale seam QA only; final provenance composed separately','directions':records},indent=2),encoding='utf-8');print(json.dumps({'qa':str(q),'seams':[{'direction':r['direction'],'meanAbsoluteDifference':r['meanAbsoluteDifference']} for r in records]}))
