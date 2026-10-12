from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,numpy as np,os,time
from PIL import Image
B=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,d):
 p=Path(p);tmp=p.with_name(p.name+'.inventory-tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for attempt in range(5):
  try:os.replace(tmp,p);return
  except OSError:
   if attempt==4:raise
   time.sleep(.5)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):p=Path(p);return p if p.is_absolute() else B/p
idx=rd(B/'current-artifacts.json');progress=rd(B/'progress.json')
target={f'r{r:02d}_c{c:02d}' for r in range(1,8) for c in range(1,8)}
covered={};extras={};skips=[]
for t,e in idx.items():
 if t in target:covered[t]={'candidate':e['candidate'],'assembly':e['assembly'],'adopted':True,'internalAccepted':progress.get('currentCandidates',{}).get(t,{}).get('internalAccepted',False)}
assemblies=set(B.rglob('*.assembly.json'))|set(B.rglob('assembly.json'))
for ap in assemblies:
 try:
  a=rd(ap);box=a.get('globalCoreBox');cand=a.get('candidate');mp=a.get('sourceIdMap')
  if not isinstance(box,list) or len(box)!=4 or box[2]-box[0]!=4096 or box[3]-box[1]!=4096 or box[0]%4096 or box[1]%4096:continue
  t=f'r{box[1]//4096+1:02d}_c{box[0]//4096+1:02d}'
  if t not in target or t in covered or not isinstance(cand,dict) or not isinstance(mp,dict):continue
  cp=path(cand['file']);ip=path(mp['file'])
  if not cp.is_file() or not ip.is_file() or Image.open(cp).size!=(4096,4096):continue
  if cand.get('sha256')!=sha(cp) or mp.get('sha256')!=sha(ip):continue
  if t not in extras or ap.stat().st_mtime>extras[t][0]:extras[t]=(ap.stat().st_mtime,ap,a)
 except (OSError,ValueError,KeyError,TypeError):continue
for t,(_,ap,a) in extras.items():
 try:
  cp=path(a['candidate']['file']);ip=path(a['sourceIdMap']['file']);arr=np.asarray(Image.open(cp).convert('RGB'));ids=np.asarray(Image.open(ip));assert ids.shape==(4096,4096)
  sources=a['sources'];sources=list(sources.values()) if isinstance(sources,dict) else sources
  valid=np.zeros(ids.shape,bool);mismatches=0;box=a['globalCoreBox']
  for s in sources:
   sid=s.get('sourceId',s.get('jointSourceId'));y,x=np.where(ids==sid)
   if not len(x):continue
   p=path(s['file']);assert sha(p)==s['sha256'];g=s['globalNativeBox'];src=np.asarray(Image.open(p).convert('RGB'));sx=x+box[0]-g[0];sy=y+box[1]-g[1];assert min(sx.min(),sy.min())>=0 and sx.max()<src.shape[1] and sy.max()<src.shape[0]
   mismatches+=int(np.any(arr[y,x]!=src[sy,sx],axis=1).sum());valid[y,x]=True
  assert mismatches==0 and valid.all()
  covered[t]={'candidate':str(cp.relative_to(B)).replace('\\','/'),'candidateSha256':sha(cp),'assembly':str(ap.relative_to(B)).replace('\\','/'),'adopted':False,'internalAccepted':False,'nativeReplay':{'pixels':16777216,'mismatches':0,'uncovered':0}}
 except (OSError,ValueError,KeyError,TypeError,AssertionError) as e:skips.append({'tile':t,'assembly':str(ap),'reason':str(e)})
internal={t for t,d in covered.items() if d['internalAccepted']}
pending=sorted(set(covered)-internal);missing=sorted(target-set(covered));now=datetime.now(timezone.utc).isoformat()
out={'zone':'northwest','updatedAtUtc':now,'counting':'Unique assigned coordinates. Fully covered includes native-source-verified candidates pending repair/QA; missing outer neighbor art is separate.','targetCoordinateCount':len(target),'fullyCoveredCandidateCount':len(covered),'internallyPassedCandidateCount':len(internal),'missingNativeWholeCoordinateCount':len(missing),'fullyCoveredPendingRepairOrQaCount':len(pending),'formalAcceptedCount':0,'fullyCoveredCoordinates':sorted(covered),'internallyPassedCoordinates':sorted(internal),'fullyCoveredPendingRepairOrQaCoordinates':pending,'missingNativeWholeCoordinates':missing,'candidates':covered,'skippedUnverifiedExtraAssemblies':skips}
wr(B/'coordinate-inventory-current.json',out)
progress.update(updatedAt=now,fullyCovered4kCount=len(covered),completeCandidateCoordinatesOnDisk=len(covered),internalPassed4kCount=len(internal),missingFullyCovered4kCount=len(missing),fullyCoveredPendingRepairOrQaCount=len(pending),coordinateInventory='coordinate-inventory-current.json',nextStep='Complete active coordinates, repair and review covered candidates, then advance to next missing coordinate; exterior joins separate.')
wr(B/'progress.json',progress)
resume=rd(B/'production-resume-20261012.json');resume.update(updatedAtUtc=now,complete4kCandidatesOnDisk=len(covered),internallyPassed4kCandidates=len(internal),missingNativeWholeCoordinates=len(missing),fullyCoveredPendingRepairOrQaCount=len(pending),coordinateInventory='coordinate-inventory-current.json')
wr(B/'production-resume-20261012.json',resume)
print(json.dumps({k:out[k] for k in ['targetCoordinateCount','fullyCoveredCandidateCount','internallyPassedCandidateCount','missingNativeWholeCoordinateCount','fullyCoveredPendingRepairOrQaCount']}))
