import json,hashlib,datetime,shutil
from pathlib import Path
from PIL import Image
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14/repairs/north-far-east-ledges-20261012-v1")
src=Path(r"C:/Users/luyua/.codex/generated_images/01a12076-19f9-7f00-8135-01e1b5fb7007/exec-b7320770-a75e-469d-9787-de6c4d0b3cae.png")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
dest=d/"repair-native-1254.png";assert not dest.exists()
with Image.open(src) as im:assert im.size==(1254,1254) and im.format=="PNG"
shutil.copy2(src,dest);assert sha(src)==sha(dest)
req=d/"request.json";prep=d/"preparation.json";r=json.loads(req.read_text())
receipt={"schemaVersion":1,"route":"builtin","tool":"image_gen.imagegen","dispatchingAgent":"/root","receivingAgent":"/root/assembly_support","evidence":"Root parent message supplied the successful original builtin output path and explicitly authorized byte-copy, receipt, original-size compose, and replay.","original":info(src),"savedNative":info(dest),"nativePixels":[1254,1254],"savedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"generatedAtUtc":None,"timeMeaning":"savedAtUtc is local preservation time only; actual generation timestamp not claimed","actualModel":None,"actualQuality":None,"request":info(req),"preparation":info(prep),"actualBuiltinParametersReportedByRoot":r["submittedParameters"],"resampled":False,"byteCopyVerified":True}
rp=d/"receipt.json";rp.write_text(json.dumps(receipt,indent=2)+"\n")
gen={**receipt,"id":d.name,"tile":"r14_c14","file":str(dest),"sha256":sha(dest),"width":1254,"height":1254,"mode":Image.open(dest).mode,"format":"PNG","receipt":info(rp),"prompt":info(d/"prompt.txt")}
(d/"repair-native-1254.png.generation.json").write_text(json.dumps(gen,indent=2)+"\n")
print(json.dumps({"source":info(src),"saved":info(dest),"receipt":info(rp)}))
