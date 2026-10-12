from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
items=[]
for direction,frame in [('E',1),('E',8),('E',9),('SE',8),('SE',9)]:
 stem=f'run-{direction}-{frame:02}-20261004-grounding-v2-01'
 rp=R/'records'/f'{stem}.json';receipt=json.loads((R/'records'/f'{stem}.receipt.json').read_text(encoding='utf-8-sig'))
 source=Path(receipt['nativePath']);dest=R/'work'/'root-ground-fix'/f'{stem}-native.png';shutil.copy2(source,dest)
 record=json.loads(rp.read_text(encoding='utf-8-sig'));im=Image.open(dest)
 record.update(status='generated_candidate_spatial_allocation_pending',native={'sourceFile':str(dest),'hostSource':str(source),'width':im.width,'height':im.height,'mode':im.mode,'sha256':sha(dest)},actualModel=None,actualQuality=None)
 rp.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 items.append({'direction':direction,'frame':frame,'nativePath':str(dest.relative_to(R)).replace('\\','/'),'nativeSha256':sha(dest),'record':str(rp.relative_to(R)).replace('\\','/'),'formalReplaced':False})
sheet=Image.new('RGB',(1280,560),(246,242,230));draw=ImageDraw.Draw(sheet)
for i,x in enumerate(items):
 for row,p in enumerate([R/'frames'/'run'/x['direction']/f"{x['frame']:02}.png",R/x['nativePath']]):
  im=Image.open(p).convert('RGBA').resize((248,248),Image.Resampling.LANCZOS)
  sheet.paste(im,(i*256,row*280+28),im);draw.text((i*256+12,row*280+8),f"{x['direction']} {x['frame']:02} / "+('current' if row==0 else 'candidate'),fill=(30,65,55))
sheet.save(R/'previews'/'grounding-new-keyposes-20261004.png')
(R/'reviews'/'grounding-v2-root-candidates.json').write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_keyposes_not_final','latestUserRequirement':'中间接地四帧，旁边接地各两帧；旁边具体空间方向已向用户确认，待回复。','frames':items},ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['tools/run-grounding-template.html','previews/run-grounding.html']:
 p=R/name;s=p.read_text(encoding='utf-8');s=s.replace('离线复核完成 · 客户端未接入','接地空间分配修订中 · 客户端未接入');p.write_text(s,encoding='utf-8')
print({'candidate_count':len(items),'formalReplaced':False,'preview':'previews/grounding-new-keyposes-20261004.png'})
