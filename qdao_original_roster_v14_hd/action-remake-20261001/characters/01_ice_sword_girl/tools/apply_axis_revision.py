"""Promote the eight independently reviewed local leg edits, preserving all other final images."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selected={'E':{7:'07-v1',8:'08-v2',15:'15-v1',16:'16-v1'},'W':{13:'13-v2',14:'14-v1',15:'15-v4',16:'16-v4'}}
changes=[]
for direction,frames in selected.items():
 for i,name in frames.items():
  src=R/f'drafts/axis-20261004/run/{direction}/{name}.png';g=read(src.with_name(src.name+'.generation.json'))
  assert sha(src)==g['sha256'] and Image.open(src).size==(1254,1254)
for direction,frames in selected.items():
 path=R/f'review/run-{direction}-selection.json';s=read(path)
 for i,name in frames.items():
  src=R/f'drafts/axis-20261004/run/{direction}/{name}.png';gp=src.with_name(src.name+'.generation.json');g=read(gp)
  dst=R/f'candidate/run/{direction}/{i:02}.png';dgp=dst.with_name(dst.name+'.generation.json');oldsha=sha(dst)
  oldrecord=R/f'sources/reference-history/{oldsha}.generation.json'
  if not oldrecord.exists():oldrecord.write_bytes(dgp.read_bytes())
  assert read(oldrecord)['sha256']==oldsha
  im=Image.open(src);assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
  im.resize((1024,1024),Image.Resampling.LANCZOS).save(dst)
  rec={'file':dst.relative_to(R).as_posix(),'sha256':sha(dst),'width':1024,'height':1024,'mode':'RGBA','nativeFrameSize':list(im.size),'derivedFrom':{'file':src.relative_to(R).as_posix(),'sha256':g['sha256'],'generationRecord':gp.relative_to(R).as_posix(),'generationRecordSha256':sha(gp)},'operation':{'type':'whole_canvas_LANCZOS_downsample','inputSize':list(im.size),'outputSize':[1024,1024],'translation':[0,0],'crop':None,'alphaFootAlignment':False,'bboxNormalization':False,'mirrored':False,'poseInterpolation':False},'actualModel':None,'actualQuality':None,'supersedesExport':{'sha256':oldsha,'generationRecord':oldrecord.relative_to(R).as_posix()},'status':'axis_revision_selected','clientRuntimeVerified':False}
  write(dgp,rec)
  f=s['frames'][i-1];assert f['frame']==i
  f.update(path=src.relative_to(R).as_posix(),sourcePath=src.relative_to(R).as_posix(),sha256=g['sha256'],generationRecord=gp.relative_to(R).as_posix(),nativeSize=list(im.size),candidatePath=dst.relative_to(R).as_posix(),candidateSha256=sha(dst),candidateGenerationRecord=dgp.relative_to(R).as_posix(),notes='视频对照后局部修订：前摆小腿自然屈膝，减少过长前踢和持续翘尖，鞋长轴保持侧向运动平面；原支撑脚和位置保持。',staticInspected=True)
  changes.append({'action':'run','direction':direction,'frame':i,'file':dst.relative_to(R).as_posix(),'source':src.relative_to(R).as_posix(),'oldSha256':oldsha,'sha256':sha(dst),'nativeSha256':g['sha256']})
 s.update(artStatus='axis_video_revision_reviewed',offlineArtworkReviewComplete=True,axisRevision='review/axis-revision-selection-20261004.json',remainingRequiredImageRepairs=[])
 write(path,s)
 cell=256;sheet=Image.new('RGB',(4*cell,4*(cell+24)),'#c6d4d9');draw=ImageDraw.Draw(sheet)
 for j in range(16):
  frame=Image.open(R/f'candidate/run/{direction}/{j+1:02}.png').resize((cell,cell),Image.Resampling.LANCZOS);x=j%4*cell;y=j//4*(cell+24)
  sheet.paste(frame,(x,y+24),frame);draw.text((x+4,y+4),f'{direction}{j+1:02} 75ms',fill='black')
 sheet.save(R/f'preview/run-{direction}-selected-256.png')
write(R/'review/axis-revision-selection-20261004.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'changes':changes,'unchangedFrameCount':188,'timingUnchanged':'run16x75ms=1200ms','clientRuntimeVerified':False})
print(json.dumps({'changedFrames':len(changes),'unchangedFrames':188}))
