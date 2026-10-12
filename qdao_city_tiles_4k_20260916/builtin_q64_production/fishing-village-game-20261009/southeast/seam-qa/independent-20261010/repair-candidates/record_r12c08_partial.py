from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/seam-qa/independent-20261010/r12_c08')
notes={
'p11--p12':'Wall courses, rock silhouette and green crevice plants connect at the vertical core cut.',
'p11--p21':'Rock foot, water foam and shoreline continue through horizontal core cut.',
'p12--p13':'Stone coping, wall blocks and foreground boulder contours connect.',
'p12--p22':'Sandy crevice and adjacent boulder contours continue through horizontal cut.',
'p13--p23':'Large boulder silhouette, cracks and faceted surface continue. Mild warm/cool surface-tone difference only.',
'p21--p22':'Foam webs and rock outlines connect at vertical cut; no rectangular interruption.',
'p21--p31':'Waterline around large rock and foam silhouettes connect.',
'p22--p23':'Rock crack network and crevice greenery continue.',
'p22--p32':'Grey rock face edges and nearby water/foam continue.',
'p23--p24':'Sunlit rock outline and dark rear crevice connect.',
'p23--p33':'Rock fissures and crevice greenery continue; mild surface-tone difference reserved for color stage.',
'p31--p32':'Open sea foam ring and blue-water shapes continue across vertical core cut.',
'p32--p33':'Rock foot and white foam shapes remain continuous.',
'cross-r1-c1':'Four-way shore rocks, sand and vegetation connect without duplicated edge or missing wedge.',
'cross-r1-c2':'Four-way large rock and crack topology remain continuous.',
'cross-r2-c1':'Foam network and blue sea join across four-way intersection.',
'cross-r2-c2':'Four-way grey rock crack network remains coherent.'
}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for n,note in notes.items():
 p=P/(n+'.qa.json');r=json.loads(p.read_text());assert r['sourceComplete']
 assert sha(r['image']['file'])==r['image']['sha256']
 for s in r['sources']:assert sha(s['file'])==s['sha256']
 r['visualReview']={'status':'reviewed_native_geometry_pass','reviewer':'seam_resume','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'structuralBlockers':[],'colorOnlyRisks':['Small native exposure/material differences; normal bounded-color stage remains'] if n in ['p13--p23','p23--p33'] else [],'candidateUsable':True,'formalAccepted':False,'observations':[note]}
 p.write_text(json.dumps(r,indent=2)+'\n')
 records.append({'id':n,'evidenceSha256':r['image']['sha256'],'status':r['visualReview']['status']})
m=json.loads((P/'manifest.json').read_text())
for item in m['results']:
 if item['id'] in notes:item['visualReview']=json.loads((P/(item['id']+'.qa.json')).read_text())['visualReview']
(P/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
summary={'tile':'r12_c08','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'partial_native_geometry_pass','reviewedSeams':13,'reviewedCrossings':4,'totalPlannedEvidence':33,'evidence':records,'formalAccepted':False,'internalReady':False,'remaining':'p14 rail repair unselected and final six tile positions incomplete; inspect newly available seams and crossings once owner selects them.'}
(P/'partial-independent-review.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'reviewed':len(records),'status':summary['status']}))

