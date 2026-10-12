from pathlib import Path
import sys,json,hashlib,datetime
from PIL import Image
z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(z));import assemble_tile
q=z/'qa/r07_c03_v7_internal_review_20261013';q.mkdir(exist_ok=False)
im=Image.open(z/'tiles/r07_c03_candidate-v7_4096.png').convert('RGB')
idx=assemble_tile.save_qa(q,im)
(q/'qa_index.json').write_text(json.dumps(idx,indent=2),encoding='utf8')
old=json.loads((z/'qa/r07_c03_v1_owner_native33_review_20261013.json').read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
items=[]
for item in old['items']:
 p=q/Path(item['path']).name
 same=sha(p)==item['sha256']
 items.append({**item,'path':p.as_posix(),'sha256':sha(p),'reusedUnchangedPass':same and item['result']=='PASS','result':'PASS' if same and item['result']=='PASS' else 'REVIEW_REQUIRED','ownerRootViewedAtNative100Percent':same and item['result']=='PASS'})
extras=[]
for n,b in [('cream_right_boundary',[1550,850,2150,1580]),('door_lower_boundary',[600,2100,1854,2950]),('side_lower_boundary',[2842,800,4096,1750])]:
 p=q/(n+'.png');im.crop(b).save(p);extras.append({'path':p.as_posix(),'sha256':sha(p),'box':b})
record={'candidate':{'path':(z/'tiles/r07_c03_candidate-v7_4096.png').as_posix(),'sha256':sha(z/'tiles/r07_c03_candidate-v7_4096.png')},'reusedPassCount':sum(i['reusedUnchangedPass'] for i in items),'items':items,'extraBoundaryCrops':extras,'internalClosurePassed':False,'formalAccepted':False,'pendingIssue':'gold eave step at tile(2208,600); second local repair failed to improve, deferred per AGENTS','rejectedAdditionalSource':'native/r07_c03_front_gold_cap_a02.png','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(q/'review-in-progress.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'reused':record['reusedPassCount'],'review':[Path(i['path']).name for i in items if i['result']!='PASS'],'extra':extras}))
