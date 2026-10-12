from pathlib import Path
from PIL import Image
import json,hashlib,os
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=Image.new('RGB',(4096,4096));sel=rd(R/'selected-native-r08_c11.json')['selected'].copy();sel['r08_c11_p33']='r08_c11_p33_v04.png'
for pid,fn in sel.items():
 sr,sc=int(pid[-2]),int(pid[-1]);base.paste(Image.open(R/'native'/fn).convert('RGB').crop((115,115,1139,1139)),((sc-1)*1024,(sr-1)*1024))
for z in rd(R/'selected-overlays-r08_c11.json')['overlays']:base.paste(Image.open(z['file']).convert('RGB').crop(z['sourceCrop']),z['destinationBox'][:2])
trial=base.copy();src=R/'native/r08_c11_wall_joint_v01.png';trial.paste(Image.open(src).convert('RGB').crop((115,115,1139,1139)),(2560,2048));trial.save(Q/'wall-joint-full-trial.png')
boxes={'left':[2304,2048,2816,3072],'right':[3328,2048,3840,3072],'bottom':[2560,2816,3584,3328],'top':[2560,1792,3584,2304],'old-joint':[2816,2048,3328,3072]}
for key,box in boxes.items():trial.crop(box).save(Q/f'wall-joint-{key}.png')
(Q/'wall-joint-trial.json').write_text(json.dumps({'trial':str(Q/'wall-joint-full-trial.png'),'sha256':sh(Q/'wall-joint-full-trial.png'),'source':str(src),'sourceSha256':sh(src),'sourceCrop':[115,115,1139,1139],'destinationBox':[2560,2048,3584,3072],'baseP33':'r08_c11_p33_v04.png','boxes':boxes,'status':'pending_direct_review','formalAccepted':False},indent=2)+'\n')
print(json.dumps(boxes))
