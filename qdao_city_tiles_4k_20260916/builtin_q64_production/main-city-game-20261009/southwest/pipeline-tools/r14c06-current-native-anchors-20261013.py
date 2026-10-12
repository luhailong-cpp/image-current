from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[1];read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
catalog=read(B/"current-candidates.json");q=B/"r14_c06/pipeline/anchors";q.mkdir(parents=True,exist_ok=True)
for role,tile,box in [("top","r13_c06",[0,4096,4326,4326]),("left","r14_c05",[4096,0,4326,4326])]:
 e=catalog["tiles"][tile]["context"];assert sha(e["file"])==e["sha256"]
 with Image.open(e["file"]) as im:
  assert im.size==(4326,4326);out=im.convert("RGB").crop(box)
 dst=q/f"{role}-{tile}-current-native-v01.png";assert not dst.exists();out.save(dst)
 d={"file":str(dst),"sha256":sha(dst),"nativePixels":list(out.size),"source":e,"sourceTile":tile,"sourceCrop":box,"sourceResampling":False,"operation":"exact native context border crop; no painting/resizing/colour edits","sourceFormalAccepted":False,"geometryStatus":"Stair V3 core repair viewed after integration; other whole-tile open issues remain." if role=="top" else "Provisional neighboring tile, open QA carried explicitly."}
 Path(str(dst)+".derivation.json").write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(dst)

