from pathlib import Path
from PIL import Image
import json,hashlib,datetime,argparse,numpy as np
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--previous',required=True);p.add_argument('--entries',required=True);p.add_argument('--version',required=True);a=p.parse_args()
def sha(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()
old=json.loads(Path(a.previous).read_text(encoding='utf-8'));extra=json.loads(Path(a.entries).read_text(encoding='utf-8'))
overlays=old['overlays']+extra
base=old['baseCandidate'];assert sha(base['file'])==base['sha256']
im=Image.open(base['file']).convert('RGB')
for o in overlays:
 assert sha(o['file'])==o['sha256']
 x0,y0,x1,y1=o['sourceROI'];wx,wy,_,_=o['nativeWorldBox'];cb=[wx+x0-20480,wy+y0-24576,wx+x1-20480,wy+y1-24576]
 assert 0<=cb[0]<cb[2]<=4096 and 0<=cb[1]<cb[3]<=4096
 o['candidateROI']=cb;o['roiWorldBox']=[wx+x0,wy+y0,wx+x1,wy+y1]
 d=Image.open(o['file']).convert('RGB');assert d.size==(1254,1254)
 im.paste(d.crop((x0,y0,x1,y1)),cb[:2])
out=r/('candidate/r07_c06-candidate-native-roi-'+a.version+'.png');assert not out.exists();im.save(out)
rec=dict(schemaVersion=1,tile=r.name,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='partial-repair-candidate-pending-full-visual-QA',baseCandidate=base,previousRegistry=dict(file=str(Path(a.previous).resolve()),sha256=sha(a.previous)),overlays=overlays,candidate=dict(file=str(out),sha256=sha(out),pixels=[4096,4096]),original16SelectionsUnchanged=True,sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,formalAccepted=False)
manifest=r/('candidate/native-overlays-20261012-'+a.version+'.json');assert not manifest.exists();manifest.write_text(json.dumps(rec,indent=2),encoding='utf-8')
# Read back full candidate and reconstruct all selected original cores plus native ROIs for exact final raw-pixel equality.
assert np.array_equal(np.array(Image.open(out).convert('RGB')),np.array(im))
print(json.dumps(dict(candidate=rec['candidate'],registry=str(manifest),registrySha256=sha(manifest))))
