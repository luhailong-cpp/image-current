"""Verify only final exported files and immutable text evidence; source PNGs may be cleaned."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
from export_review_runtime import edge_counts
B=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok,message):
    if not ok: raise ValueError(message)

def verify():
    m=read(B/'manifest.json');a=read(B/'acceptance.json')
    check(m['status']==a['status'] and m['status'] in ('passed','ready_with_review_limit'),'Unknown delivery status')
    check(a['visualApproval']=='passed' and a['reviewedAt'],'Static review incomplete')
    if m['status']=='passed':check(a['dynamicApproval']=='passed','Dynamic review incomplete')
    else:check(a['dynamicApproval']=='incomplete' and a['browserAccessLimit'] and len(a['remainingDynamicSequences'])==7,'Missing explicit browser review limit')
    check(m['acceptance']['sha256']==sha(B/'acceptance.json') and m['acceptance']['record']==a,'Acceptance changed')
    check(sha(B/m['selectionSource']['file'])==m['selectionSource']['sha256']==a['previewManifestSha256'],'Selection changed')
    spec={'run':(['N','NE','E','SE','S','SW','W','NW'],16,60),'hit':(['E','W'],6,40),
          'attack':(['E','W'],12,30),'cast':(['E','W'],16,45)}
    timing=read(B/'animation-timing.json')
    for action,(_,count,ms) in spec.items():
        check((timing[action]['frameMs'],timing[action]['cycleMs'])==(ms,count*ms),'Timing configuration differs from formal manifest')
    contact=read(B/'review/contact-pairs-current-20261004.json')
    check((contact['frameMs'],contact['cycleMs'],contact['pairMs'])==(60,960,120),'Stale run contact timing')
    expected={(act,d) for act,(ds,_,_) in spec.items() for d in ds}
    check(len(m['sequences'])==14 and {(s['action'],s['direction']) for s in m['sequences']}==expected,'Wrong sequences')
    rows={}; pixelhashes={}; physical=set()
    for s in m['sequences']:
        _,count,ms=spec[s['action']]
        check((s['count'],s['ms'],s['cycleMs'])==(count,ms,count*ms),'Wrong duration')
        check(len(s['frames'])==count and [f['frame'] for f in s['frames']]==list(range(1,count+1)),'Wrong order')
        for f in s['frames']:
            slot=f"{s['action']}-{s['direction']}-{f['frame']:02d}"
            check(f['slot']==slot and f['durationMs']==ms and f['status']=='passed','Frame mismatch')
            p=B/f['file']; physical.add(p.resolve());h=sha(p)
            check(h==f['sha256']==a['runtimeFrameSha256'][slot],'Frame SHA mismatch')
            check(f['event']==('hit_contact' if s['action']=='attack' and f['frame']==6 else
                              'cast_release' if s['action']=='cast' and f['frame']==10 else None),'Event mismatch')
            g=f['generationRecord'];gp=B/g['file'];r=read(gp)
            check(sha(gp)==g['sha256'] and r==g['record'] and r['sha256']==h,'Receipt changed')
            check(r['derivedFrom']['sha256']==f['sourceSha256']==r['sourceGenerationRecord']['record']['sha256'],'Source chain mismatch')
            check(r['transform']=={'type':'uniform_full_canvas_resize','filter':'LANCZOS','crop':None,'translation':[0,0],'alphaCleanup':False},'Unexpected pixel transform')
            source=r['sourceGenerationRecord']['record']
            for field in ('actualModel','actualQuality','configSnapshot','submittedParameters'):
                check(r[field]==source[field],'Generation evidence changed')
            with Image.open(p) as im:
                im.load();check(im.format=='PNG' and im.mode=='RGBA' and im.size==(1024,1024),'Invalid PNG')
                check(im.getchannel('A').getextrema()==(0,255),'Invalid alpha')
                edges=edge_counts(im);check(not any(edges.values()),'Clipped outer edge')
                ph=hashlib.sha256(im.tobytes()).hexdigest()
                check(ph not in pixelhashes,'Duplicate pixel frame: '+slot)
                pixelhashes[ph]=slot
            rows[slot]=h
    check(len(rows)==196 and physical=={p.resolve() for p in (B/'runtime').rglob('*.png')},'Wrong physical PNG set')
    d=read(B/'preview/delivery-data.json')
    check(d['status']==m['status'] and d['clientIntegrated']==False,'Wrong preview status')
    from plan_final_cleanup import validate_delivery
    by_slot={f['slot']:f for s in m['sequences'] for f in s['frames']}
    validate_delivery(by_slot,physical)
    return {'status':'passed','assetDeliveryStatus':m['status'],'dynamicApproval':a['dynamicApproval'],'checkedAt':datetime.now(timezone.utc).isoformat(),
            'manifestSha256':sha(B/'manifest.json'),'acceptanceSha256':sha(B/'acceptance.json'),
            'runtimeFrames':196,'sequences':14,'distinctPixelFrames':196,
            'allCanvas1024RGBA':True,'allOuterEdgesGT128Zero':True,
            'durationsAndEvents':'passed','generationReceipts':'passed','deliveryReferences':'passed',
            'sourcePngRequired':False,'clientIntegrated':False,'clientRuntimeAcceptance':'not_tested'}

try:
    result=verify()
except Exception as e:
    result={'status':'failed','error':str(e)}
(B/'review/final-package-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
if result['status']!='passed':raise SystemExit(2)
