import json,hashlib,argparse
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--version',required=True,type=int);a=ap.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=z/f'tiles/r07_c04_candidate-v{a.version}_4096.png';base=z/'tiles/r07_c04_candidate-v1_4096.png'
new=Image.open(p).convert('RGB');old=Image.open(base).convert('RGB')
q=z/f'qa/r07_c04_v{a.version}_internal_delta_review';q.mkdir(exist_ok=False)
oldip=z/'qa/assembly_r07_c04_candidate-v1_4096/qa_index.json';oldindex=json.loads(oldip.read_text())
items=[];changed=[]
for item in oldindex['seamAndJunctionCrops']:
 box=item['tileCropBoxHalfOpen'];im=new.crop(box);same=np.array_equal(np.array(im),np.array(old.crop(box)))
 fp=Path(item['path'])
 assert sha(fp)==item['sha256']
 if not same:
  fp=q/Path(item['path']).name;im.save(fp);changed.append(fp.name)
 items.append({**item,'path':fp.as_posix(),'sha256':sha(fp),'reusedUnchangedV1Crop':same,'currentTileCropExactPixels':True,'reviewStatus':'reuse_prior_exact_pixel_review' if same else 'pending_changed_crop_review','prior':dict(path=item['path'],sha256=item['sha256'])})
pr=q/'preview_1024px_NOT_FOR_GAME.png';new.resize((1024,1024),Image.Resampling.LANCZOS).save(pr)
d={'tileId':'r07_c04','candidate':dict(path=p.as_posix(),sha256=sha(p)),'baseline':dict(path=base.as_posix(),sha256=sha(base)),'priorIndex':dict(path=oldip.as_posix(),sha256=sha(oldip)),'seamAndJunctionCrops':items,'changedCropCount':len(changed),'unchangedReusedCount':33-len(changed),'changedNames':changed,'preview':dict(path=pr.as_posix(),sha256=sha(pr),role='downsampled inspection only not game art'),'internalClosurePassed':False,'formalAccepted':False}
with (q/'qa_index.json').open('x',encoding='utf8') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'qaIndex':str(q/'qa_index.json'),'sha256':sha(q/'qa_index.json'),'changed':changed,'unchangedReused':33-len(changed)}))

