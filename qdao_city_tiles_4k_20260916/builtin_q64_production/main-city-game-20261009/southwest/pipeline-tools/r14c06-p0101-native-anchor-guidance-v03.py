from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=Path(r"C:\Users\luyua\.codex\generated_images\01a12076-0b9d-76b2-949d-c4cf520a83be\exec-6e82f1a3-1e06-4cea-9a4b-eb3b9701b83f.png");anchor=B/"r14_c06/pipeline/guides/p01_01.recover-20261013b-v01.continuity-seed.png"
with Image.open(src) as im:target=im.convert("RGB");assert target.size==(1254,1254)
with Image.open(anchor) as im:
 original=im.convert("RGB");target.paste(original.crop((0,230,230,1254)),(0,230));target.paste(original.crop((0,0,1254,230)),(0,0))
out=B/"r14_c06/pipeline/guides/p01_01.recover-20261013b-v03.mechanical-native-anchor-guide.png";assert not out.exists();target.save(out)
Path(str(out)+".derivation.json").write_text(json.dumps({"file":str(out),"sha256":sha(out),"source":str(src),"sourceSha256":sha(src),"anchor":str(anchor),"anchorSha256":sha(anchor),"operation":"Exact native top230 and left230 pasted onto unselected native candidate for generation guidance only; no resampling or final-art claim","sourceResampling":False,"gameArt":False},indent=2)+"\n",encoding="utf-8")
print(out)

