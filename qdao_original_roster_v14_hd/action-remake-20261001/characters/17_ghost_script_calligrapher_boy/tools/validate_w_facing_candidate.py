from pathlib import Path
from PIL import Image
import json,hashlib,sys
b=Path(__file__).resolve().parents[1]
for key in sys.argv[1:]:
 p=b/'staging'/f'{key}.png';im=Image.open(p).convert('RGBA');row={}
 for label,img in [('native',im),('export1024',im.resize((1024,1024),Image.Resampling.LANCZOS))]:
  a=img.getchannel('A');w,h=img.size;row[label]={}
  for name,box in [('top',(0,0,w,1)),('bottom',(0,h-1,w,h)),('left',(0,0,1,h)),('right',(w-1,0,w,h))]:
   vals=list(a.crop(box).getdata());row[label][name]={'maxAlpha':max(vals),'above128':sum(v>128 for v in vals)}
 rp=p.with_suffix('.png.generation.json');r=json.loads(rp.read_text(encoding='utf-8-sig'));r['evidence']['toolResultFile']=f'provenance/{key}.tool-result.json'
 for x in r['references']:x['sha256']=hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()
 first=Path(r['references'][0]['path']);r['editSource']={'file':first.relative_to(b).as_posix(),'sha256':hashlib.sha256(first.read_bytes()).hexdigest()}
 r['validation']=row;rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'key':key,'sha256':r['sha256'],'nativeSize':[im.width,im.height],'edges':row},ensure_ascii=False))
