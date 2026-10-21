from pathlib import Path
import json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north')
versions={'p11':'v001','p12':'v001','p13':'v001','p14':'v001','p21':'v002','p22':'v001','p23':'v003','p24':'v002','p31':'v001','p32':'v001','p33':'v001','p34':'v001','p41':'v001','p42':'v001','p43':'v001','p44':'v001'}
s={'schemaVersion':1,'selectionVersion':'right-r04c14-candidate-sixteen-v001','tile':'r04_c14','status':'candidate_best_available_mechanical_complete_not_visually_accepted','fullVisualAcceptance':False,'formalAcceptedCount':0,'patches':{},'knownBlocking':['p21 west eave phase unresolved after two repairs; v002 best','p22 west transition to p21 unresolved','p23 south wall diagonal phase unresolved after two repairs; v003 best','p24 south pillar width shifted','p42 south rail edge about50px shifted','p43 south post right edge about60px shifted','p44 south masonry phase about100px shifted after two repairs; v001 best'],'notes':['All16 real1254px native outputs; core[115,115,1139,1139). No resizing/blending. Candidate for concentrated QA, NOT new reference acceptance.']}
for p,v in versions.items():
 r=B/f'versions/right-r04c14-{p}-native-{v}/r04_c14/native/{p}.png.generation.json'
 j=json.loads(r.read_text(encoding='utf-8'))
 s['patches'][p]={'record':str(r),'sha256':j['sha256'],'recordSha256':hashlib.sha256(r.read_bytes()).hexdigest()}
o=B/'selections/right-r04c14-candidate-sixteen-v001.json'
with o.open('x',encoding='utf-8') as f:json.dump(s,f,ensure_ascii=False,indent=2)
print(o)

