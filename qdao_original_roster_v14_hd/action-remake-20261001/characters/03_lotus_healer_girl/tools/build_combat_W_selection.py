from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
from PIL import Image,ImageDraw,ImageFont
ROLE=Path(__file__).resolve().parent.parent
maps={'hit':['01-v1','02-v1','03-v1','04-v1','05-v1','06-v1'],'attack':['01-v2','02-v1','03-v1','04-v1','05-v1','06-v1','07-v1','08-v1','09-v1','10-v3','11-v1','12-v1'],'cast':['01-v1','02-v1','03-v3','04-v1','05-v2','08-v1','06-v1','07-v1','05-v1','10-v1','11-v1','12-v2','13-v1','14-v1','15-v1','16-v1']}
plans=json.loads((ROLE/'review/combat-W-phase-plan.json').read_text(encoding='utf8'))['frames']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',12)
all_checks=[]
for action,stems in maps.items():
 frames=[];duration={'hit':40,'attack':30,'cast':45}[action];event={'hit':1,'attack':6,'cast':9}[action]
 for slot,stem in enumerate(stems,1):
  source=ROLE/'generation'/action/'W'/(stem+'.png');im=Image.open(source)
  rev=json.loads(source.with_suffix('.review.json').read_text(encoding='utf8'));gen=json.loads(Path(str(source)+'.generation.json').read_text(encoding='utf8'))
  sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==gen['sha256'] and im.mode=='RGBA' and min(im.size)>=1024
  issues=rev['issues'].copy()
  if action=='cast' and slot in (6,7,8,9):issues.append(f'按实际腕/灯位置选序：源编号{stem}唯一用于槽{slot:02d}；来源prompt编号保留，不冒充原计划命中。')
  frames.append(dict(slot=slot,source=source.relative_to(ROLE).as_posix(),sourceSha256=sha,observedPhase=rev['observedPhase'],plannedPhase=plans[action][slot-1]['phase'],issues=issues,durationMs=duration,review=source.with_suffix('.review.json').relative_to(ROLE).as_posix(),generationRecord=Path(str(source)+'.generation.json').relative_to(ROLE).as_posix(),visualAccepted=False))
 assert len(set(f['sourceSha256'] for f in frames))==len(frames)
 group=dict(schemaVersion=1,action=action,direction='W',status='candidate_not_accepted',visualAccepted=False,clientVerified=False,dynamicAccepted=False,nativeRoot=[610,1179],canvas=[1254,1254],rootMeaning='沿用W关键帧的固定画布诊断坐标；未按帧移动、缩放、最低alpha贴地，动作固定根点尚待整组标定。不是E镜像根点。',eventFrame=event,eventTime=(event-1)*duration,eventTimeMs=(event-1)*duration,eventAccepted=False,totalDurationMs=duration*len(frames),frames=frames,issues=['候选完整不代表方向、支撑、节奏或客户端事件验收。','脚位、头发、道具存在逐帧AI重画差异；没有程序逐帧配准。']+({'hit':['03有明确后仰/屈膝峰值；03→04回弹幅度较大，240ms节奏待动态验收。'],'attack':['07后跟抬起、左前掌落地，斜轴可由俯仰解释，未见足够证据断定水平外撇；后鞋位置仍有漂移。','05发尾距右边缘约6px；04–06出手幅度/06事件150ms待动态检查。'],'cast':['06/07/08/09按实际相位唯一重排；原05-v1实际高举峰值选入09。','12-v2局部恢复灯体量，视觉宽略大于13；13–16灯收势有外内小摆，尚未动态验收。']}[action]),actualModel=None,actualQuality=None,createdAtUtc=datetime.now(timezone.utc).isoformat())
 out=ROLE/'review'/f'{action}-W-sequence-input.json';out.write_text(json.dumps(group,ensure_ascii=False,indent=2),encoding='utf8')
 cols=3 if action=='hit' else 4;rows=math.ceil(len(frames)/cols);w=cols*272;h=56+rows*302
 sheet=Image.new('RGB',(w,h),(30,34,41));draw=ImageDraw.Draw(sheet)
 draw.text((12,8),f'{action.upper()} W | {len(frames)} slots | {group["totalDurationMs"]}ms | WIP 未验收',font=font,fill='white')
 draw.text((12,32),'整画布等比缩略，仅诊断；动作根点未标定，参考线 y1179',font=small,fill=(220,180,100))
 for i,f in enumerate(frames):
  x=(i%cols)*272+8;y=56+(i//cols)*302
  draw.rectangle((x,y,x+255,y+255),fill=(56,61,70))
  im=Image.open(ROLE/f['source']);thumb=im.resize((256,256),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb)
  gy=y+round(1179/1254*256);draw.line((x,gy,x+255,gy),fill=(135,180,160),width=1)
  draw.text((x,y+260),f'{i+1:02d} / {Path(f["source"]).stem} / {duration}ms',font=small,fill='white')
  draw.text((x,y+277),f['plannedPhase'],font=small,fill=(220,210,170))
 cp=ROLE/'review'/f'{action}-W-contact.png';sheet.save(cp)
 all_checks.append(dict(action=action,slots=len(frames),allUnique=True,nativeRGBA=True,totalDurationMs=group['totalDurationMs'],eventTimeMs=group['eventTimeMs'],input=out.relative_to(ROLE).as_posix(),inputSha256=hashlib.sha256(out.read_bytes()).hexdigest(),contact=cp.relative_to(ROLE).as_posix(),contactSha256=hashlib.sha256(cp.read_bytes()).hexdigest(),contactOperation='diagnostic contact sheet; uniform full-canvas resize only; source PNGs not modified'))
(ROLE/'review/combat-W-technical-verification.json').write_text(json.dumps(dict(checkedAtUtc=datetime.now(timezone.utc).isoformat(),checks=all_checks,sourcePNGModified=False,browserTest=False,clientTest=False,visualAccepted=False),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(all_checks,ensure_ascii=False))

