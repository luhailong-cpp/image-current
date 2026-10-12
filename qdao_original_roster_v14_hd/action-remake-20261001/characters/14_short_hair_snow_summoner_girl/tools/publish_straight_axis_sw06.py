"""Publish the reviewed SW06 AI yaw repair with immutable old text records."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from PIL import Image
from export_frame import run
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
key='run/SW/06';dst=R/(key+'.png');meta=Path(str(dst)+'.generation.json')
assert sha(dst)==read(R/'audit/straight-axis-baseline.json')['frames'][key+'.png']
stem='run-SW-06-straight-axis-v1';req=read(R/f'provenance/{stem}.request.json');receipt=read(R/f'provenance/{stem}.receipt.json')
host=Path(receipt['observedToolReturnedPath']);src=R/f'run/staging/{stem}.png';shutil.copy2(host,src)
im=Image.open(src);assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
refs=[{'path':p,'sha256':sha(Path(p)),'role':'edit target' if i==0 else ('primary approved style' if i==3 else 'adjacent Southwest boot-yaw reference')} for i,p in enumerate(req['submittedParameters']['referenced_image_paths'])]
gen={'file':src.relative_to(R).as_posix(),'sha256':sha(src),'generatedAt':datetime.fromtimestamp(host.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host file mtime; no tool timestamp','recordedAt':now(),'width':im.width,'height':im.height,'format':'PNG','mode':'RGBA','alphaExtrema':[0,255],'tool':'image_gen__imagegen','route':'builtin','configSnapshot':read(Path('D:/work/image/config/image-generation.json')),'submittedParameters':dict(req['submittedParameters'],model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具没有型号/质量选择器，返回未披露实际型号和质量。','evidence':{'toolReturnedPath':str(host),'receipt':f'provenance/{stem}.receipt.json','workspaceCopyShaMatchesSource':sha(src)==sha(host)},'request':f'provenance/{stem}.request.json','prompt':f'provenance/{stem}.request.json','references':refs,'review':{'status':'root_native_visually_selected'}}
save(Path(str(src)+'.generation.json'),gen)
old=read(meta);prior=R/f'provenance/straight-axis-prior-run-SW-06-{old["sha256"][:12]}.json';assert not prior.exists();save(prior,old)
history={f:read(R/f) for f in ['audit/contact-SW-review.json','audit/root-SW-preview-observations.json','audit/bamboo-root-acceptance.json','run/SW/grounding-review.json']}
save(R/'audit/straight-axis-prior-SW-records.json',history)
run(src,dst);m=read(meta)
m['registrationTransform']={'status':'applied','method':'direct_registered_canvas_redraw','globalScale':1.0,'inheritedCharacterScale':.8,'sourceRoot':[512,942],'targetRoot':[512,942],'outputSha256':sha(dst),'note':'AI edit of registered frame; only whole canvas downsample and edge RGB cleanup; no pose synthesis, extra scale or sole realignment.'}
m['straightAxisRepair']={'previousSha256':old['sha256'],'priorGenerationRecord':prior.relative_to(R).as_posix(),'observation':'Rear left support boot yaw corrected from nearly south/front to Southwest in line with the motion plane; knee and contact retained.','status':'static_selected_pending_sequence_review','reviewedAt':now()}
save(meta,m)
c=read(R/'audit/contact-SW-review.json')
for f in c['frames']:
    if f['file']==key+'.png':f['sha256']=sha(dst)
c['status']='static_pending_root_preview';c.pop('rootPreview',None)
c['straightAxisRepair']={'file':key+'.png','sha256':sha(dst),'observation':m['straightAxisRepair']['observation']}
save(R/'audit/contact-SW-review.json',c)
rv=read(R/'review.json');save(R/'provenance/straight-axis-prior-review-run-SW-06.json',rv[key]);rv[key]={'sha256':sha(dst),'visualStatus':'pending','reviewer':'root','reviewedAt':now(),'notes':'Local Southwest rear support shoe-yaw repair; pending sequence review.','clientValidated':False};save(R/'review.json',rv)
print('SW06 published and pending final browser review: '+sha(dst))
