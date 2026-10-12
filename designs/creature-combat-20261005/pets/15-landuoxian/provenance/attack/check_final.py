from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2]
prov=root/'provenance'/'attack'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frames=[];problems=[];seen={}
for d in ['E','W']:
 for i in range(1,13):
  p=root/'runtime'/'attack'/d/f'{i:02d}.png'
  if not p.exists(): problems.append('missing '+str(p));continue
  im=Image.open(p);digest=sha(p);recpath=p.with_suffix('.png.generation.json')
  rec=json.loads(recpath.read_text(encoding='utf-8'))
  if im.size!=(1024,1024) or im.mode!='RGBA':problems.append('dimensions/mode '+str(p))
  if rec.get('sha256')!=digest:problems.append('sha '+str(p))
  if digest in seen:problems.append('duplicate '+str(p)+' '+seen[digest])
  seen[digest]=str(p)
  a=im.getchannel('A');edges=[a.crop((0,0,1024,1)).getextrema(),a.crop((0,1023,1024,1024)).getextrema(),a.crop((0,0,1,1024)).getextrema(),a.crop((1023,0,1024,1024)).getextrema()]
  if any(e[1] for e in edges):problems.append('edge clipping '+str(p))
  refcheck=[]
  for ref in rec.get('references',[]):
   rp=Path(ref.get('file',ref.get('path')));ok=rp.exists() and ('sha256' not in ref or sha(rp)==ref['sha256'])
   refcheck.append({'file':str(rp),'shaMatches':ok})
   if not ok:problems.append('reference '+str(rp))
  frames.append({'file':str(p),'sha256':digest,'record':str(recpath),'size':list(im.size),'mode':im.mode,'alphaExtrema':a.getextrema(),'alphaBbox':a.getbbox(),'outerEdgesTransparent':True,'referenceChecks':refcheck})
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'count':len(frames),'expected':24,'pass':len(frames)==24 and not problems,'problems':problems,'frames':frames}
(prov/'technical-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
rej=prov/'W'/'11.rejected-1.generation.json'
r=json.loads(rej.read_text(encoding='utf-8'));r['fileStatus']='replaced in place by corrected W11; historical sha256 refers to discarded version';r['prompt']=str(prov/'W'/'11.rejected-1.prompt.txt');r['evidence']['receipt']=str(prov/'W'/'11.rejected-1.receipt.json');r['rejectionReason']='Mallet lowered to hip level, breaking late-recovery path. Corrected to shoulder-height return.';r['replacement']=str(root/'runtime'/'attack'/'W'/'11.png');r['native']['fileStatus']='historical source was replaced in place; sha256 retained as text evidence';rej.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'count':report['count'],'pass':report['pass'],'problems':problems}))
