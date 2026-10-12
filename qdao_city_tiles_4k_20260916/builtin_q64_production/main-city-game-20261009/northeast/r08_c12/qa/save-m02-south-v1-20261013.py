from pathlib import Path
from PIL import Image
import json,hashlib,shutil
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12');q=p/'qa/repair-resume-20261013';src=Path(r'C:/Users/luyua/.codex/generated_images/01a1345a-d695-7ea3-9410-7bee96f26ed0/exec-9c120c6b-5c4b-41f7-8b14-e7e3d7fcff77.png');dst=p/'native/repairs/m02-extra-band-south-v1.png';assert not dst.exists();shutil.copy2(src,dst)
im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
base=p/'candidates/r08_c12.m02-north-v1.png';can=Image.open(base).convert('RGB');can.paste(im,(1250,1000));out=p/'candidates/r08_c12.m02-south-v1.png';assert not out.exists();can.save(out)
record={'sourceOutputPath':str(src),'repairNative':str(dst),'repairSha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'nativeSize':[1254,1254],'actualModel':None,'actualQuality':None,'baseCandidate':str(base),'baseSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'targetWorldBoxInTile':[1250,1000,2504,2254],'operation':'exact integer AI-native crop paste; no resizing, feathering or drawn pixels','output':str(out),'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'M02 erroneous duplicated route removed; outer repair boundaries awaiting review'}
(q/'m02-extra-band-south-v1-composition.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
target=q/'m01-orphan-trim-target-v1.png';assert not target.exists();can.crop((0,1300,1254,2554)).save(target)
print(json.dumps(record))
