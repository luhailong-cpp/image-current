"""Save current exact 4K candidate and reuse unchanged native QA without previews."""
from pathlib import Path
from PIL import Image
import numpy as np
import json, hashlib
from datetime import datetime, timezone

Z=Path(__file__).resolve().parent; T=Z/'r09_c08'; Q=T/'qa/complete-native-20261013-v2'
Q.mkdir(parents=True,exist_ok=False)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    with Path(p).open('x',encoding='utf-8') as f: json.dump(d,f,indent=2,ensure_ascii=False)
selection=T/'selected-patches.json'; before=selection.read_bytes(); sel=read(selection)
assert len(sel['patches'])==16
canvas=np.zeros((4096,4096,3),dtype=np.uint8); sources=[]
for pid,rel in sorted(sel['patches'].items()):
    path=T/rel; pixels=np.asarray(Image.open(path).convert('RGB')); assert pixels.shape==(1254,1254,3)
    x,y=(int(pid[2])-1)*1024,(int(pid[1])-1)*1024
    canvas[y:y+1024,x:x+1024]=pixels[115:1139,115:1139]
    item={'patch':pid,'file':str(path),'sha256':sha(path),'dimensions':[1254,1254],'crop':[115,115,1139,1139],'destination':[x,y]}
    if Path(rel).parts[0]=='native':
        receipt=read(T/(path.stem+'.receipt.json')); raw=Path(receipt['sourcePath'])
        assert np.array_equal(pixels,np.asarray(Image.open(raw).convert('RGB')))
        item.update(actualBuiltinRaw=str(raw),actualBuiltinRawSha256=sha(raw),rawPixelReplayExact=True,actualModel=None)
    else:
        adoption=read(T/'processed/bracket-joint-20261013-v2/adoption-completed.json')
        rec=next(r for r in adoption['adopted'] if r['patch']==pid)
        assert rec['sha256']==sha(path)
        item.update(sourceProof=adoption['adoptionTimeReplay'],sourceProofSha256=sha(adoption['adoptionTimeReplay']),
                    provenance='previously independently replayed same-coordinate AI raw masks; adopted image hash unchanged')
    sources.append(item)
candidate=Q/'candidate-4096.png'; Image.fromarray(canvas).save(candidate)
assert np.array_equal(canvas,np.asarray(Image.open(candidate).convert('RGB')))
old=read(T/'qa/complete-native-20261013-v1/manifest.json')
new=read(T/'qa/p13-quick-20261013-v2/manifest.json')
new_names={Path(e['file']).name for e in new['evidence']}
evidence=[dict(e,reusedUnchangedPixels=True) for e in old['evidence'] if Path(e['file']).name not in new_names]
evidence += [dict(e,reusedUnchangedPixels=False) for e in new['evidence']]
assert len(evidence)==33
current_hashes={i['patch']:i['sha256'] for i in sources}
for e in evidence:
    assert sha(e['file'])==e['sha256']
    for source in e['sources']: assert current_hashes[source['patch']]==source['sha256']
    x0,y0,x1,y1=e['globalBox']; box=(x0-28672,y0-32768,x1-28672,y1-32768)
    assert np.array_equal(canvas[box[1]:box[3],box[0]:box[2]],np.asarray(Image.open(e['file']).convert('RGB')))
    e['currentExactCoreReplay']=True
issues=[
 {'id':'stone-material-density','status':'pending','description':'Stone mineral texture differs between rows and across p22/p23/p24; p22-v2 retained repetitive fine lattice after targeted edit. Surface density and clarity transitions remain visible.'},
 {'id':'p13-east-paving','status':'pending','description':'p13-v2 improved the large right-edge groove discontinuity from v1, but stone edge/finish transitions against p14 remain visible; not accepted.'},
 {'id':'roof-fascia-color','status':'pending','description':'p43/p44 and adjacent roof highlights/fascia retain a color seam outside the adopted bracket repair.'},
 {'id':'window-external','status':'pending','description':'p44/r10_c08 p14 duplicated diamond window motif; independent joint repair assigned to north agent, no candidate adopted.'},
 {'id':'external-seams','status':'pending','description':'New full tile requires current available external edge QA; absence of local west neighbor does not establish global absence.'}]
now=datetime.now(timezone.utc).isoformat()
proof={'createdAt':now,'tile':'r09_c08','candidate':str(candidate),'candidateSha256':sha(candidate),
 'candidateDimensions':[4096,4096],'exactNativeCoreReplay':True,'sources':sources,
 'rawPixelReplayedCount':14,'unchangedPreviouslyReplayedMaskedNativeCount':2,
 'artResampling':False,'artBlur':False,'artBlending':False,'layoutPixelsUsed':False,
 'evidence':evidence,'unchangedEvidenceReusedCount':28,'newlyViewedEvidenceCount':5,
 'nativeQAViewedOrHashReusedCount':33,'internalReady':False,'formalAccepted':False,'pendingIssues':issues}
write(Q/'independent-replay-and-review.json',proof)
write(Q/'manifest.json',dict(proof,selection=str(selection),selectionSha256=sha(selection),selectedCount=16))
write(Q/'selection-before-final-record.json',sel)
assert selection.read_bytes()==before
sel.update(candidate=str(candidate),candidateSha256=sha(candidate),status='full_native_candidate_material_and_external_repairs_pending',
 internalReady=False,formalAccepted=False,materialPending=True,internalReview=str(Q/'independent-replay-and-review.json'),updatedAt=now)
pending=sel.setdefault('pendingIssues',[]); ids={p.get('id') for p in pending if isinstance(p,dict)}
pending.extend(i for i in issues if i['id'] not in ids)
selection.write_text(json.dumps(sel,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'nativePositions':16,'QAReused':28,'QANew':5,'internalReady':False,'formalAccepted':False}))
