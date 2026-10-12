import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
src=Path("C:/Users/luyua/.codex/generated_images/01a13553-091a-72a2-8569-28de53d9fd91/exec-d82d6d16-318c-41e4-8ae8-ec32d2382ceb.png")
out=Path(__file__).with_name("p04_01.recover20261013-v03.joint-guidance.png")
assert not out.exists()
im=Image.open(src).convert("RGB");assert im.size==(1254,1254)
lines=[[(429,235),(902,714)],[(1074,271),(1253,454)],[(1074,271),(501,714)],[(343,405),(570,230)]]
d=ImageDraw.Draw(im)
for line in lines:d.line(line,fill=(236,30,204),width=4)
im.save(out)
rec={"type":"nonfinal_mechanical_joint_guidance","source":str(src),"sourceSha256":hashlib.sha256(src.read_bytes()).hexdigest(),"output":str(out),"outputSha256":hashlib.sha256(out.read_bytes()).hexdigest(),"pixels":[1254,1254],"resize":False,"lineCoordinates":lines,"note":"Magenta lines indicate native-joint continuation only, must be removed/repainted by image model; no code-generated art used as final."}
Path(str(out)+".derivation.json").write_text(json.dumps(rec,indent=2),encoding="utf8")
print(json.dumps(rec))
