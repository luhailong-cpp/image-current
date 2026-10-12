from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
from PIL import Image,ImageDraw,ImageFont
ROLE=Path(__file__).resolve().parent.parent
maps={'hit':['01-v2','02-v2','03-v3','04-v1','05-v1','06-v1'],'attack':['01-v2','02-v1','03-v1','04-v1','05-v2','06-v1','07-v1','08-v1','09-v1','10-v1','11-v1','12-v1'],'cast':['01-v3','02-v1','03-v1','04-v1','05-v1','06-v2','07-v3','08-v4','06-v1','10-v3','11-v1','12-v1','13-v1','10-v1','15-v1','16-v2']}
plans=json.loads((ROLE/'review/combat-E-phase-plan.json').read_text(encoding='utf8'))['frames']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',12)
all_checks=[]
for action,stems in maps.items():
 frames=[];duration={'hit':40,'attack':30,'cast':45}[action];event={'hit':1,'attack':6,'cast':9}[action]
 for slot,stem in enumerate(stems,1):
  source=ROLE/'generation'/action/'E'/(stem+'.png');im=Image.open(source)
  rev=json.loads(source.with_suffix('.review.json').read_text(encoding='utf8'))
  gen=json.loads(Path(str(source)+'.generation.json').read_text(encoding='utf8'))
  sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==gen['sha256'] and im.mode=='RGBA' and min(im.size)>=1024
  issues=rev['issues'].copy()
  if action=='cast' and slot==9:issues.append('源文件命名06，实际是完整释放，唯一选用于09；来源编号未伪改。')
  if action=='cast' and slot==14:issues.append('源文件命名10，实际是收势，唯一选用于14；来源编号未伪改。')
  frames.append(dict(slot=slot,source=source.relative_to(ROLE).as_posix(),sourceSha256=sha,observedPhase=rev['observedPhase'],plannedPhase=('释放前短回收聚势，再接09伸出' if action=='cast' and slot==8 else plans[action][slot-1]['phase']),issues=issues,durationMs=duration,review=source.with_suffix('.review.json').relative_to(ROLE).as_posix(),generationRecord=Path(str(source)+'.generation.json').relative_to(ROLE).as_posix(),visualAccepted=False))
 assert len(set(f['sourceSha256'] for f in frames))==len(frames)
 group=dict(schemaVersion=1,action=action,direction='E',status='candidate_not_accepted',visualAccepted=False,clientVerified=False,dynamicAccepted=False,nativeRoot=[800,1164],canvas=[1254,1254],rootMeaning='固定画布诊断坐标；未按帧移动、缩放、最低alpha贴地；整组尚未标定验收。',eventFrame=event,eventTime=(event-1)*duration,eventTimeMs=(event-1)*duration,eventAccepted=False,totalDurationMs=duration*len(frames),frames=frames,issues=['全套仍为候选，未进行客户端事件/节奏/方向/接地验收。','部分双鞋朝向偏三分之四、宽站姿；鞋尖/膝/踝需同平面复核。','头身/道具存在AI逐帧漂移；固定画布未经逐帧配准。']+({'hit':['03-v3受力峰值更明确；部分胸口偏向观众，支撑像素仍有漂移。'],'attack':['06灯距右边缘约5px；07灯穗低于诊断地面；后段回收路径仍需动态确认。'],'cast':['08已修胸前瓶，实际为释放前短回收；12灯碗缩小；低垂灯穗接近鞋，动作固定根点待标定。']}[action]),actualModel=None,actualQuality=None,createdAtUtc=datetime.now(timezone.utc).isoformat())
 out=ROLE/'review'/f'{action}-E-sequence-input.json';out.write_text(json.dumps(group,ensure_ascii=False,indent=2),encoding='utf8')
 cols=3 if action=='hit' else 4;rows=math.ceil(len(frames)/cols);w=cols*272;h=56+rows*302
 sheet=Image.new('RGB',(w,h),(30,34,41));draw=ImageDraw.Draw(sheet)
 draw.text((12,8),f'{action.upper()} E | {len(frames)} slots | {group["totalDurationMs"]}ms | WIP 未验收',font=font,fill='white')
 draw.text((12,32),'整画布等比缩略，仅诊断；无逐帧对齐；固定参考线 y1164',font=small,fill=(220,180,100))
 for i,f in enumerate(frames):
  x=(i%cols)*272+8;y=56+(i//cols)*302
  draw.rectangle((x,y,x+255,y+255),fill=(56,61,70))
  im=Image.open(ROLE/f['source']);thumb=im.resize((256,256),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb)
  gy=y+round(1164/1254*256);draw.line((x,gy,x+255,gy),fill=(135,180,160),width=1)
  draw.text((x,y+260),f'{i+1:02d} / {Path(f["source"]).stem} / {duration}ms',font=small,fill='white')
  draw.text((x,y+277),f['plannedPhase'],font=small,fill=(220,210,170))
 cp=ROLE/'review'/f'{action}-E-contact.png';sheet.save(cp)
 all_checks.append(dict(action=action,slots=len(frames),allUnique=True,nativeRGBA=True,totalDurationMs=group['totalDurationMs'],eventTimeMs=group['eventTimeMs'],input=out.relative_to(ROLE).as_posix(),contact=cp.relative_to(ROLE).as_posix(),contactSha256=hashlib.sha256(cp.read_bytes()).hexdigest(),contactOperation='diagnostic contact sheet; uniform full-canvas resize only; source PNGs not modified'))
(ROLE/'review/combat-E-technical-verification.json').write_text(json.dumps(dict(checkedAtUtc=datetime.now(timezone.utc).isoformat(),checks=all_checks,sourcePNGModified=False,browserTest=False,clientTest=False,visualAccepted=False),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(all_checks,ensure_ascii=False))

