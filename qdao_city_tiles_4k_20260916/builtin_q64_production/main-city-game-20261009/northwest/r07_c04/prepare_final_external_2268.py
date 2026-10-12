from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).parent
name='r07_c04-candidate-native-bridges-2268d482e68c2928'
m=json.loads((P/'candidate'/name/'assembly.json').read_text())
q=P/'qa'/name
im=Image.open(m['output']['file']).convert('RGB')
north=P.parent/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c04-joint-4096.png'
n=Image.open(north).convert('RGB')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
row=Image.new('RGB',(4096,320));row.paste(n.crop((0,3936,4096,4096)),(0,0));row.paste(im.crop((0,0,4096,160)),(0,160))
out=[]
for c in range(4):
 f=q/f'external-north-segment{c+1:02d}.png';row.crop((c*1024,0,(c+1)*1024,320)).save(f)
 out.append(dict(name=f.stem,file=str(f),sha256=sha(f),nativePixelScale=1,sourceResampled=False,north=dict(file=str(north),sha256=sha(north),cropLTRB=[c*1024,3936,(c+1)*1024,4096]),south=dict(**m['output'],cropLTRB=[c*1024,0,(c+1)*1024,160])))
(q/'external-north-crops.json').write_text(json.dumps(out,indent=2)+'\n')
base=Image.open(P/'candidate/r07_c04-candidate-minimum-error-b38cb951695e.png').convert('RGB')
assert im.crop((3866,0,4096,4096)).tobytes()==base.crop((3866,0,4096,4096)).tobytes()
proof=dict(status='passed',candidate=m['output'],base=dict(file=str(P/'candidate/r07_c04-candidate-minimum-error-b38cb951695e.png'),sha256=sha(P/'candidate/r07_c04-candidate-minimum-error-b38cb951695e.png')),comparedTileBox=[3866,0,4096,4096],checkedPixels=230*4096,exactNativeEastStripUnchanged=True)
(q/'east-strip-unchanged.json').write_text(json.dumps(proof,indent=2)+'\n')
oldp=P/'qa/r07_c04-candidate-native-bridges-5032b69bc48f9356/review-internal.json'
old={e['name']:e for e in json.loads(oldp.read_text())['entries']}
changed=[];inherit=[]
for e in m['qa']+m['bridgeBoundaryQa']:
 name=Path(e['file']).stem;o=old.get(name)
 (inherit if o and o['sha256']==e['sha256'] and o['verdict']!='blocking' else changed).append(name)
print(json.dumps(dict(changed=changed,inherited=len(inherit),eastStripProof=proof),indent=2))

