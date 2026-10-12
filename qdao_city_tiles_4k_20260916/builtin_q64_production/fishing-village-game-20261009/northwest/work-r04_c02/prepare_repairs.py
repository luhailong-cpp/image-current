import json,os
from pathlib import Path
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");W=B/'work-r04_c02';A=W/'base-v1/extended.png';im=Image.open(A)
boxes={'green-hem-whole-v01':[4450,13200,5704,14454],'rope-joint-whole-v01':[5550,15245,6804,16499]}
for k,box in boxes.items():
 p=W/'guides'/(k+'.native-target.png');im.crop((box[0]-3981,box[1]-12173,box[2]-3981,box[3]-12173)).save(p)
 p.with_suffix('.derivation.json').write_text(json.dumps({'source':str(A),'globalBox':box,'method':'exact native crop only; no resample'},indent=2),encoding='utf-8')
qa={'internalAccepted':False,'formalAccepted':False,'status':'complete-candidate-pending-visible-repairs','knownIssues':['green-cloth lower hem hole/step','east lower suspension rope severed','red cloth roll/phase join pending','paving edge thin slab/highlight stub','sand texture junction transitions need full review'],'reviewed':['overview.preview-only.jpg','qa/junction-1-1.png','qa/junction-1-3.png','qa/junction-2-1.png','qa/junction-3-2.png'],'sourceProof':{'extendedPixels':4326*4326,'mismatches':0}}
(W/'base-v1/qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
p=B/'current-artifacts.json';d=json.loads(p.read_text(encoding='utf-8-sig'));d['r04_c02']={'candidate':'work-r04_c02/base-v1/r04_c02.candidate.png','assembly':'work-r04_c02/base-v1/r04_c02.candidate.assembly.json','qa':'work-r04_c02/base-v1/qa.json','status':'complete-candidate-pending-cloth-rope-and-seam-repair','formalAccepted':False};tmp=p.with_suffix('.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
