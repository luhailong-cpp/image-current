import json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
issues=[{'id':'G1','severity':'blocking_geometry','globalBox':[37780,43900,38200,44400],'object':'wood deck to stone paving boundary at four-patch junction','sources':['r11_c10/p31-v1','r11_c10/p32-v1','r11_c10/p41-v1','r11_c10/p42-v2'],'detail':'Wood starts abruptly at global x37888 and is cut off horizontally at global y44147 (p42 native y230). A disconnected paving T junction also remains near p42 native x230. Requires coherent full-junction redraw and all incoming boundary connections.','evidence':['p32--p42','p41--p42','cross-r3-c1']},
{'id':'Q1','severity':'quality_review_requested','globalBox':[37632,43100,38020,43520],'object':'lower wooden sill and two nail heads','sources':['r11_c10/p31-v1','r11_c10/p32-v1'],'detail':'Left source and inherited left strip visibly softer than fresh p32 detail; no major contour step, but native detail/focus changes near right conditioning boundary. Owner should inspect the complete sill when closing internal QA.','evidence':['p31--p32','cross-r2-c1']}]
for res in manifest['results']:
 if not res['sourceComplete']:continue
 path=Path(res['report']);rec=json.loads(path.read_text(encoding='utf-8'))
 if rec['visualReview']['status']=='reviewed_reused_identical_pixels':continue
 related=[e for e in issues if res['id'] in e['evidence']]
 blockers=[e for e in related if e['severity']=='blocking_geometry']
 rec['visualReview']={'status':'reviewed_independent_with_blocker' if blockers else 'reviewed_independent_native_geometry','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'seam_review','candidateUsable':not bool(blockers),'formalAccepted':False,'structuralBlockers':blockers,'qualityObservations':[e for e in related if e['severity']!='blocking_geometry'],'colorOnlyRisks':[],'scope':'Actual 512px native core strip and 512px native crossing; source hashes locked in evidence','observations':[] if related else ['No visible contour disconnect in exact native crop.']}
 path.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 res['visualReview']=rec['visualReview']
manifest.update(issues=issues,status='partial_internal_review_with_G1_blocker',internalReady=False)
(HERE/'review-round1.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('review-round1.json')
