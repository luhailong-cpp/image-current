"""Reassign a unique already-generated native pose to its anatomically correct slot."""
import argparse,json,hashlib,copy
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('action');p.add_argument('direction');p.add_argument('frame',type=int);p.add_argument('reason');a=p.parse_args()
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
src=ROOT/'work'/f'{a.stem}.png';sr=src.with_name(src.name+'.generation.json');record=json.loads(sr.read_text(encoding='utf-8-sig'))
for path in (ROOT/'runtime').rglob('*.png.generation.json'):
 r=json.loads(path.read_text(encoding='utf-8-sig'))
 if any(x.get('sha256')==sha(src) for x in r.get('derivedFrom',[])):raise ValueError('Native already assigned; remove old export first, never duplicate a pose.')
out=ROOT/'runtime'/a.action/a.direction/f'{a.frame:02d}.png';out.parent.mkdir(parents=True,exist_ok=True)
if out.exists():
 old=out.with_name(out.name+'.generation.json');r=json.loads(old.read_text(encoding='utf-8-sig'));r['replacementReason']=a.reason
 (ROOT/'records'/f'{a.action}_{a.direction}_{a.frame:02d}_reassigned_previous_{r["sha256"][:12]}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.open(src);im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
r={'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','derivedFrom':[{'file':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'generationRecord':sr.relative_to(ROOT).as_posix()}],'native':record['native'],'operation':'Full canvas uniform Lanczos downsample to 1024; no cropping, mirroring, warping or per-frame bbox alignment','actualModel':None,'actualQuality':None,'unverifiedReason':record['unverifiedReason'],'visualReview':a.reason,'anchor':{'type':'provisional fixed virtual ground/root','x':512,'y':942,'normalizedUnityPivot':[0.5,0.08],'verified':False},'generatedAt':record['generatedAt'],'poseReassignment':{'originalPromptPreserved':True,'reason':a.reason}}
out.with_name(out.name+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
record['exported']=True;record['exportPath']=out.relative_to(ROOT).as_posix();record['poseReassignment']=r['poseReassignment'];sr.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'out':str(out),'source':str(src)},ensure_ascii=False))
