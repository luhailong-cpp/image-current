from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
T=D/'upper-cream-step-local-v02';T.mkdir(exist_ok=True)
src=D/'blue-band-east-join-v01/input.png'
im=Image.open(src);im.save(T/'input.png')
guide=im.copy();q=ImageDraw.Draw(guide);q.rectangle((552,114,808,370),outline=(255,0,128),width=4);q.ellipse((650,214,710,274),outline=(255,0,128),width=4)
guide.save(T/'QA-ROI-overlay-not-final.png')
(T/'input-derivation.json').write_text(json.dumps({'sourceFile':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceCropContextBox':[2560,2160,3814,3414],'roiHint':[552,114,808,370],'resampled':False,'overlayIsQANotFinal':True},indent=2),encoding='utf-8')
(D/'upper-cream-step-small-v01/qa-review.json').write_text(json.dumps({'selected':False,'verdict':'native_dimensions_do_not_match_target','targetDimensions':[256,256],'actualDimensions':list(Image.open(D/'upper-cream-step-small-v01/native.png').size),'sourceResampling':False,'reason':'Builtin enlarged local composition to1254 square; may not downsample into native256 ROI.'},indent=2),encoding='utf-8')
print(T)
