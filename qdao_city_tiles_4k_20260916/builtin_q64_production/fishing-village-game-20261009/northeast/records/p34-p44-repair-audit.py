from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rp=B/'qa/p34-p44-repair-visual-review.json';v=read(rp)
v['independentVisualReview']={'reviewer':'/root/middle_column','method':'read-only view_image of actual host output and exact side-by-side reference; no files modified by independent reviewer','layoutResult':'fail','detail':'The exact-guide front rim protrudes around x360–420,y330–400 and support extends to y1000. The new capped corner lies around x670–800,y240–390 and support ends near y670. The footprint is too far right and too shallow, far beyond low-resolution uncertainty.','fishResult':'improved but complete proportion not certified','fishDetail':'Blue back, silver-white belly, round eye, organized overlapping scales and soft volume closely resemble p13 sample. Visible fish are slightly shorter/thicker and tails mostly obscured, so full-fish proportions cannot be certified.'}
write(rp,v)
cp=B/'qa/p34-p44-repair-check.json';c=read(cp);c['visualReview']['sha256']=sha(rp);write(cp,c)
files=[]
for folder in ['records','native','guides','qa']:files.extend((B/folder).glob('p34-p44-repair*.json'))
checked=[];errors=[]
def walk(x,owner,at=''):
 if isinstance(x,dict):
  p=x.get('path') or x.get('file')
  if p and 'sha256' in x:
   path=Path(p)
   if not path.exists():errors.append({'owner':str(owner),'at':at,'missing':p})
   else:
    actual=sha(path);checked.append({'owner':str(owner),'path':p,'matches':actual==x['sha256']})
    if actual!=x['sha256']:errors.append({'owner':str(owner),'at':at,'path':p,'expected':x['sha256'],'actual':actual})
  for k,v in x.items():walk(v,owner,at+'/'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):walk(v,owner,at+'/'+str(i))
for p in files:walk(read(p),p)
s=read(B/'records/p34-p44-repair-v1.submission.json');r=read(B/'records/p34-p44-repair-v1.receipt.json')
assert r['submittedArguments']['prompt']==Path(s['promptFile']).read_text(encoding='utf-8-sig')
assert r['submittedArguments']['referenced_image_paths']==[v['path'] for v in s['references']]
assert r['actualModel'] is None and r['actualQuality'] is None
assert len(s['references'])==5
assert not errors,errors
out={'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'only new p34-p44-repair records and direct file/hash links; no modification of shared records','jsonFilesChecked':len(files),'hashLinksChecked':len(checked),'errors':errors,'submittedPromptExactlyMatchesFile':True,'fiveActualReferencesMatchSubmission':True,'actualModel':None,'actualQuality':None,'actualAiCallsThisRepair':1,'nativeDimensions':[1254,1254],'candidateDimensions':{p:list(Image.open(B/('native/p34-p44-repair-'+p+'-candidate-v1.png')).size) for p in ['p34','p44']},'formalAccepted':False,'visualResult':'failed_validation_candidate_only','visualReview':{'path':str(rp),'sha256':sha(rp)},'mechanicalCheck':{'path':str(cp),'sha256':sha(cp)}}
p=B/'records/p34-p44-repair-provenance-check.json';write(p,out)
print(json.dumps(out))

