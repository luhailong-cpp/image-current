from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
stamp=datetime.now(timezone.utc).isoformat()
Q=B/'r09_c06/pipeline/qa/full-20261012-8acb763a3ad68383'
review={'recordedAtUtc':stamp,'reviewer':'root','assembly':str(B/'r09_c06/pipeline/output/8acb763a3ad68383/assembly.json'),'all24NativeInternalStripsViewed':True,'nativeExternalBoundariesViewed':['left r09_c05','right r09_c07','bottom r10_c06'],'overviewViewed':str(Q/'three-tile-overview-RESIZED-QA-ONLY.png'),'formalAccepted':False,'internalPassed':False,'externalPassed':False,'openFindings':[
{'id':'H2-1-wood-tone','severity':'reject','location':'core y2048, column 1','finding':'Triangular light/dark wood quilt boundaries near x100..300 and x700; cream line is continuous but wood material is not.'},
{'id':'H1-3-stone-tone','severity':'reject','location':'core y1024, column 3','finding':'Wavy step-shaped tone change on stone curb face; dense fine pattern remains.'},
{'id':'quiet-stone','severity':'reject','location':'V3 row1','finding':'Paving has dense cellular texture inconsistent with broad quiet grey material.'},
{'id':'left-external-tone','severity':'reject','location':'r09_c05 / r09_c06','finding':'Wood board phase mostly aligned but strong darker/oranger material transition at tile boundary; emblem tone changes.'},
{'id':'right-external-geometry','severity':'reject','location':'r09_c06 / r09_c07 rows2-3','finding':'Red support and crossbar heights/levels differ; duplicated members and cream/grey stone discontinuity.'},
{'id':'bottom-arc-joint','severity':'reject','location':'r09_c06 / r10_c06 columns1-2','finding':'Cream inner/outer arcs step at join; wood tone and grain scale differ.'},
{'id':'bottom-floor','severity':'reject','location':'r09_c06 / r10_c06 column3','finding':'Horizontal wood tone/grain boundary.'},
{'id':'bottom-post-curb','severity':'reject','location':'r09_c06 / r10_c06 column4','finding':'Gold cap/post x-position and width differ, top wood meets lower grey ground; curb/rail topology does not meet.'},
{'id':'macro-ellipse','severity':'reject','location':'r09_c05 and r09_c06 arena','finding':'Arena ellipse angular on c05; p03_01 c06 inner arc remains displaced versus approved guide. Shared arena geometry needs coordinated repair.'}
],'nextAction':'Target native local material repairs plus coordinated cross-tile structure repairs; continue missing tiles in parallel.'}
out=Q/'root-full-review.json';assert not out.exists();atomic_json(out,review)
cat=read(B/'current-candidates.json')
for tile,rel in [('r09_c01','r09_c01/pipeline/output/0310020c9169112c/assembly.json'),('r09_c06','r09_c06/pipeline/output/8acb763a3ad68383/assembly.json'),('r09_c07','r09_c07/repairs-resume-20261012/inner-rim-upper-v01/integrated/assembly.json')]:
    ap=B/rel;a=read(ap)
    core=a.get('output',a.get('candidate'));ctx=a.get('contextOutput',a.get('context'))
    assert core and ctx, list(a)
    for e in [core,ctx]: assert sha(e['file'])==e['sha256']
    assert Image.open(core['file']).size==(4096,4096)
    assert Image.open(ctx['file']).size==(4326,4326)
    e={'tile':tile,'source':'current-native-provisional-with-open-QA','assembly':str(ap),'candidate':core,'context':ctx,'formalAccepted':False,'internalPassed':False}
    if tile=='r09_c06':e['review']=str(out)
    cat['tiles'][tile]=e
cat.update(updatedAtUtc=stamp,complete4kCandidateCount=len(cat['tiles']),formalAcceptedCount=0)
atomic_json(B/'current-candidates.json',cat)
print(json.dumps({'review':str(out),'candidateCount':len(cat['tiles'])}))

