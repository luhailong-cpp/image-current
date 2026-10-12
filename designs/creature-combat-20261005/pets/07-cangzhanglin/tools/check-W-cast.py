from pathlib import Path
from PIL import Image,ImageDraw
import json, hashlib, datetime
root=Path(__file__).resolve().parents[1]
frames=[]; hashes=[]; errors=[]
sheet=Image.new('RGB',(1280,1360),(226,232,225)); draw=ImageDraw.Draw(sheet)
notes=['注意目标，中性四蹄支撑','颈轻收，头与背保持W后视','头缓降、四肢微屈','头低蓄气，完整四足','修正版保持低头，仅角根微光','胸颈起升，小玉色灵光','修正版去除实体球，保留气雾','角周暖金光增强，后视/四足稳定','高聚气状态，金玉光不遮肢体','向左上释放，四足完整，局部鬃绢扬起','玉色气芒释放极点，原地四足支撑','气芒散退，头颈回收','少量光点，颈回收','四肢吸收回弹、微屈','单个余光，鬃绢回摆','中性附近恢复，两点微光']
for i in range(1,17):
 p=root/'runtime'/'cast'/'W'/f'{i:02}.png'; recp=root/'records'/'W-cast'/f'{i:02}.generation.json'
 if not p.exists() or not recp.exists():errors.append(f'missing {i}');continue
 im=Image.open(p); sha=hashlib.sha256(p.read_bytes()).hexdigest(); hashes.append(sha)
 rec=json.loads(recp.read_text(encoding='utf-8'))
 if im.size!=(1024,1024) or im.mode!='RGBA': errors.append(f'size or mode {i}')
 if rec['sha256']!=sha:errors.append(f'sha {i}')
 if im.getchannel('A').getextrema()!=(0,255):errors.append(f'alpha {i}')
 rec['visualReview']={'status':'reviewed','reviewer':'W-cast subagent','method':'actual per-image native outputs viewed; final contact sheet and browser normal/slow playback sampled','notes':notes[i-1],'clientIntegration':'not-tested'}
 rec['referencesDetails']=[]
 for ref,role in zip(rec['references'],rec['referenceRoles']):
  rp=Path(ref)
  rec['referencesDetails'].append({'path':ref,'role':role,'sha256':hashlib.sha256(rp.read_bytes()).hexdigest() if rp.exists() else None})
 recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 tile=Image.new('RGBA',(320,320),(226,232,225,255));tile.alpha_composite(im.resize((320,320),Image.Resampling.LANCZOS))
 x=((i-1)%4)*320;y=((i-1)//4)*340
 sheet.paste(tile.convert('RGB'),(x,y));draw.text((x+8,y+320),f'W CAST {i:02} / 45 ms',fill=(24,60,44))
 frames.append({'frame':i,'file':str(p.relative_to(root)).replace('\\','/'),'sha256':sha,'durationMs':45,'record':str(recp.relative_to(root)).replace('\\','/'),'event':'cast' if i==10 else None,'poseReview':notes[i-1]})
if len(set(hashes))!=16:errors.append('duplicate image hash')
for i,reason in [(5,'first candidate head raised too early and light too strong'),(7,'first candidate spell looked like decorated solid jade orb')]:
 p=root/'records'/'W-cast'/f'{i:02}.r1.generation.json'
 rec=json.loads(p.read_text(encoding='utf-8'))
 rec['status']='rejected';rec['rejectionReason']=reason;rec['supersededBy']=f'records/W-cast/{i:02}.generation.json';rec['previousFinalPath']=rec.pop('file');rec['file']=None;rec['retention']='Generated original exists only in host output cache outside assigned write scope; rejected runtime PNG was overwritten by independently generated revision. Text evidence retained.'
 p.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
preview=root/'preview';preview.mkdir(exist_ok=True)
sheet.save(preview/'W-cast-contact.png')
report={'group':'W-cast','frameCount':len(frames),'durationMs':45,'totalDurationMs':720,'independentAIGenerations':18,'networkFailureCount':1,'technicalStatus':'passed' if not errors else 'failed','errors':errors,'allHashesUnique':len(set(hashes))==16,'format':'1024x1024 RGBA PNG','transform':{'resize':[960,960],'offset':[32,6],'canvas':[1024,1024],'perFrameAlignment':False},'nativeOutputs':'1254x1254 RGBA','actualModel':None,'actualQuality':None,'modelEvidence':'tool does not expose selectors or actual model/quality; target snapshot retained per image','visualStatus':'all 16 native frame outputs visually inspected; 05 and 07 revised; true W view, four legs and one tail retained','dynamicStatus':'normal and quarter-speed browser playback sampled, cycles observed; full six-group parent review pending','limitations':['Some fine armor/cloth contours vary between independently generated frames; no mirroring, copying, translation or interpolation was used.','Released light on frames 10–11 is longer than prompt target; anatomy is not obscured.','Game client integration not tested.'],'preview':'preview/W-cast.html','contact':'preview/W-cast-contact.png','frames':frames}
(root/'records'/'W-cast'/'group-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frameCount':len(frames),'errors':errors,'uniqueHashes':len(set(hashes)),'report':str(root/'records'/'W-cast'/'group-report.json')},ensure_ascii=False))

