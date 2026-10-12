from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,sys,os
from datetime import datetime,timezone
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
ROOT=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
vs=read(ROOT/'r08_c12_selection.json')['patchVersions']
pairs=[]
for r in range(1,5):
 for c in range(1,5):
  a=f'{r}{c}'
  for b,d in [(f'{r}{c+1}','horizontal')] if c<4 else []:
   pairs.append((a,b,d))
  if r<4:pairs.append((a,f'{r+1}{c}','vertical'))
for a,b,d in pairs:
 ident=f'r08_c12-p{a}{vs[a]}-p{b}{vs[b]}'
 subprocess.run([sys.executable,str(ROOT/'qa'/'check_pair.py'),f'r08_c12_p{a}_{vs[a]}.png',f'r08_c12_p{b}_{vs[b]}.png',d,ident],check=True,capture_output=True)
external=[]
for c,v in [(1,'v01'),(2,'v06'),(3,'v02'),(4,'v01')]:
 a=f'4{c}';ident=f'r08_c12-p{a}{vs[a]}-r09_c12-p1{c}{v}'
 subprocess.run([sys.executable,str(ROOT/'qa'/'check_pair.py'),f'r08_c12_p{a}_{vs[a]}.png',f'r09_c12_p1{c}_{v}.png','vertical',ident],check=True,capture_output=True);external.append(ident)
records=[]
for p in sorted((ROOT/'native').glob('r08_c12*.generation.json')):
 x=read(p);f=Path(x['file']);errs=[]
 if sha(f)!=x['sha256']:errs.append('PNG sha mismatch')
 if Image.open(f).size!=(1254,1254):errs.append('native dimensions not1254')
 if not Path(x['prompt']).exists() or sha(x['prompt'])!=x['promptSha256']:errs.append('prompt missing or sha mismatch')
 for ref in x['references']:
  if not Path(ref['file']).exists() or sha(ref['file'])!=ref['sha256']:errs.append('reference missing or sha mismatch '+ref['file'])
 receipt=ROOT/x['evidence']['toolReceipt']
 if not receipt.exists():errs.append('receipt missing')
 if not Path(x['sourceOutputPath']).exists() or sha(x['sourceOutputPath'])!=x['sha256']:errs.append('host source missing or unequal')
 if x['actualModel'] is not None or x['actualQuality'] is not None or x['submittedParameters']!={'model':None,'quality':None}:errs.append('model evidence conflation')
 if x['resizedAfterGeneration'] is not False:errs.append('resize flag')
 records.append({'record':str(p),'file':str(f),'sha256':sha(f),'promptSha256':x['promptSha256'],'referenceCount':len(x['references']),'receipt':str(receipt),'errors':errs,'pass':not errs})
write(ROOT/'qa'/'r08_c12.source-audit.json',{'auditedAt':datetime.now(timezone.utc).isoformat(),'scope':'snapshot all22r08 generation records','records':records,'allPass':all(r['pass'] for r in records),'actualModel':None,'actualQuality':None})
write(ROOT/'qa'/'r08_c12.qa-index.json',{'internal':[f'r08_c12-p{a}{vs[a]}-p{b}{vs[b]}' for a,b,d in pairs],'external':external})
p=read(ROOT/'progress-r08_c12.json');p.update(status='candidate_visual_review',selectedCandidateNativeCount=16,candidate4kCount=1,complete4kCount=0,formalAcceptedCount=0,nextStep='24 internal seams and9junctions native visual review; external not accepted');write(ROOT/'progress-r08_c12.json',p)
print(json.dumps({'internalPairs':len(pairs),'externalPairs':len(external),'auditRecords':len(records),'auditPass':all(r['pass'] for r in records)}))

