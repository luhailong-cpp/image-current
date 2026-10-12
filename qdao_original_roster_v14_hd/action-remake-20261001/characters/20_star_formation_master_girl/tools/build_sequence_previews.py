from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
selection=json.loads((ROOT/'selection.json').read_text(encoding='utf-8-sig'))
delivered=selection.get('status')=='offline_delivery'
label='离线交付' if delivered else '候选，动态待审'
specs={'run':(16,60),'hit':(6,40),'attack':(12,30),'cast':(16,45)}
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
groups={}
for e in selection['frames']:groups.setdefault((e['action'],e['direction']),{})[e['frame']]=e
for (action,direction),entries in groups.items():
 count,duration=specs[action]; cols=4; cell=280; rows=(count+cols-1)//cols
 contact=Image.new('RGB',(cols*cell,rows*(cell+32)),'#e7e4dc');draw=ImageDraw.Draw(contact)
 previews=[];sources=[]
 for number in range(1,count+1):
  ox=((number-1)%cols)*cell;oy=((number-1)//cols)*(cell+32)
  e=entries.get(number)
  if e:
   p=ROOT/e['source'] if e.get('inputIsFinalExport') else ROOT/f'candidate/{action}/{direction}/{number:02}.png'
   if not p.exists():continue
   rgba=Image.open(p).convert('RGBA')
   small=rgba.resize((cell,cell),Image.Resampling.LANCZOS);contact.paste(small,(ox,oy),small)
   sources.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':p.relative_to(ROOT).as_posix()+'.generation.json'})
   frame=Image.new('RGB',(512,550),'#e7e4dc');art=rgba.resize((512,512),Image.Resampling.LANCZOS);frame.paste(art,(0,0),art)
   ImageDraw.Draw(frame).text((12,519),f'{action}/{direction} {number:02}/{count} · {label}',font=font,fill='#25423d');previews.append(frame)
   text=f'{number:02} · {label}'
  else:text=f'{number:02} · 缺帧'
  draw.text((ox+12,oy+cell+3),text,font=font,fill='#25423d')
 out=ROOT/f'preview/{action}-{direction}-contact.png';contact.save(out)
 def record(p,op):
  Path(str(p)+'.generation.json').write_text(json.dumps({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'derivedFrom':sources,'operation':op,'dynamicAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
 record(out,'逐槽联系表；缺帧显示文字，不补造PNG；候选等比缩小用于审核')
 if len(previews)==count:
  for speed,mul in [('normal',1),('slow',4)]:
   out=ROOT/f'preview/{action}-{direction}-{speed}.png';previews[0].save(out,save_all=True,append_images=previews[1:],duration=duration*mul,loop=0,disposal=0,blend=0)
   record(out,{'type':'APNG动态预览','frameCount':count,'durationMs':duration*mul,'frameDurationsMs':[duration*mul]*count,'loopMs':duration*mul*count,'extraEndPauseMs':0,'rateMultiplier':1/mul,'alphaCompositeBackground':'#e7e4dc','artAltered':False})
print('Sequence previews refreshed; complete groups only; no automatic visual approval.')

