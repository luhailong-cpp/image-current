from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14");m=json.loads((T/'candidate/latest-assembly.json').read_text());im=Image.open(m['candidate']['path']).convert('RGB')
q=T/'review/full-internal-20261011';q.mkdir(exist_ok=True)
record={'candidate':m['candidate'],'fullSeamBands':[],'junctions':[],'previewOnlyDownsampled':'overview-preview-only.png'}
im.resize((1024,1024),Image.Resampling.LANCZOS).save(q/'overview-preview-only.png')
for axis in ['v','h']:
 for k,c in enumerate([1024,2048,3072],1):
  b=(c-128,0,c+128,4096) if axis=='v' else (0,c-128,4096,c+128)
  band=im.crop(b);f=q/(axis+str(k)+'-full100pct.png');band.save(f)
  segments=[]
  for s in range(4):
   bb=(0,s*1024,256,(s+1)*1024) if axis=='v' else (s*1024,0,(s+1)*1024,256)
   sf=q/(axis+str(k)+'-segment'+str(s)+'-100pct.png');band.crop(bb).save(sf);segments.append(str(sf))
  record['fullSeamBands'].append({'axis':axis,'coordinate':c,'cropInCore':b,'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'segments':segments})
for row,y in enumerate([1024,2048,3072],1):
 for col,x in enumerate([1024,2048,3072],1):
  b=(x-192,y-192,x+192,y+192);f=q/(f'junction-{row}-{col}-100pct.png');im.crop(b).save(f);record['junctions'].append({'cropInCore':b,'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(q/'qa-source-manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(m['candidate']['sha256'])

