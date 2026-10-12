"""Read-only source QA; write exact native-core evidence under own folder."""
import sys,json,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
sys.path.insert(0,str(BASE))
from review_external_seams import Sources,write_evidence,read_json,sha

sources=Sources()
edges=[('r10c09-east','x',36864,36864),('r10c09-south','y',40960,32768),
       ('r10c10-south','y',40960,36864),('r11c09-east','x',36864,40960),
       ('r10c09-west','x',32768,36864),('r11c09-south','y',45056,32768)]
results=[]
intersections=set()
for name,axis,seam,start in edges:
    for i in range(4):
        lo=start+i*1024
        box=[seam-256,lo,seam+256,lo+1024] if axis=='x' else [lo,seam-256,lo+1024,seam+256]
        identifier=f'{name}-segment-{i+1}'
        old=BASE/'seam-qa'/'r10_c09'/f'{name.split("-")[-1]}-segment-{i+1}.qa.json'
        dest=HERE/(identifier+'.qa.json')
        if name.startswith('r10c09-') and old.exists() and not dest.exists():
            shutil.copyfile(old,dest)
        results.append(write_evidence(sources,HERE,identifier,box,{'axis':axis,'coordinate':seam,'coordinateInImage':256}))
    for i in range(5):
        intersections.add((seam,start+i*1024) if axis=='x' else (start+i*1024,seam))
for x,y in sorted(intersections):
    identifier=f'intersection-x{x}-y{y}'
    old=BASE/'seam-qa'/'r10_c09'/(identifier+'.qa.json')
    dest=HERE/(identifier+'.qa.json')
    if old.exists() and not dest.exists():shutil.copyfile(old,dest)
    results.append(write_evidence(sources,HERE,identifier,[x-384,y-384,x+384,y+384],{'intersectionGlobal':[x,y],'intersectionInImage':[384,384]}))
summary={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'2x2 shared edges plus currently existing west/south outer edges','formalAccepted':False,'results':results}
(HERE/'manifest.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'evidence':len(results),'sourceComplete':sum(r['sourceComplete'] for r in results),'previousReviewRetained':sum(r['visualReview']['status'].startswith('reviewed') for r in results),'pendingReview':[r['id'] for r in results if r['sourceComplete'] and r['visualReview']['status']=='pending_view_image_review']},ensure_ascii=False))
