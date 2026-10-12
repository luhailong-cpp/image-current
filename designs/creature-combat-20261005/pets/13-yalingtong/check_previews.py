from pathlib import Path
import struct,json
from PIL import Image
R=Path(__file__).resolve().parent
rows=[];errors=[]
for a,(count,ms) in {'hit':(6,40),'attack':(12,30),'cast':(16,45)}.items():
 for d in 'EW':
  for mode,mul in [('normal',1),('slow',4)]:
   p=R/f'preview/{a}-{d}-{mode}.webp'
   if not p.exists():errors.append(str(p));continue
   data=p.read_bytes();offset=12;dur=[]
   while offset+8<=len(data):
    tag=data[offset:offset+4];size=struct.unpack('<I',data[offset+4:offset+8])[0];payload=data[offset+8:offset+8+size]
    if tag==b'ANMF':dur.append(int.from_bytes(payload[12:15],'little'))
    offset+=8+size+(size%2)
   im=Image.open(p);row={'file':p.relative_to(R).as_posix(),'size':list(im.size),'frames':im.n_frames,'durationsMs':dur,'expectedDurationMs':ms*mul};rows.append(row)
   if im.n_frames!=count or dur!=[ms*mul]*count or im.size!=(512,512):errors.append('animation contract '+str(p))
result={'passed':not errors,'errors':errors,'previews':rows,'note':'WebP/HTML previews are supporting outputs; 1024 RGBA PNGs are the runtime assets.'}
(R/'preview-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'passed':result['passed'],'errors':errors,'previewCount':len(rows)}))
