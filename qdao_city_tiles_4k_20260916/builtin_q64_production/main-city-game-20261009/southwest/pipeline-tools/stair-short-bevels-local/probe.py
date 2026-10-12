from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent
S=R.parent/'crossedge-stair-restored-20261011'
orig=np.array(Image.open(S/'stair-combined/input.png').convert('RGB'))
base=np.array(Image.open(S/'stair-combined/premixed.png').convert('RGB'))
native=np.array(Image.open(S/'stair-lower-v01/native.png').convert('RGB'))
def edge(a,cy,l,rr):
 vals=np.abs(np.diff(a[cy-12:cy+13,l:rr].astype(float),axis=0)).mean(axis=(1,2))
 return int(np.argmax(vals))+cy-12
rows=[]
for wy,off in [(40507,3),(40734,-4)]:
 cy=wy-39320;ny=wy-39706
 for title,a,y in [('original',orig,cy),('base',base,cy),('native',native,ny),('translated',native,ny+off)]:
  Image.fromarray(a).crop([360,y-30,960,y+35]).save(R/f'{wy}-{title}.png')
 vals=[]
 for l,rr in [(420,480),(490,550),(560,620),(620,640),(640,700),(710,770),(790,850),(850,910)]:
  vals.append({'xBand':[l,rr],'originalEdge':39320+edge(orig,cy,l,rr),'nativeEdge':39706+edge(native,ny,l,rr),'translatedEdge':39706+edge(native,ny,l,rr)-off})
 rows.append({'worldY':wy,'offsetInSource':off,'measurements':vals})
(R/'probe.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))
