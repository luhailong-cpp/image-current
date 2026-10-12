from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rp=T/'native/p11-v1.png.generation.json';rec=json.loads(rp.read_text(encoding='utf-8-sig'));ref=rec['references'][0]
layout=T/'layout-only/p11-layout-only.png';west=T.parent/'r10_c09/native/p14-v3.png'
im=Image.open(layout).convert('RGB');im.paste(Image.open(west).convert('RGB').crop((1024,0,1254,1254)),(0,0))
snap=T/'input-snapshots'/f"{ref['sha256']}.png";snap.parent.mkdir(exist_ok=True);im.save(snap)
assert sha(snap)==ref['sha256']
d={'file':str(snap),'sha256':sha(snap),'originalSubmittedPath':ref['path'],'operation':'exact mechanical reconstruction of earlier guide; SHA256 exactly matches generation-time recorded reference','layoutSource':{'path':str(layout),'sha256':sha(layout)},'westNativeSource':{'path':str(west),'sha256':sha(west),'crop':[1024,0,1254,1254],'pasteAt':[0,0]},'layoutOnly':True,'notFinalArtwork':True,'dimensions':[1254,1254]}
snap.with_suffix('.png.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
ref['verifiedSnapshotPath']=str(snap);ref['snapshotEvidence']=str(snap.with_suffix('.png.derivation.json'))
rp.write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'restoredReference':str(snap),'sha256ExactlyMatches':True}))

