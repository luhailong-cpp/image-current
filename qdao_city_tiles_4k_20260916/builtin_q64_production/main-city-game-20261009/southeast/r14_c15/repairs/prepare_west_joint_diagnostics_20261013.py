from pathlib import Path
from PIL import Image
import json,hashlib
q=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15");t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14")
d=q/"repairs/west-stone-joints-20261013-v1";assert not d.exists();d.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
n=json.loads((t/"candidate/latest-assembly.json").read_text());c=json.loads((q/"candidate/latest-assembly.json").read_text())
assert sha(n["candidate"]["path"])=="7288055c3509f4603e3006cd23914d5c4acae499180bd79869aafcf40cde8af3"
assert sha(c["candidate"]["path"])=="5ce10046c09c4e5ea101d0638cd62de9327869d487762c1804bca74ce971c627"
wi=Image.open(n["candidate"]["path"]).convert("RGB");ci=Image.open(c["candidate"]["path"]).convert("RGB")
index={"west":n["candidate"],"child":c["candidate"],"childContext":c["context"],"childManifest":c["manifest"],"windows":[]}
for code,y in [("W01",480),("W02",1680),("W03",2842)]:
 p=d/code;p.mkdir();im=Image.new("RGB",(1254,1254));im.paste(wi.crop((3456,y,4096,y+1254)),(0,0));im.paste(ci.crop((0,y,614,y+1254)),(640,0));f=p/"reference-core-join-native-1254.png";im.save(f)
 index["windows"].append({"id":code,"originY":y,"path":str(f),"sha256":sha(f),"westernCoreBox":[3456,y,4096,y+1254],"childCoreBox":[0,y,614,y+1254]})
(d/"diagnostic-index.json").write_text(json.dumps(index,indent=2)+"\n")
print(str(d))
