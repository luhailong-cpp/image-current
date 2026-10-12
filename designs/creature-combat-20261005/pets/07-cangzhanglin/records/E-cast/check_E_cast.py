from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
base=Path(r'D:/work/image/designs/creature-combat-20261005/pets/07-cangzhanglin')
records=base/'records'/'E-cast'
hashes=[];frames=[];errors=[]
notes={6:'修正版：仍在低位，从05开始小幅起颈，四足原地支撑；未直接恢复中性。',7:'头胸起升聚气，四蹄、双组角、单云尾完整。',8:'胸颈进一步上抬，角间玉气增强，保持E斜前朝右下。',9:'高位聚气，玉金灵光增强；四足/角/尾无新增或减少。',10:'修正版：缩小原先触边的大气浪，完整小型玉色气芒向右下开始释放，保留原地姿态。',11:'释放极点，头颈向右下伸出；四蹄支撑，无位移循环。',12:'灵气减弱、头颈回收，面胸与玉甲身份一致。',13:'回收至近中性，绢带随局部运动，四足完整。',14:'轻屈四肢吸收回弹，头略低，微弱余气。',15:'恢复近中性，鬃绢趋于平稳、灵气已散。',16:'中性附近收势，方向/形象/四足与首帧相接。'}
sheet=Image.new('RGB',(1280,1360),(226,232,225));draw=ImageDraw.Draw(sheet)
for n in range(1,17):
 path=base/'runtime'/'cast'/'E'/f'{n:02}.png'; recpath=records/f'{n:02}.generation.json'
 if not path.exists() or not recpath.exists(): errors.append(f'missing {n}');continue
 im=Image.open(path);sha=hashlib.sha256(path.read_bytes()).hexdigest();hashes.append(sha)
 rec=json.loads(recpath.read_text(encoding='utf-8'))
 if im.size!=(1024,1024) or im.mode!='RGBA':errors.append(f'size/mode {n}')
 if im.getchannel('A').getextrema()!=(0,255):errors.append(f'alpha {n}')
 if sha!=rec['sha256']:errors.append(f'sha {n}')
 if not (base/rec['prompt']).is_file():errors.append(f'prompt {n}')
 if not (base/rec['evidence']['receipt']).is_file():errors.append(f'receipt {n}')
 if rec['actualModel'] is not None or rec['actualQuality'] is not None:errors.append(f'unverified actual values {n}')
 if n in notes:
  rec['visualReview']=notes[n]+' 已实际查看该帧原生工具输出及组总览；六组连播由主代理统一复核，客户端未验证。'
  rec['referencesSha256']=[{'path':r['path'],'role':r['role'],'sha256':hashlib.sha256(Path(r['path']).read_bytes()).hexdigest() if Path(r['path']).is_file() else None} for r in rec['references']]
  recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 tile=Image.new('RGBA',(320,320),(226,232,225,255));tile.alpha_composite(im.resize((320,320),Image.Resampling.LANCZOS));x=((n-1)%4)*320;y=((n-1)//4)*340;sheet.paste(tile.convert('RGB'),(x,y));draw.text((x+8,y+320),f'E CAST {n:02} / 45 ms',fill=(24,60,44))
 frames.append({'frame':n,'file':f'runtime/cast/E/{n:02}.png','sha256':sha,'record':f'records/E-cast/{n:02}.generation.json','durationMs':45,'event':'cast' if n==10 else None})
if len(set(hashes))!=16:errors.append('duplicate SHA')
for n,reason in [(6,'head rose too close to neutral in first draft; revised to initial rise from low preparation'),(10,'jade light wave too large and touching native right edge; replaced by compact contained wisp')]:
 p=records/f'{n:02}-attempt01-rejected.generation.json';r=json.loads(p.read_text(encoding='utf-8'))
 r['status']='rejected';r['rejectionReason']=reason;r['previousFinalPath']=r.get('file');r['file']=None
 r['supersededBy']=f'records/E-cast/{n:02}.generation.json';r['prompt']=f'prompts/cast-E-{n:02}-attempt01-rejected.txt'
 r['evidence']['receipt']=f'records/E-cast/{n:02}-attempt01-rejected.receipt.json'
 r['derivedFrom']['supersededStagePath']=r['derivedFrom']['path'];r['derivedFrom']['path']=None;r['derivedFrom']['retention']='Rejected staged and runtime pixels overwritten by independent accepted revision; original host cache path and SHA retained as historical evidence.'
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
sheet.save(records/'E-cast-contact.png')
report={'group':'E-cast','status':'technical-check-passed' if not errors else 'failed','frameCount':len(frames),'uniqueSha256':len(set(hashes)),'dimensions':'1024x1024','mode':'RGBA','durationMs':45,'totalMs':720,'eventFrame':10,'errors':errors,'newFramesThisResume':list(range(6,17)),'newIndependentAIGenerationsThisResume':13,'targetModel':'gpt-image-2.5-sunburst','targetQuality':'max','actualModel':None,'actualQuality':None,'singleFrameVisualReview':'All 16 inspected; prior 01-05 kept. Frame06 and10 revised with original rejected evidence retained. Four natural quadruped limbs, two branched antler groups and single cloud tail retained, E front-three-quarter facing down-right.','dynamicReview':'Pending parent consolidated six-group playback verification.','clientIntegration':'not-tested','transform':{'wholeCanvasResize':[960,960],'pasteOffset':[32,6],'targetCanvas':[1024,1024],'perFrameAlignment':False},'retention':'Current staging/cast/E originals remain for parent final verified cleanup; no image backups were created.','frames':frames}
(records/'group-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'group':'E-cast','count':len(frames),'uniqueHashes':len(set(hashes)),'errors':errors},ensure_ascii=False))

