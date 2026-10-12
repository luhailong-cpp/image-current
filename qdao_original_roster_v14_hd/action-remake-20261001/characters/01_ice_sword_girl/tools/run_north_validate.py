from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=sys.argv[1];p=ROOT/'review'/f'run-{d}-selection.json';j=json.loads(p.read_text(encoding='utf-8'));rows=[]
assert [f['frame'] for f in j['frames']]==list(range(1,17))
assert j['timing']['frameDurationsMs']==[75]*16
for f in j['frames']:
    out=ROOT/f['path'];src=ROOT/f['sourcePath'];gr=ROOT/f['generationRecord']
    g=json.loads(gr.read_text(encoding='utf-8'));ng=json.loads((src.with_name(src.name+'.generation.json')).read_text(encoding='utf-8'))
    ni=Image.open(src);oi=Image.open(out)
    assert ni.mode=='RGBA' and min(ni.size)>=1024
    assert oi.mode=='RGBA' and oi.size==(1024,1024)
    assert ni.getchannel('A').getextrema()==(0,255) and oi.getchannel('A').getextrema()==(0,255)
    assert f['sha256']==g['sha256']==sha(out)
    assert f['sourceSha256']==g['derivedFrom']['sha256']==sha(src)
    assert (ROOT/g['derivedFrom']['generationRecord']).is_file()
    assert g['operation']['name']=='whole_canvas_uniform_downscale'
    assert g['operation']['translation']==[0,0] and g['operation']['crop'] is None
    assert ng['actualModel'] is None and ng['actualQuality'] is None
    assert f['durationMs']==75
    rows.append({'frame':f['frame'],'sourcePath':f['sourcePath'],'path':f['path'],'nativeSize':list(ni.size),'candidateSize':list(oi.size),'nativeSha256':sha(src),'candidateSha256':sha(out),'alphaExtrema':[0,255],'status':'technical_pass_only'})
assert len(set(x['nativeSha256'] for x in rows))==16
assert len(set(x['candidateSha256'] for x in rows))==16
result={'direction':d,'checkedAt':datetime.now(timezone.utc).isoformat(),'candidateCount':16,'uniqueNativeCount':16,'timing':{'frameMs':75,'cycleMs':1200},'method':'native>=1024 RGBA with alpha, fullcanvas1024 derivative and exact source/hash/record linkage; visual review separate','clientRuntimeVerified':False,'frames':rows}
(ROOT/'review'/f'run-{d}-technical.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
j['artStatus']='static_reviewed_candidates_dynamic_review_pending';j['nativeCanvasSize']=[1254,1254];j['timing']['uniformCycleMs']=1200;j['visualReviewDocument']=f'review/run-{d}-visual-review.md';j['technicalReviewDocument']=f'review/run-{d}-technical.json';j['contactSheet']=f'review/run-{d}-contact.png';p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'direction':d,'candidateCount':16,'uniqueNativeCount':16,'all75ms':True,'cycleMs':1200,'lineageHashesAlpha':'pass'}))

