from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,argparse
z=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument("--target",required=True);ap.add_argument("--repair",required=True);ap.add_argument("--components",nargs="+",required=True);ap.add_argument("--output-dir",required=True);a=ap.parse_args()
out=(z/a.output_dir).resolve();assert out.is_relative_to(z) and not out.exists();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rec=lambda p:{"path":p.as_posix(),"sha256":sha(p)}
t=(z/a.target).resolve();r=(z/a.repair).resolve();ps=[(z/p).resolve() for p in a.components]
m=np.zeros((1254,1254),bool)
for p in ps:
 arr=np.array(Image.open(p));assert arr.shape==m.shape and set(np.unique(arr)).issubset({0,255});m|=arr==255
old=np.array(Image.open(t).convert("RGB"));new=np.array(Image.open(r).convert("RGB"));assert old.shape==new.shape==(1254,1254,3)
c=old.copy();c[m]=new[m]
mp=out/"source_selection_mask.png";cp=out/"combined_native_crop.png"
Image.fromarray(m.astype(np.uint8)*255).save(mp);Image.fromarray(c).save(cp)
d={"operation":"Boolean union of same-coordinate binary hard source masks","components":[rec(p) for p in ps],"target":rec(t),"repair":rec(r),"mask":rec(mp),"combinedCrop":rec(cp),"repairPixelCount":int(m.sum()),"resizing":False,"registration":False,"feathering":False,"colorCorrection":False,"pixelSynthesis":False}
(out/"mask_selection.json").write_text(json.dumps(d,indent=2)+"\n",encoding="utf8");print(json.dumps(d))

