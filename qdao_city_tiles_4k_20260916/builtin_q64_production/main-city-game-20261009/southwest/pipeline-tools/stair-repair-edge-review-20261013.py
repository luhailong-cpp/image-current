from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parents[1];q=B/"r13_c06/repairs-resume-20261012/stair-V3-full-native-v01/qa-native";q.mkdir(exist_ok=False)
ap=q.parent/"integrated/assembly.json";a=json.loads(ap.read_text(encoding="utf-8-sig"));im=Image.open(a["contextOutput"]["file"]).convert("RGB")
l,t,r,b=2565,2957,3819,4211
panel=Image.new("RGB",(1254,560),"white");d=ImageDraw.Draw(panel)
panel.paste(im.crop((l,t-128,r,t+128)),(0,24));d.text((3,3),"repair TOP",fill="black")
panel.paste(im.crop((l,b-128,r,b+115)),(0,304));d.text((3,283),"repair BOTTOM plus untouched native halo",fill="black");panel.save(q/"horizontal-boundaries.png")
panel=Image.new("RGB",(560,1278),"white");d=ImageDraw.Draw(panel)
panel.paste(im.crop((l-128,t,l+128,b)),(0,24));d.text((3,3),"repair LEFT",fill="black")
panel.paste(im.crop((r-128,t,r+128,b)),(280,24));d.text((283,3),"repair RIGHT",fill="black");panel.save(q/"vertical-boundaries.png")
im.crop((l,t,r,b)).save(q/"actual-integrated-native-crop.png")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(q/"manifest.json").write_text(json.dumps({"assembly":str(ap),"assemblySha256":sha(ap),"candidate":a["output"],"context":a["contextOutput"],"panelsNativeResampled":False,"formalAccepted":False,"files":[{"file":str(p),"sha256":sha(p)} for p in q.glob("*.png")]},indent=2)+"\n",encoding="utf-8")
print(q)

