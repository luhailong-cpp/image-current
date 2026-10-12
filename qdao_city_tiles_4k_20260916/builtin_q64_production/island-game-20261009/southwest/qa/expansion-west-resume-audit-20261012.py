from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':p.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
index=ROOT/'qa/expansion-west-worker-map.json';d=load(index)
freeze=ROOT/'qa/expansion-west-migration-freeze-20261011.json'
auth=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
reqpath=ROOT/'prompts/r10_c02_s04_03_v01.request.json';req=load(reqpath)
errors=[];records=[]
for p in sorted((ROOT/'native').glob('*.png.generation.json')):
    stem=p.name.removesuffix('.png.generation.json')
    if not re.fullmatch(r'r(?:09|10|11|12|13|14)_c0[12]_s\d{2}_\d{2}_v\d{2}',stem):continue
    record=load(p);np=ROOT/'native'/(stem+'.png');receipt=ROOT/'receipts'/(stem+'.tool.json')
    okay=np.exists() and sha(np)==record.get('sha256') and receipt.exists()
    if not okay:errors.append(stem)
    records.append({'stem':stem,'native':meta(np),'generationRecord':meta(p),'receipt':meta(receipt),'verified':okay})
refs=[]
for ref in req['references']:
    m=meta(ref['path']);m['matchesSavedRequest']=m['sha256']==ref['sha256'];refs.append(m)
    if not m['matchesSavedRequest']:errors.append(ref['path'])
prompt=meta(req['promptPath']);prompt['matchesSavedRequest']=prompt['sha256']==req['promptSha256']
if not prompt['matchesSavedRequest']:errors.append(req['promptPath'])
resume={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'production_resume_authorized_but_new_generation_held_for_current_permission_recovery',
'authorization':meta(auth),'historicalFreeze':meta(freeze),'historicalFreezeUnmodified':True,
'currentNewBlocker':{'literalError':'Fatal error: application network permission was revoked','observedAtUtc':'2026-10-12T11:47:28Z','source':'Parent /root direct collaboration message reports current resumed NORTH and EAST agent turn failures. This worker did not invoke image_gen and did not directly receive a new tool failure.','parentInstruction':'No generation or network retry before user restores permission; local verification only.'},
'workerInvokedNewGeneration':False,'workerDirectPermissionFailure':False,'generationInFlight':False,'unsavedSuccessfulToolResults':False,'newSuccessfulNativeCount':0,
'selectedMap':meta(index),'selectedNativeCount':d['selectedNativeCount'],'retainedSuccessfulNativeFiles':len(records),
'selectedArraySnapshot':{t:d[t] for t in d['assignedTiles']},'nativeInventoryVerification':records,'verificationErrors':errors,
'candidateArtifacts':d.get('candidateArtifacts',{}),'currentPreparedRequest':meta(reqpath),'requestStem':req['stem'],'requestSubmitted':False,
'preparedNativeAlreadyExists':(ROOT/'native'/(req['stem']+'.png')).exists(),'prompt':prompt,'references':refs,
'nextActionAfterPermissionRestored':'View existing guide and three mandatory references, then submit r10_c02_s04_03_v01 once. Continue full exclusive west assignment. Do not regenerate saved sources.',
'pendingRepairReview':meta(ROOT/'qa/c04-hardseam-west-r09c02-v01-review.json'),
'preservation':'No old native, prompt, guide, preview, QA, freeze or audit was modified; no Git state changed; main progress/map untouched.'}
out=ROOT/'qa/expansion-west-production-resume-20261012.json'
out.write_text(json.dumps(resume,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'path':out.as_posix(),'selected':d['selectedNativeCount'],'retainedNative':len(records),'verificationErrors':errors,'inFlight':False,'unsavedSuccess':False,'directNewPermissionFailure':False,'newImageGenCalls':0}))

