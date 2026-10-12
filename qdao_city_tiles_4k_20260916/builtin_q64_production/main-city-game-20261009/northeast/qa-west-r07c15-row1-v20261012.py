from pathlib import Path
from PIL import Image
import hashlib,json
Z=Path(__file__).resolve().parent
W=Z/'r07_c14/candidates/r07_c14.candidate.png';N=Z/'r07_c15/native/p11-v20261012.png'
O=Z/'r07_c15/qa/first-row-v20261012/west-shared-core-p11.png'
assert not O.exists()
im=Image.new('RGB',(512,1024));im.paste(Image.open(W).convert('RGB').crop((3840,0,4096,1024)),(0,0));im.paste(Image.open(N).convert('RGB').crop((115,115,371,1139)),(256,0));im.save(O)
Path(str(O)+'.generation.json').write_text(json.dumps({'file':str(O),'sha256':hashlib.sha256(O.read_bytes()).hexdigest(),'assetRole':'QA shared edge integer crop; not game art','derivedFrom':[{'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in [W,N]],'operation':'native-scale integer crops/paste without resizing'},indent=2),encoding='utf-8')
