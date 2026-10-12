from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
p=json.loads((Q/'proposal-v05.json').read_text());now=datetime.now(timezone.utc).isoformat()
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def wr(f,d):f.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
checks=[]
for job in p['jobs']:
 mask=np.asarray(Image.open(job['mask']));vals=np.unique(mask).tolist()
 assert vals==[0,255] and int((mask>0).sum())==job['selectedPixels']
 assert sha(job['source'])==job['sourceSha256'] and sha(job['mask'])==job['maskSha256']
 checks.append({'id':job['id'],'sourceHashVerified':True,'maskHashVerified':True,'binaryMaskValues':vals,'selectedPixels':job['selectedPixels']})
for o in p['outputs']:
 assert sha(o['file'])==o['sha256'] and sha(o['sourceID'])==o['sourceIDSha256']
 a=np.asarray(Image.open(o['file']).convert('RGB'));b=np.asarray(Image.open(o['base']).convert('RGB'));ids=np.asarray(Image.open(o['sourceID']))
 assert np.array_equal(a[1996:],b[1996:]) and np.array_equal(a[ids==0],b[ids==0])
review={'createdAt':now,'reviewer':'coordinate_audit','proposal':str(Q/'proposal-v05.json'),'status':'roof_object_candidate_acceptable_with_minor_material_notes','scope':'Existing E/F02/G native roof object ownership and its actual100percent boundary crops; no formal tile or external acceptance.','formalAccepted':False,
'primaryFindings':['G gold object has no remaining x1651 rectangular material bar in v05.','E/F02 cut x692 preserves the curved lowest blue tile rim; F01 at same cut was rejected for about5–8px phase shift.','The v04 mask lower-edge omission near G local x695 was corrected in v05; complete G lower gold silhouette is retained.','New y1996 rectangular wood band is absent. All candidate rows y1996 onward are exactly unchanged from older base.','Blue tile ends, gold medallions and gold-to-blue silhouette remain connected in inspected current trial crops.'],
'materialNotes':[{'location':'r09c12 x2004, roughly y742..1200','severity':'minor_texture_transition','finding':'At G right coverage limit a narrow paint-value/brush-texture change is visible at100percent. Gold silhouette/highlight direction remain aligned; substantially smaller than rejected x1651 block. Original RGB retained.','evidence':'full-object-g-right-v05.png'},{'location':'r09c12 y2048, wood posts below roof','severity':'inherited_minor_wood_texture_transition','finding':'Visible horizontal brush/value change inherited from v06 base. Beam outlines and diagonal lighting boundary continue. Distinct from rejected newly inserted y1996 stripe.','evidence':'full-object-bottom-v05.png'},{'location':'r09c11 x3814 (r09c12 relative x=-282), blue roof','severity':'minor_texture_transition','finding':'Narrow tone/brush-texture join visible in blue; gutter geometry and tile lip remain continuous. No new silhouette break.','evidence':'full-object-e-left-v05.png'}],
'recommendation':'Use only proposal-v05 as reviewed starting point. Preserve native source coordinates and binary masks; root performs final per-source-ID replay, whole shared-edge QA and formal decision. Do not adopt prior v01–v04 trials.',
'maskAndSourceChecks':checks,'sourceIdSemantics':p['sourceIdRule'],'outputHashes':[{'file':o['file'],'sha256':o['sha256'],'sourceID':o['sourceID'],'sourceIDSha256':o['sourceIDSha256']} for o in p['outputs']],
'reviewedOriginalPixelCrops':[e['file'] for e in p['evidence']], 'viewedPreview':'full-object-preview-v05.png',
'previousTrialDisposition':{'v01':'rejected: F01 x692 breaks tile rim; original gold bar remains','v02':'rejected: G mask empty because floodfill image was read-only; source replay remained exact but intended G replacement absent','v03':'rejected: same empty G mask; source unchanged','v04':'superseded: G applied, small lower silhouette omission near G x695 required v05'}}
pairs=[]
for name in ['ef','roofwood-left','bottom','e-left']:
 a=Q/f'full-object-{name}-v04.png';b=Q/f'full-object-{name}-v05.png'
 same=Image.open(a).tobytes()==Image.open(b).tobytes()
 if same:pairs.append({'v05':str(b),'pixelIdenticalToViewedV04':True})
 else:print('Re-view needed',name)
review['inheritedExactCropReviews']=pairs
wr(Q/'independent-review-v05.json',review)
p['status']='roof_object_candidate_acceptable_with_minor_material_notes';p['knownBlocker']=None;p['review']=str(Q/'independent-review-v05.json');p['formalAccepted']=False;p['previousTrialSuperseded']=['v01','v02','v03','v04'];wr(Q/'proposal-v05.json',p)
print(json.dumps({'review':str(Q/'independent-review-v05.json'),'proposalSha256':sha(Q/'proposal-v05.json'),'outputs':review['outputHashes'],'status':review['status']},indent=2))

