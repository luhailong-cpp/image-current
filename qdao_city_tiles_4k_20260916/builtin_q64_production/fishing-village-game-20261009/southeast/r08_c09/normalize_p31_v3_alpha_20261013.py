from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=T/'layout-only/p31-v3-whole-post-core-aligned.png';a=np.array(Image.open(src).convert('RGBA'));a[a[:,:,3]==0,:3]=255
out=T/'layout-only/p31-v3-whole-post-clean-alpha.png';Image.fromarray(a).save(out)
rp=T/'p31-v3.request.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));r['referenced_image_paths'][0]=str(out);r['referenceEvidence'][0]['path']=str(out);r['referenceEvidence'][0]['sha256']=sha(out)
r['prompt']+='\nThe white/transparent background holes are ONLY missing flat stone, not additional gold finials. There is precisely ONE gold cap centered atx636, over precisely ONE narrow straight shaftx568..704. Preserve that sole cap/shaft geometry from this clean guide.'
rp.write_text(json.dumps(r,indent=2),encoding='utf-8');(T/'p31-v3.prompt.txt').write_bytes(r['prompt'].encode('utf-8'))
Path(str(out)+'.derivation.json').write_text(json.dumps(dict(file=str(out),sha256=sha(out),classification='input only',operation='White RGB under zero-alpha pixels so obsolete draft object is not visible to alpha-ignoring decoders',derivedFrom=dict(file=str(src),sha256=sha(src))),indent=2),encoding='utf-8')
