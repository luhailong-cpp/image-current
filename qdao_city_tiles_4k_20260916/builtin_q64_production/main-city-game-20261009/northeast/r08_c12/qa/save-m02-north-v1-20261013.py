from pathlib import Path
from PIL import Image
import json,hashlib,shutil
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12');src=Path(r'C:/Users/luyua/.codex/generated_images/01a1345a-d695-7ea3-9410-7bee96f26ed0/exec-9167aa2c-e796-4863-8122-7d35db544ffb.png');q=p/'qa/repair-resume-20261013';n=p/'native/repairs';n.mkdir(exist_ok=True)
dst=n/'m02-extra-band-north-v1.png';assert not dst.exists();shutil.copy2(src,dst)
im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
baseline=p/'qa/core-baseline/f7529838f3e52b886085/r08_c12-core-baseline.candidate.png';can=Image.open(baseline).convert('RGB')
# Copy only the AI repaired corridor, never paint or interpolate.
boxes=[[250,0,660,1100],[250,1100,930,1254]]
for b in boxes:can.paste(im.crop(b),(1250+b[0],b[1]))
out=p/'candidates/r08_c12.m02-north-v1.png';assert not out.exists();can.save(out)
record={'sourceOutputPath':str(src),'repairNative':str(dst),'repairSha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'nativeSize':list(im.size),'actualModel':None,'actualQuality':None,'baseCandidate':str(baseline),'baseSha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'targetWorldBoxInTile':[1250,0,2504,1254],'repairCropBoxes':boxes,'operation':'exact integer AI-native ROI paste; no resizing, feathering or drawn pixels','output':str(out),'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'partial M02 correction awaiting south continuation and boundary review'}
(q/'m02-extra-band-north-v1-composition.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
target=q/'m02-extra-band-south-target-v1.png';assert not target.exists();can.crop((1250,1000,2504,2254)).save(target)
print(json.dumps(record))
