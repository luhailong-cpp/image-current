from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageSequence
import json
b=Path(__file__).resolve().parents[1]
p=b/'audit/run-E-grounding-review.json';data=json.loads(p.read_text(encoding='utf-8'))
presets=[('legacy480',[30]*16),('trial640',[40]*16),('trial720',[45]*16),('trial800',[50]*16),('weighted720',data['customDurationsMs'])]
outs=[]
for size in [240,384]:
 thumbs=[];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',13 if size==240 else 17)
 for r in data['frames']:
  im=Image.open(b/r['source']).convert('RGBA');can=Image.new('RGBA',(1024,1024));can.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49));sm=can.resize((size,size),Image.Resampling.LANCZOS)
  tile=Image.new('RGB',(size,size+36),(221,229,236));d=ImageDraw.Draw(tile);tile.paste(sm,(0,32),sm);d.text((7,7),f'E{r["frame"]:02d} · {r["phaseObserved"]}',font=font,fill=(22,49,65));d.line((0,32+942*size/1024,size,32+942*size/1024),fill=(190,82,68));thumbs.append(tile)
 for key,durs in presets:
  ends=[];total=0
  for v in durs:total+=v;ends.append(round(total/10)*10)
  actual=[v-(ends[i-1]if i else 0)for i,v in enumerate(ends)]
  dst=b/'audit'/f'run-E-grounding-{key}-{size}.gif'
  thumbs[0].save(dst,save_all=True,append_images=thumbs[1:],duration=actual,loop=0,disposal=2,optimize=False)
  chk=Image.open(dst);realdurs=[f.info['duration']for f in ImageSequence.Iterator(chk)]
  assert len(realdurs)==16 and sum(realdurs)==sum(durs)
  outs.append({'file':dst.relative_to(b).as_posix(),'frameCount':16,'spriteCanvasSize':size,'requestedMs':durs,'actualGifMs':realdurs,'cycleMs':sum(realdurs)})
data['previewDerivatives']={'outputs':outs,'operation':'整画布固定缩放和诊断线/标签绘制，仅预览；无姿态合成','derivedFrom':[{'file':r['source'],'sha256':r['sha256'],'generationRecord':r['generationRecord']}for r in data['frames']]}
data['browser']={'status':'pending_updated_snapshot_review','html':'audit/run-E-grounding.html','notClaimed':'未接入客户端，更新后的整组仍待主审'}
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'previews':len(outs),'validated':[{'file':r['file'],'cycle':r['cycleMs']}for r in outs]},ensure_ascii=False))

