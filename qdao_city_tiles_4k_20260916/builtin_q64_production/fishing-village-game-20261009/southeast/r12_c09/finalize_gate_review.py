import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
checks=[]
for path in sorted((ROOT/'layout-only').glob('*-native-conditioned.png.derivation.json')):
 d=read(path);base=d['baseInput'];im=Image.open(base['path']).convert('RGB');ok=sha(base['path'])==base['sha256'];sources=[]
 for s in d['nativeSources']:
  source=Image.open(s['source']).convert('RGB')
  c=s['sourceCrop'];at=s['pasteAt'];im.paste(source.crop(tuple(c)),tuple(at))
  prov=s.get('sourceProvenance');pk=(sha(prov['path'])==prov['sha256']) if prov else None
  sources.append({'source':s['source'],'sourceShaMatches':sha(s['source'])==s['sha256'],'sourceProvenanceShaMatches':pk,'unscaledCopy':(c[2]-c[0],c[3]-c[1])==tuple(s['pastedDimensions'])})
 actual=Image.open(d['file']).convert('RGB')
 checks.append({'patch':d['patch'],'baseShaMatches':ok,'sources':sources,'conditionShaMatches':sha(d['file'])==d['sha256'],'conditionPixelReplayExact':bool(np.array_equal(np.array(im),np.array(actual)))})
all_native=[]
for gp in sorted((ROOT/'native').glob('*.png.generation.json')):
 d=read(gp);p=Path(d['file'])
 all_native.append({'file':str(p),'shaMatches':sha(p)==d['sha256'],'dimensions':list(Image.open(p).size),'actualModelQualityNull':d['actualModel'] is None and d['actualQuality'] is None,'submittedModelQualityNull':d['submittedParameters']['model'] is None and d['submittedParameters']['quality'] is None,'promptRequestReceiptPresent':Path(d['prompt']).exists() and Path(d['evidence']['request']).exists() and Path(d['evidence']['receipt']).exists(),'configSnapshotPresent':bool(d['configSnapshot'])})
review={'tile':'r12_c09','createdAt':datetime.now(timezone.utc).isoformat(),'status':'partial_QA_under_capacity_gate','internalReady':False,'formalAccepted':False,'reviewedNativeInternalSeams':17,'reviewedNativeCrosses':6,'reviewedNorthExternalStrips':4,'visualFindings':[{'scope':'17 available internal seams + 6 intersections','finding':'No conspicuous large contour break seen in fence rails, stone wall edges, shrub silhouettes, rock shapes or dock corner at current hard cuts. This is partial geometry QA only.'},{'scope':'p13-p14 and p14-p24 paving','finding':'p14 fine surface pattern is more regular and grid-like than adjacent p13. Small color/texture step remains; record for later approved finishing, do not report final acceptance.'},{'scope':'r11_c09 bottom to r12_c09 top, four native strips','finding':'Major paving lines appear connected in preliminary read-only visual inspection. North c4 has visible texture/tone change; no modifications made to either tile.'},{'scope':'p23-v1 versus p23-v2','finding':'Rejected v1 invented water where layout is retaining stone. Selected v2 removes invented water. Small terminal fence support is a material/structure interpretation to review alongside layout before final acceptance.'}],'pending':['p41-p44 not generated','Full24seams/9crosses not yet available','No bounded colorpass or other finishing during gate','Independent p13-p14 geometry review requested but not yet done','All external boundary acceptance remains pending','Shared mail reference and config sources absent at last ingest; root must resolve asset-location policy before generation resumes'],'conditionReplay':checks,'nativeRecordAudit':all_native,'deletionsPerformed':False,'newArtworkRequestsAfterGate':0}
save(ROOT/'qa/capacity-gate-partial-review.json',review)
cp=read(ROOT/'capacity-gate-checkpoint.json');cp['qaReview']=str(ROOT/'qa/capacity-gate-partial-review.json');cp['qaReviewSha256']=sha(ROOT/'qa/capacity-gate-partial-review.json');cp['conditionReplayAllExact']=all(x['conditionPixelReplayExact'] for x in checks);cp['all13NativeRecordsPresent']=len(all_native)==13;save(ROOT/'capacity-gate-checkpoint.json',cp)
p=read(ROOT/'progress.json');p['status']='paused_by_capacity_layout_gate';p['internalReady']=False;p['formalAcceptedCount']=0;p['checkpoint']=str(ROOT/'capacity-gate-checkpoint.json');p['updatedAt']=datetime.now(timezone.utc).isoformat();save(ROOT/'progress.json',p)
print(json.dumps({'conditionsReplayed':len(checks),'allExact':cp['conditionReplayAllExact'],'nativeRecords':len(all_native),'checkpoint':str(ROOT/'capacity-gate-checkpoint.json'),'checkpointSha256':sha(ROOT/'capacity-gate-checkpoint.json'),'qaReviewSha256':cp['qaReviewSha256']}))

