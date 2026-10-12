from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for action,i,v,note in [('cast',12,2,'近左符臂由前伸向胸前屈肘回收，中间手位已补；右剑臂和双脚站位保持。'),('attack',11,3,'远右持剑恢复向左上斜举，消除10→11→12横剑回跳；近左符臂保持。'),('hit',4,2,'受击最大后仰后的中间回弹，头身仍有后倾、眼神半恢复，双足保持支撑。')]:
 p=R/f'review/combat-{action}-W-selection.json';s=rd(p);f=s['frames'][i-1]
 src=R/f'drafts/{action}/W/{i:02}-v{v}.png';sgp=src.with_name(src.name+'.generation.json');sg=rd(sgp)
 out=R/f['path'];im=Image.open(src);im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
 gp=out.with_name(out.name+'.generation.json');g=rd(gp)
 g.update(sha256=sha(out),exportedAt=datetime.now(timezone.utc).isoformat(),generatedAt=sg['generatedAt'],nativeFrameSize=list(im.size),actualModel=None,actualQuality=None)
 g['derivedFrom']={'path':src.relative_to(R).as_posix(),'sha256':sha(src),'generationRecord':sgp.relative_to(R).as_posix(),'generationRecordSha256':sha(sgp)}
 wr(gp,g)
 f.update(sourcePath=src.relative_to(R).as_posix(),sourceSha256=sha(src),sha256=sha(out),sourceGenerationRecord=sgp.relative_to(R).as_posix(),nativeSize=list(im.size),notes=note,actualPhase=note)
 for z in s['frames']:
  if action=='cast':
   z['notes']=z.get('notes','').replace('11→12 talisman recovery is concentrated in one45ms transition, and03–07 wrist position varies around face/ear. These require normal-speed motion judgment.','12-v2 now provides a bent-elbow intermediate return from11 to13; 03–07 wrist position travels around face/ear.')
 s['latestLocalRepair']={'frame':i,'version':v,'observation':note,'nativeEdit':True,'posePixelTransform':False}
 s['artStatus']='static_sequence_reviewed_last_local_repairs_applied'
 s['remainingIssues']=['客户端世界坐标站位及无滑步尚未验证；画稿存在轻微头发衣摆变化。']
 wr(p,s)
 count=len(s['frames']);sheet=Image.new('RGB',(1024,284*((count+3)//4)),(39,54,65));d=ImageDraw.Draw(sheet)
 for k,z in enumerate(s['frames']):
  a=Image.open(R/z['sourcePath']).resize((256,256),Image.Resampling.LANCZOS);x=k%4*256;y=k//4*284
  sheet.paste(a,(x,y+28),a);d.text((x+4,y+4),f"{action}/W/{k+1:02} {Path(z['sourcePath']).stem}",fill='white')
 sheet.save(R/f'review/combat-{action}-W-contact-sheet.png')
print('Combat W three continuity repairs selected and exported')
