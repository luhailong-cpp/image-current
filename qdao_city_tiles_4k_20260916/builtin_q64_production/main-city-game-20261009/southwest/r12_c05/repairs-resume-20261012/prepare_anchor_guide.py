from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
T=D/'blue-band-east-join-v03';T.mkdir(exist_ok=True)
src=D/'blue-band-east-join-v01/input.png'
im=Image.open(src).convert('RGB');im.save(T/'input.png')
guide=im.copy();q=ImageDraw.Draw(guide)
q.line([(0,1080),(1253,149)],fill=(255,0,180),width=5)
q.line([(0,744),(1046,0)],fill=(0,170,0),width=5)
for x,y in [(0,1080),(1253,149),(0,744),(1046,0)]: q.ellipse((x-12,y-12,x+12,y+12),outline=(240,0,0),width=3)
guide.save(T/'QA-control-lines-not-final.png')
(T/'guide-derivation.json').write_text(json.dumps({'kind':'QA-only coordinate annotation','sourceFile':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'notFinalArt':True,'annotationNeverCopiedToFinal':True,'blueCreamAnchorLine':[[0,1080],[1253,149]],'grayCreamAnchorLine':[[0,744],[1046,0]]},indent=2),encoding='utf-8')
for name,generated in [('blue-band-east-join-v02','exec-5925fcd5-b8a5-4e90-a168-015c1af92328.png')]:
 p=D/name/'native.png'
 (D/name/'receipt.json').write_text(json.dumps({'tool':'image_gen.imagegen','outcome':'success','generatedSourcePath':r'C:/Users/luyua/.codex/generated_images/01a1301a-c454-7b20-abf6-17f6ef73b906/'+generated,'native':{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size)},'actualModel':None,'actualQuality':None,'savedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2),encoding='utf-8')
 (D/name/'qa-review.json').write_text(json.dumps({'selected':False,'verdict':'anchor_drift_reject','finding':'Text coordinate request failed to preserve blue/cream left y1080; returned near y1013. Preserve original output but do not integrate.','formalAccepted':False,'internalAccepted':False},indent=2),encoding='utf-8')
print(T/'QA-control-lines-not-final.png')
