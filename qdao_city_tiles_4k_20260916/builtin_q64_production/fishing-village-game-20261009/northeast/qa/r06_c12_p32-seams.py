from pathlib import Path
from PIL import Image
import json,hashlib,sys
z=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
name,topname,leftname=sys.argv[1:4]
target=Image.open(z/'native'/f'{name}.png').convert('RGB')
for side,othername in [('top',topname),('left',leftname)]:
 other=Image.open(z/'native'/f'{othername}.png').convert('RGB')
 if side=='top':
  out=Image.new('RGB',(1024,512))
  out.paste(other.crop((115,883,1139,1139)),(0,0))
  out.paste(target.crop((115,115,1139,371)),(0,256))
 else:
  out=Image.new('RGB',(512,1024))
  out.paste(other.crop((883,115,1139,1139)),(0,0))
  out.paste(target.crop((115,115,371,1139)),(256,0))
 p=z/'qa'/f'{name}-{side}-seam.png'
 out.save(p)
 record={'file':str(p),'sha256':sha(p),'operation':'1:1 crop and opaque paste of 256px strips along 1024 core boundary; no scaling, blending or painting','derivedFrom':[{'path':str(z/'native'/f'{s}.png'),'sha256':sha(z/'native'/f'{s}.png'),'generationRecord':str(z/'native'/f'{s}.png.generation.json')} for s in [othername,name]],'purpose':'100% native seam QA only, not final game art'}
 Path(str(p)+'.derived.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 print(str(p))

