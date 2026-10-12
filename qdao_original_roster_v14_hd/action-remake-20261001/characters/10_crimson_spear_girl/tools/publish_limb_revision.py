from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,copy,io,argparse
R=Path(__file__).resolve().parents[1].resolve()
W=R/'full-limb-review-20261004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
args=argparse.ArgumentParser();args.add_argument('--apply',action='store_true');a=args.parse_args()
def apply_staged():
    plan=load(W/'publish-staging/plan.json')
    # Validate the complete durable stage before touching runtime, including on resume.
    for item in plan['items']:
        p=(R/item['stage']).resolve();dest=(R/item['destination']).resolve()
        assert p.is_relative_to(W/'publish-staging') and dest.is_relative_to(R/'runtime')
        assert sha(p)==item['meta']['sha256']
    for item in plan['items']:
        dest=R/item['destination']
        write(R/item['oldSnapshot'],item['oldRecord']);write(R/item['sourceSnapshot'],item['sourceRecord'])
        dest.write_bytes((R/item['stage']).read_bytes())
        write(Path(str(dest)+'.generation.json'),item['meta'])
    target=plan['delivery']
    for frames in target['groups'].values():
        for f in frames:assert sha(R/f['file'])==f['sha256']
    write(R/'delivery-current.json',target)
    (R/'SHA256SUMS.txt').write_text('\n'.join(f['sha256']+'  '+f['file'] for fs in target['groups'].values() for f in fs)+'\n',encoding='utf-8')
    write(W/'publish-report.json',plan['report'])
    write(W/'publish-journal.json',{'status':'complete','stagePlan':'full-limb-review-20261004/publish-staging/plan.json'})
    print(json.dumps({k:v for k,v in plan['report'].items() if k!='slots'}))
if (W/'publish-journal.json').exists() and load(W/'publish-journal.json')['status']=='in-progress':
    assert a.apply,'An interrupted publication is staged; rerun with --apply to resume the exact prepared outputs.'
    apply_staged();raise SystemExit(0)
D=load(R/'delivery-current.json');before=copy.deepcopy(D)
assert not (W/'publish-report.json').exists(),'already published; do not apply runtime remapping twice'
rows={group+'/'+str(f['frame']).zfill(2):f for group,fs in D['groups'].items() for f in fs}
selected={}
for p in W.glob('*/selection.json'):
    selected.update(load(p).get('slots',{}))
assert selected and {k.split('/')[1] for k in selected}.issubset({'N','NE','E','SE','S','SW','W','NW'})
approval=load(W/'approved-slots.json')
required=set(approval['slots'])
assert approval['status']=='visually-approved' and required
audit=load(W/'pre-repair-frame-review.json')
assert set(audit['unresolvedSlots']).issubset(required),'Known failing slots must all be repaired before publication'
assert set(selected)==required,'Selection differs from the independently reviewed approval set'
assert sha(R/'delivery-current.json')==approval['beforeInventorySHA256'],'Runtime changed after visual approval'
prepared={};native_unique=set();summary=[]
for slot,value in selected.items():
    assert slot in rows
    value=value if isinstance(value,str) else value.get('file') or value.get('path')
    src=(R/value).resolve();assert src.is_relative_to(R)
    dest=R/rows[slot]['file'];old=load(Path(str(dest)+'.generation.json'))
    im=Image.open(src);im.load();assert im.mode=='RGBA'
    source_record=Path(str(src)+'.generation.json');m=load(source_record)
    assert sha(src)==m['sha256'],str(src)
    old_snap=W/'prior-runtime-records'/(slot.replace('/','-')+'.json')
    source_snap=W/'input-record-snapshots'/(slot.replace('/','-')+'.json')
    now=datetime.now(timezone.utc).isoformat()
    if src.is_relative_to(R/'runtime'):
        assert im.size==(1024,1024)
        meta=copy.deepcopy(m);evidence=meta['nativeEvidence']
        source_frame=m['playbackFrame']
        operation='existing independent pose reassigned once in playback order; pixels unchanged'
        data=src.read_bytes()
    elif im.size==(1254,1254):
        buf=io.BytesIO();im.resize((1024,1024),Image.Resampling.LANCZOS).save(buf,format='PNG');data=buf.getvalue()
        evidence={'historicalFile':src.relative_to(R).as_posix(),'sha256':sha(src),'size':[1254,1254],'mode':'RGBA','generationRecord':source_record.relative_to(R).as_posix(),'recordSHA256':sha(source_record)}
        source_frame=int(slot.split('/')[-1]);meta={}
        operation='builtin independently redrawn pose; whole1254 canvas resampled to1024 without translation'
    else:
        assert im.size==(1024,1024) and 'nativeEvidence' in m, str(src)
        data=src.read_bytes();meta=copy.deepcopy(m);evidence=meta['nativeEvidence'];source_frame=int(slot.split('/')[-1])
        operation='independently drawn pose, documented head/hip/spear scale registration; no foot-bottom alignment'
    evidence=copy.deepcopy(evidence)
    evidence['historicalFile']=evidence.get('historicalFile') or evidence['file']
    evidence['historicalFile']=evidence['historicalFile'].replace('\\','/')
    evidence['generationRecord']=evidence['generationRecord'].replace('\\','/')
    evidence_record=R/evidence['generationRecord']
    if 'recordSHA256' in evidence:assert evidence['recordSHA256']==sha(evidence_record)
    evidence['recordSHA256']=sha(evidence_record)
    evidence.setdefault('mode','RGBA')
    native_path=R/evidence['historicalFile']
    if native_path.exists():assert sha(native_path)==evidence['sha256']
    assert evidence['sha256'] not in native_unique,'duplicate selected native '+slot
    native_unique.add(evidence['sha256'])
    out_sha=hashlib.sha256(data).hexdigest()
    meta.update(file=dest.relative_to(R).as_posix(),sha256=out_sha,width=1024,height=1024,mode='RGBA',exportedAt=now,operation=operation,nativeEvidence=evidence,sourceFrame=source_frame,playbackFrame=int(slot.split('/')[-1]),frameDurationMs=rows[slot]['durationMs'],actualModel=None,actualQuality=None,unverifiedReason='host built-in tool does not disclose actual model/quality',clientIntegrated=False,priorRuntime={'sha256':old['sha256'],'generationRecord':old_snap.relative_to(R).as_posix()},selectedInput={'historicalFile':src.relative_to(R).as_posix(),'sha256':sha(src),'recordSnapshot':source_snap.relative_to(R).as_posix()})
    rows[slot].update(sha256=out_sha,nativeSHA=evidence['sha256'],nativeSize=evidence['size'],nativeSource=evidence['historicalFile'],sourceFrame=source_frame,fullLimbRevision='20261005-anatomy')
    prepared[slot]=(dest,data,meta,old_snap,old,source_snap,m)
    summary.append({'slot':slot,'selectedSource':src.relative_to(R).as_posix(),'oldSHA':old['sha256'],'newSHA':out_sha,'nativeSHA':evidence['sha256']})
# All input images/records have been read before any output mutation.
pixels=set()
for slot,f in rows.items():
    im=Image.open(io.BytesIO(prepared[slot][1])) if slot in prepared else Image.open(R/f['file'])
    assert im.size==(1024,1024) and im.mode=='RGBA'
    box=im.getchannel('A').point(lambda x:255 if x>=32 else 0).getbbox()
    assert box and box[0]>0 and box[1]>0 and box[2]<1024 and box[3]<1024,(slot,box)
    h=hashlib.sha256(im.tobytes()).hexdigest();assert h not in pixels,slot;pixels.add(h)
report={'status':'applied' if a.apply else 'dry-run','selectedSlots':len(summary),'changedPixels':sum(x['oldSHA']!=x['newSHA'] for x in summary),'uniqueRuntimePixels':len(pixels),'battleUnchanged':all(not x['slot'].startswith(('hit/','attack/','cast/')) or x['oldSHA']==x['newSHA'] for x in summary),'runtimeStagedBeforeWrite':True,'slots':summary}
if a.apply:
    write(W/'delivery-before.json',before)
    D.update(updatedAt=datetime.now(timezone.utc).isoformat(),fullLimbRevision='20261005-anatomy',orders={},phaseWeightsApplied=False)
    stage=W/'publish-staging';stage.mkdir(parents=True,exist_ok=True);items=[]
    for slot,(dest,data,meta,old_snap,old,source_snap,m) in prepared.items():
        staged=stage/(slot.replace('/','-')+'.png');staged.write_bytes(data)
        items.append({'slot':slot,'stage':staged.relative_to(R).as_posix(),'destination':dest.relative_to(R).as_posix(),'meta':meta,'oldSnapshot':old_snap.relative_to(R).as_posix(),'oldRecord':old,'sourceSnapshot':source_snap.relative_to(R).as_posix(),'sourceRecord':m})
    report['durableStageBeforeWrite']=True
    write(stage/'plan.json',{'items':items,'delivery':D,'report':report})
    write(W/'publish-journal.json',{'status':'in-progress','stagePlan':(stage/'plan.json').relative_to(R).as_posix()})
    apply_staged();raise SystemExit(0)
else:write(W/'publish-plan.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='slots'}))
