from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/seam-qa/independent-20261010/r11_c08-final-external');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
notes={
'north-segment-1':'Hull plank gaps, rounded rib and lower support connect across horizontal tile boundary. No new outline step seen.',
'north-segment-2':'Hull board lines, large rib and horizontal supports remain connected.',
'north-segment-3':'At old bench repair left edge x31117, upper rim lower outline and one nearby board groove show a small native step. This is inside north neighbor and persists into current assembled context.',
'north-segment-4':'Main rim and rib silhouettes connect, but old repair right boundary x32371 has abrupt vertical shadow/tone cut on deck surface (C2).',
'east-segment-1':'Hull front rim and large rib connect. Front bevel material/shadow changes abruptly at x32768 although silhouette remains coherent.',
'east-segment-2':'Large angled rib, front frame and stone paving silhouettes connect; small wood tone differences only.',
'east-segment-3':'Post and paving geometry connect; paving abruptly changes texture scale and warmth across x32768.',
'east-segment-4':'Paving shapes and joints connect; strong left/right paving texture-density and warm-tone transition persists at x32768.',
'intersection-x29696-y40960':'Four-way hull planks and horizontal strake are continuous.',
'intersection-x30720-y40960':'Four-way planks and curved rib remain connected; modest material tone differences.',
'intersection-x31744-y40960':'Four-way rounded upper rim and underlying boards connect.',
'intersection-x32768-y40960':'Four-tile rim/rib intersection continuous; material facets vary at tile boundary.',
'intersection-x32768-y41984':'Large rib and hull plank lines connect through four-way intersection.',
'intersection-x32768-y43008':'Post stack, beam junction and stone paving connect through four-way intersection.',
'intersection-x32768-y44032':'Paving joints remain continuous through four-way intersection but x32768 surface texture/color split remains.'
}
issues=[
{'id':'G3','classification':'small geometric step at existing repair perimeter','worldBox':[31097,40760,31137,41000],'sourceTile':'r10_c08','detail':'At x31117 bench-rim left adoption boundary, lower edge of large golden rim has a small step and nearby board groove also shifts. Exact native crop retained; local geometry repair needed rather than color alone.','evidence':str(P/'north-segment-3-left-adoption-focus.png'),'evidenceSha256':sha(P/'north-segment-3-left-adoption-focus.png')},
{'id':'C2','classification':'shadow boundary remains open','worldBox':[32330,40700,32410,41100],'sourceTile':'r10_c08','detail':'x32371 rectangular shadow/tone discontinuity visible on deck at north segment4; rim silhouette coherent.','evidence':str(P/'north-segment-4-100pct.png')},
{'id':'M4','classification':'material and tone transition','worldBox':[32690,43008,32840,45056],'sourceTile':'r11_c08/r11_c09','detail':'Stone paving remains geometrically connected but left and right sides have abrupt texture-density and warm-tone difference on same slabs at x32768. Color can reduce warmth mismatch; remaining texture split needs owner review.','evidence':str(P/'east-segment-4-100pct.png')},
{'id':'C3','classification':'minor wood bevel tone/material transition','worldBox':[32690,41000,32840,41340],'sourceTile':'r11_c08/r11_c09','detail':'Front bevel and highlight material differ at shared edge while rim contour remains connected.','evidence':str(P/'east-segment-1-100pct.png')}
]
m=json.loads((P/'manifest.json').read_text());count=0
for item in m['records']:
 n=item['id']
 if n not in notes:continue
 rp=Path(item['report']);r=json.loads(rp.read_text())
 assert r['sourceComplete'] and sha(r['image']['file'])==r['image']['sha256']
 for src in r['sources']:assert sha(src['file'])==src['sha256']
 geom=['G3'] if n=='north-segment-3' else []
 visual=[]
 if n=='north-segment-4':visual=['C2']
 if n in ['east-segment-3','east-segment-4','intersection-x32768-y44032']:visual=['M4']
 if n in ['east-segment-1','intersection-x32768-y40960']:visual+=['C3']
 r['visualReview']={'status':'reviewed_issues_open' if geom or visual else 'reviewed_native_geometry_pass','reviewer':'seam_resume independent','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'structuralBlockers':geom,'colorOnlyRisks':visual,'candidateUsable':not bool(geom),'formalAccepted':False,'observations':[notes[n]]}
 if 'M4' in visual:r['visualReview']['note']='M4 includes texture-density difference and is not certified as color-only; owner material review remains.'
 rp.write_text(json.dumps(r,indent=2)+'\n');item['visualReview']=r['visualReview'];count+=1
m['independentReview']={'reviewedEvidence':count,'segments':8,'crossings':7,'sourceIncompleteCrossings':['intersection-x28672-y40960','intersection-x32768-y45056'],'issues':issues,'status':'external_QA_complete_for_available_sources_issues_open'}
(P/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
(P/'independent-review.json').write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidateSha256':m['candidateSha256'],**m['independentReview'],'formalAccepted':False,'allViewedEvidenceAndSourceHashesVerified':True},indent=2)+'\n')
print(json.dumps({'reviewed':count,'openIssues':[x['id'] for x in issues],'missingCrossings':2}))

