"""Promote reviewed fixed-registration exports; never infer visual acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
SPEC={'run':(['N','NE','E','SE','S','SW','W','NW'],16,75),'hit':(['E','W'],6,40),'attack':(['E','W'],12,30),'cast':(['E','W'],16,45)}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
accept=load(ROOT/'provenance/offline-acceptance.json')
assert accept['offlineArtworkAccepted'] is True
native=load(ROOT/'candidate-selection.json');registered=load(ROOT/'registered-selection.json')
expected={(a,d,f) for a,(dirs,n,ms) in SPEC.items() for d in dirs for f in range(1,n+1)}
key=lambda r:(r['action'],r['direction'],r['frame'])
assert len(native)==len(registered)==len(expected)==196
assert {key(r) for r in native}=={key(r) for r in registered}==expected
nativeMap={key(r):r for r in native};accepted=accept['nativeSha256BySlot']
assert len({r['sha256'] for r in native})==196
assert all(accepted['/'.join(map(str,key(r)))]==r['sha256'] for r in native)
for a,(dirs,n,ms) in SPEC.items():
    for d in dirs:assert accept['sequences'][a+'/'+d]['accepted'] is True
rows=[]
for r in registered:
    original=nativeMap[key(r)];source=ROOT/r['file'];export=load(ROOT/r['generationRecord'])
    assert sha(source)==r['sha256']==export['sha256']
    assert sha(ROOT/original['file'])==original['sha256']==export['source']['sha256']
    with Image.open(source) as im:
        im.load();assert im.size==(1024,1024) and im.mode=='RGBA'
    assert export['edgeMaxAlpha']==0 and not export['transform']['perFrameNormalization']
    out=f"final/{r['action']}/{r['direction']}/{r['frame']:02}.png";dest=ROOT/out
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    record=out+'.generation.json';full=load(ROOT/original['generationRecord'])
    doc={**export,'file':out,'status':'offline_artwork_accepted_client_pending','sourceGeneration':full,'nativeSourceRecord':original['generationRecord'],'finalVisualPassed':True,'offlineAcceptance':'provenance/offline-acceptance.json','clientValidated':False,'sourceRetention':'native/intermediate PNG removed after final-reference verification per user policy; text lineage retained'}
    save(ROOT/record,doc)
    rows.append({'action':r['action'],'direction':r['direction'],'frame':r['frame'],'file':out,'generationRecord':record,'sha256':sha(dest),'nativeSourceFile':original['file'],'nativeSha256':original['sha256'],'visualStatus':'离线手脚/持琴/比例/透明合成复核通过；客户端未接入验收','finalVisualPassed':True,'clientValidated':False})
reg=load(ROOT/'registration.json')
manifest={'schemaVersion':1,'character':'05_celestial_musician_girl','builtAt':datetime.now(timezone.utc).isoformat(),'status':'offline_artwork_complete_client_pending','canvas':[1024,1024],'mode':'RGBA','frameCount':196,'specifications':{a:{'directions':ds,'framesPerDirection':n,'frameMs':ms,'cycleOrClipMs':n*ms} for a,(ds,n,ms) in SPEC.items()},'root':reg['targetRoot'],'pivotBottomOrigin':reg['pivotBottomOrigin'],'registration':'registration.json','runTiming':'1200ms uniform cycle, 75ms per frame; fast options removed; client movement-speed match untested','frames':rows,'clientIntegrated':False,'clientRuntimeValidated':False}
save(ROOT/'final/manifest.json',manifest);save(ROOT/'final-selection.json',rows)
status=load(ROOT/'STATUS.json');status.update({'updatedAt':manifest['builtAt'],'status':manifest['status'],'finalVisualPassed':196,'exported1024RGBA':196,'completeSequences':14,'clientIntegrated':False,'clientRuntimeValidated':False,'remaining':{a:0 for a in SPEC},'limitations':['离线素材完成；客户端接入与实际世界位移下脚滑/观感未验收。','工具未披露实际模型/质量，保留配置目标与提交/返回证据，不声称已锁定型号。']})
status['root'].update({'appliedToExports':True,'rule':reg['method'],'registrationFile':'registration.json','globalScale':reg['globalScale'],'pivot':reg['pivotBottomOrigin']})
for item in status['sequences'].values():item['visualPassed']=True
save(ROOT/'STATUS.json',status)
print(json.dumps({'formalFrames':len(rows),'size':'1024 RGBA','uniqueSha256':len({r['sha256'] for r in rows}),'clientValidated':False},ensure_ascii=False))
