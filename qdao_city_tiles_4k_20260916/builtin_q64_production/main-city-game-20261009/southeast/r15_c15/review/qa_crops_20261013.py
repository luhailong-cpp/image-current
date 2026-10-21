from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c15')
L=json.loads((T/'candidate/latest-assembly.json').read_text())
I=Image.open(L['candidate']['path']).convert('RGB')
R=T/'review/assembly-008f4b817c43676ebb32/native-segments'
R.mkdir(exist_ok=True)
e=[]
def save(name,im,box,kind):
 p=R/(name+'.png');assert not p.exists();im.save(p);e.append({'name':name,'path':str(p),'box':box,'kind':kind,'size':list(im.size)})
for edge in ['north','south','east','west']:
 for q in range(4):
  a,b=q*1024,(q+1)*1024
  box={'north':[a,0,b,320],'south':[a,3776,b,4096],'east':[3776,a,4096,b],'west':[0,a,320,b]}[edge]
  save(f'{edge}-q{q}',I.crop(box),box,'core-edge')
for pos in [1024,2048,3072]:
 for q in range(4):
  a,b=q*1024,(q+1)*1024
  for axis in ['v','h']:
   box=[pos-200,a,pos+200,b] if axis=='v' else [a,pos-200,b,pos+200]
   save(f'{axis}{pos}-q{q}',I.crop(box),box,'internal-seam')
for edge,n in [('north','r14_c15'),('west','r15_c14')]:
 L2=json.loads((T.parent/n/'candidate/latest-assembly.json').read_text());N=Image.open(L2['candidate']['path']).convert('RGB')
 for q in range(4):
  a,b=q*1024,(q+1)*1024
  if edge=='north':
   C=Image.new('RGB',(1024,400));C.paste(N.crop((a,3896,b,4096)),(0,0));C.paste(I.crop((a,0,b,200)),(0,200));box=[a,-200,b,200]
  else:
   C=Image.new('RGB',(400,1024));C.paste(N.crop((3896,a,4096,b)),(0,0));C.paste(I.crop((0,a,200,b)),(200,0));box=[-200,a,200,b]
  save(f'external-{edge}-q{q}',C,box,'formal-core-only-neighbor-seam')
 (R/(edge+'-neighbor-source.json')).write_text(json.dumps(L2,indent=2))
(R/'crop-index.json').write_text(json.dumps({'candidate':L['candidate'],'crops':e},indent=2))
print(len(e))
