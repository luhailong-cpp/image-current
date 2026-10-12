from pathlib import Path
import sys,json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
from assemble_tile import save_qa,save_json
p=Z/"tiles/r04_c04_candidate-v2_4096.png";im=Image.open(p)
out=Z/"qa/r04_c04_v2_native_review";out.mkdir(exist_ok=False)
entries=[]
for name,box in [("foliage_top",[2600,0,3854,400]),("foliage_bottom",[2600,1200,3854,1600]),("foliage_left",[2470,160,2870,1414]),("foliage_right",[3430,160,3830,1414])]:
 f=out/(name+"_100pct.png");im.crop(box).save(f);entries.append({"path":str(f),"cropBox":box,"dimensions":list(Image.open(f).size),"sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
qa=save_qa(out/"seams",im)
save_json(out/"seams"/"qa_index.json",qa)
save_json(out/"boundary_index.json",{"source":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"operation":"exact native coordinate QA crops only; no resize","boundaries":entries})
print(json.dumps({"out":str(out)}))

