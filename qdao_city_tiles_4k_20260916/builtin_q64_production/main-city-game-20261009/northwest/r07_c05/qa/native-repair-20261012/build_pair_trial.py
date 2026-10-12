"""QA-only exact native core pair trial. No source selection or production edits."""
from pathlib import Path
import hashlib, json, sys
from PIL import Image

D = Path(__file__).resolve().parent
T = D.parents[1]
read = lambda path: json.loads(Path(path).read_text(encoding="utf-8-sig"))
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
ref = lambda path: {"file": str(Path(path).resolve()), "sha256": sha(path)}
identifiers = sys.argv[1:]
assert len(identifiers) == 2 and {v[:6] for v in identifiers} == {"s02_03", "s03_03"}
replacements = {identifier[:6]: T / "native" / (identifier + ".png") for identifier in identifiers}
base_path = T / "candidate/r07_c05-candidate-hard-1672ae5e4698.assembly.json"
base = read(base_path)
destination = D / ("trial-pair-" + "-".join(identifiers))
assert not destination.exists()
destination.mkdir()
canvas = Image.new("RGB", (4096,4096))
sources = []
for entry in base["nativeSources"]:
    item = dict(entry)
    if item["id"] in replacements:
        path = replacements[item["id"]]
        generation = read(path.with_suffix(".png.generation.json"))
        assert generation["sha256"] == sha(path) and [generation["width"],generation["height"]] == [1254,1254]
        item.update(ref(path))
        item["generationRecord"] = ref(path.with_suffix(".png.generation.json"))
    assert sha(item["file"]) == item["sha256"]
    with Image.open(item["file"]) as opened:
        assert opened.mode == "RGB" and opened.size == (1254,1254)
        core = opened.crop((115,115,1139,1139))
    x,y = (item["column"]-1)*1024, (item["row"]-1)*1024
    canvas.paste(core,(x,y))
    assert canvas.crop((x,y,x+1024,y+1024)).tobytes() == core.tobytes()
    sources.append(item)
candidate = destination / "qa-only-hard-native-core-pair.png"
canvas.save(candidate)
qa = []
for logical in replacements:
    target = next(item for item in sources if item["id"] == logical)
    x,y = (target["column"]-1)*1024,(target["row"]-1)*1024
    boxes = [("west",[x-160,y,x+160,y+1024],True),
             ("north",[x,y-160,x+1024,y+160],False),
             ("east",[x+864,y,x+1184,y+1024],True),
             ("south",[x,y+864,x+1024,y+1184],False)]
    for name,px,py in [("northwest",x,y),("northeast",x+1024,y),("southwest",x,y+1024),("southeast",x+1024,y+1024)]:
        boxes.append((name,[px-160,py-160,px+160,py+160],False))
    for name,box,rotate in boxes:
        assert 0<=box[0]<box[2]<=4096 and 0<=box[1]<box[3]<=4096
        crop=canvas.crop(box)
        if rotate: crop=crop.transpose(Image.Transpose.ROTATE_90)
        path=destination/(logical+"-"+name+".png")
        crop.save(path)
        qa.append({"name":logical+"-"+name,**ref(path),"cropLTRB":box,"rotationCCW90":rotate,
                   "pixels":list(crop.size),"sourceResampled":False,"nativePixelScale":1,
                   "derivedFrom":ref(candidate),"actuallyViewed":False,"verdict":"pending"})
manifest={"schemaVersion":1,"role":"QA-only exact native pair trial, not selected production candidate",
          "baseManifest":ref(base_path),"replacementNatives":{key:ref(value) for key,value in replacements.items()},
          "output":ref(candidate),"nativeSources":sources,"qa":qa,
          "pixelProof":{"status":"passed","checkedPixels":4096*4096,
                        "allPixelsExactNativeCoreAtRecordedWorldCoordinates":True},
          "sourceSelectionModified":False,"formalAccepted":False}
path=destination/"trial-manifest.json"
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"manifest":ref(path),"candidate":manifest["output"],"qaCount":len(qa)},indent=2))
