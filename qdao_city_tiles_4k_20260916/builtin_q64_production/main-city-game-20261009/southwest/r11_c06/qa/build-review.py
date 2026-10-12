from pathlib import Path
from PIL import Image
import hashlib,json
base=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
out=base/"r11_c06"/"qa"/"full-review"
out.mkdir(parents=True,exist_ok=True)
paths={
"self":base/"r11_c06/pipeline/output/94ddb3ea62a89ee2/r11_c06.candidate.png",
"north":base/"r10_c06/pipeline/output/5c4d9d81c6fcc1ca/r10_c06.candidate.png",
"west":base/"r11_c05/refinement-resume20261010/integrated-v2/r11_c05.repaired-v2.candidate.png"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ims={k:Image.open(v).convert("RGB") for k,v in paths.items()}
assert all(im.size==(4096,4096) for im in ims.values())
checks={"sources":{k:{"file":str(p),"sha256":sha(p),"pixels":list(ims[k].size)} for k,p in paths.items()},"sourceResampling":False,"qaOnly":True,"crops":[]}
west=Image.new("RGB",(512,4096))
west.paste(ims["west"].crop((3840,0,4096,4096)),(0,0))
west.paste(ims["self"].crop((0,0,256,4096)),(256,0))
north=Image.new("RGB",(4096,512))
north.paste(ims["north"].crop((0,3840,4096,4096)),(0,0))
north.paste(ims["self"].crop((0,0,4096,256)),(0,256))
for i in range(4):
    for key,img,box in [("west",west,(0,i*1024,512,(i+1)*1024)),("north",north,(i*1024,0,(i+1)*1024,512))]:
        p=out/f"{key}-segment-{i+1}.png"
        crop=img.crop(box);crop.save(p)
        checks["crops"].append({"file":str(p),"sha256":sha(p),"pixels":list(crop.size),"boundary":key,"boundaryAtPixel":256,"segment":i+1})
boxes={
"step-terminal":(100,1200,750,1650),
"stone-tone-p01p02":(750,850,1300,1300),
"top-right-stone-tone":(2750,0,3500,450),
"p03p04-free-joint-left":(900,2780,1450,3270),
"p03p04-loop":(1700,2800,2350,3300),
"p04-free-joint-left":(800,3440,1330,3950),
"p04-free-joint-center":(1800,3550,2350,4096)}
for name,box in boxes.items():
    p=out/f"{name}.png"; crop=ims["self"].crop(box);crop.save(p)
    checks["crops"].append({"file":str(p),"sha256":sha(p),"pixels":list(crop.size),"coreBox":box,"purpose":"known-issue-inspection"})
checks["allNativeFiles1254"]=all(Image.open(p).size==(1254,1254) for p in (base/"r11_c06/native").glob("*.png"))
checks["nativeCount"]=len(list((base/"r11_c06/native").glob("*.png")))
checks["receiptCount"]=len(list((base/"r11_c06/pipeline/receipts").glob("*.receipt.json")))
checks["rejectedImageCount"]=len(list((base/"r11_c06/pipeline/rejected").glob("*.png")))
(out/"mechanical-review.json").write_text(json.dumps(checks,indent=2),encoding="utf-8")
print(json.dumps({k:checks[k] for k in ["sources","allNativeFiles1254","nativeCount","receiptCount","rejectedImageCount"]},indent=2))

