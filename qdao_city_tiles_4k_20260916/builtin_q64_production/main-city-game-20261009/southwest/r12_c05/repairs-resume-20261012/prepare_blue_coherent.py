from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
src=D/'integrated-local-v10/r12_c05.candidate.context.png';im=Image.open(src).convert('RGB')
# Actual retained native outer anchors, not a seam tolerance based on source-pixel uncertainty.
anchors=[(2560,3240),(4325,1990)];m=(1990-3240)/(4325-2560)
jobs=[('blue-coherent-left-v04',(2560,2160,3814,3414)),('blue-coherent-right-v04',(3072,1716,4326,2970))]
for name,box in jobs:
 T=D/name;T.mkdir(exist_ok=True);crop=im.crop(box);crop.save(T/'input.png');guide=crop.copy();q=ImageDraw.Draw(guide)
 x0,y0,x1,y1=box;p0=(0,3240+m*(x0-2560)-y0);p1=(1253,3240+m*(x0+1253-2560)-y0)
 q.line([p0,p1],fill=(255,0,180),width=5)
 for x,y in [p0,p1]:q.ellipse((x-10,y-10,x+10,y+10),outline=(230,0,0),width=3)
 guide.save(T/'QA-common-line-overlay-not-final.png')
 (T/'input-derivation.json').write_text(json.dumps({'sourceFile':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'cropContextBox':list(box),'resampled':False,'commonBlueCreamLineContextAnchors':anchors,'commonLineSlope':m,'localLineAnchors':[p0,p1],'guideNotFinal':True,'coordinateBasis':'actual current native outer line edges; source approx52px uncertainty is not seam tolerance'},indent=2),encoding='utf-8')
 print(json.dumps({'job':name,'anchors':[p0,p1]}))
R=D/'upper-cream-step-local-v02'
(R/'qa-review-v03.json').write_text(json.dumps({'candidate':'integrated-local-v10','localVerdict':'boundary_geometry_improved_candidate_ready_for_independent_review','maskProposal':'proposal-v03.json','viewed':['applied-ROI-native-v03-QA.png','../integrated-local-v10/H2-4-native-QA.png','../integrated-local-v10/V3-3-native-QA.png'],'finding':'Missing edge and wide gray stair-step segment replaced by one continuous thin joint. Left cap has minor line-weight variation. Blue/cream notch and blue field tone remain open. All external and full-tile acceptance withheld.','formalAccepted':False,'internalAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
