from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
import local_repairs
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=B/'r12_c06/repairs-resume-20261012/V2-roof-rim-v01/integrated/assembly.json';a=read(ap)
for step in a['localNativeRepairs']:
 g=read(step['generationRecord']);assert sha(step['generationRecord'])==step['generationRecordSha256']
 assert sha(g['file'])==g['sha256']==sha(g['sourceOutputPath'])
 assert sha(g['evidence']['toolReceipt'])==g['evidence']['toolReceiptSha256'] and sha(g['inputContext'])==g['inputContextSha256']
 prev=np.array(Image.open(g['inputContext']).convert('RGB'));native=np.array(Image.open(g['file']).convert('RGB'));l,t,r,b=g['contextBox']
 mixed,d=local_repairs.quilt(prev[t:b,l:r],native,2);prev[t:b,l:r]=mixed
 sa=read(Path(step['generationRecord']).parent/'integrated/assembly.json');ctx=sa['contextOutput'];core=sa['output'];assert sha(ctx['file'])==ctx['sha256'] and sha(core['file'])==core['sha256']
 actual=np.array(Image.open(ctx['file']).convert('RGB'));assert np.array_equal(prev,actual) and np.array_equal(actual[115:4211,115:4211],np.array(Image.open(core['file']).convert('RGB')))
 assert d['alphaSha256Uint8RowMajor']==step['quilting']['alphaSha256Uint8RowMajor']
rp=ap.parent/'root-review.json';assert not rp.exists()
atomic_json(rp,{'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','assembly':str(ap),'allThreeNativeRepairCompositionsReproduced':True,'originalFullReview':str(B/'r12_c06/repairs-resume-20261012/V3-roof-rim-v01/integrated/root-full-review.json'),'rootViewed':['V1 integrated1254 repair crop','V2 integrated1254 repair crop'],'resolved':['All three main central roof rim steps removed in native local repairs.'],'openFindings':['V1 repair left edge leaves gold shading/slight edge notch.','V2 repair lower halo has visible repeated roof phase/color offsets; central rim improved but roof seam QA remains failed.','All previous quiet stone, paving line, H3 roof tone, and external boundary issues remain pending.'],'sourceResampling':False,'maximumFeatherRadiusPixels':2,'internalPassed':False,'formalAccepted':False})
cat=read(B/'current-candidates.json');cat['tiles']['r12_c06']={'tile':'r12_c06','source':'current-native-provisional-with-open-QA','assembly':str(ap),'candidate':a['output'],'context':a['contextOutput'],'review':str(rp),'internalPassed':False,'formalAccepted':False};cat.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),complete4kCandidateCount=len(cat['tiles']),formalAcceptedCount=0);atomic_json(B/'current-candidates.json',cat)
D=B/'r13_c06/pipeline/anchors';D.mkdir(parents=True,exist_ok=True)
for name,e,box in [('top-r12c06-rims-v03',cat['tiles']['r12_c06']['context'],[0,4096,4326,4326]),('left-r13c05-native-v01',cat['tiles']['r13_c05']['context'],[4096,0,4326,4326])]:
 p=D/(name+'.png');assert not p.exists();assert sha(e['file'])==e['sha256'];Image.open(e['file']).crop(box).save(p)
 atomic_json(p.with_suffix('.derivation.json'),{'source':e,'sourceCrop':box,'file':str(p),'sha256':sha(p),'sourceResampling':False,'nativePixelsPreserved':True,'status':'provisional_neighbor_anchor_not_formally_accepted','formalAccepted':False})
print(json.dumps({'catalogCount':len(cat['tiles']),'rootTile':'r13_c06','anchors':str(D),'formalAccepted':False}))
