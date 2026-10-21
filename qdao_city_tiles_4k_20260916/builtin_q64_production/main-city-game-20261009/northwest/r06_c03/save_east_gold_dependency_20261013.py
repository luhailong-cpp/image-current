from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent;d=T/'repair-batches/east-gold-material-01';a=json.loads((d/'derivation.json').read_text());east=Path(a['actualEastNeighbor']['file']);own=Path(a['source']);b1=[0,2500,160,2680];b2=[3936,2500,4096,2680]
im1=Image.open(east).convert('RGB').crop(b1);im2=Image.open(own).convert('RGB').crop(b2);im1.save(d/'actual-east-native-gold.png');im2.save(d/'own-native-gold.png');joint=Image.new('RGB',(320,180));joint.paste(im2,(0,0));joint.paste(im1,(160,0));joint.save(d/'actual-gold-joint.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert np.array_equal(np.array(joint)[:,160:],np.array(im1))
r=dict(status='needs_coordinator_boundary_review_not_reopened_by_this_worker',reason='Dark vertical gold surface trace remains in fixed actual east neighbor first columns after left-only trial. A one-sided repair cannot remove those protected pixels.',actualEast=dict(file=str(east),sha256=sha(east),nativeCropFile=str(d/'actual-east-native-gold.png'),nativeCropSha256=sha(d/'actual-east-native-gold.png'),cropLTRB=b1,worldBox=[12288,22980,12448,23160]),own=dict(file=str(own),sha256=sha(own),nativeCropFile=str(d/'own-native-gold.png'),nativeCropSha256=sha(d/'own-native-gold.png'),cropLTRB=b2,worldBox=[12128,22980,12288,23160]),joint=dict(file=str(d/'actual-gold-joint.png'),sha256=sha(d/'actual-gold-joint.png'),seamX=160),scale=1,sourceResampled=False,sourcePixelsEqual=True,neighborModified=False,generatedAttemptAdoptedPixels=0)
(d/'east-boundary-dependency-evidence.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
