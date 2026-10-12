from pathlib import Path
from PIL import Image
import json,hashlib,datetime
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
p=D/'blue-band-east-join-v03/native.png'
(p.parent/'receipt.json').write_text(json.dumps({'tool':'image_gen.imagegen','outcome':'success','generatedSourcePath':r'C:/Users/luyua/.codex/generated_images/01a1301a-c454-7b20-abf6-17f6ef73b906/exec-af61a887-5da2-4004-8aa8-dfbb5fb150b8.png','native':{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size)},'actualModel':None,'actualQuality':None,'savedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2),encoding='utf-8')
(p.parent/'qa-review.json').write_text(json.dumps({'selected':False,'verdict':'anchor_drift_reject','finding':'QA image coordinate overlay did not preserve y1080 blue/cream left anchor; output near y1013. Original pixels and geometry controls must remain retained.','formalAccepted':False,'internalAccepted':False},indent=2),encoding='utf-8')
T=D/'upper-cream-step-small-v01';T.mkdir(exist_ok=True)
src=D.parent/'repairs-audit-line-20261011/integrated-local-v06/r12_c05.candidate.context.png'
im=Image.open(src);box=(3112,2274,3368,2530);im.crop(box).save(T/'input.png')
(T/'input-derivation.json').write_text(json.dumps({'sourceFile':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'cropContextBox':list(box),'resampled':False},indent=2),encoding='utf-8')
print(T/'input.png')
