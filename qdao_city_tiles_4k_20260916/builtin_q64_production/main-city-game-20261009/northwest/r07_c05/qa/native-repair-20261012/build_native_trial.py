"""QA-only trial from exact native cores; never selects sources or edits originals."""
from pathlib import Path
import hashlib, json, sys
from PIL import Image

D = Path(__file__).resolve().parent
T = D.parents[1]
read = lambda path: json.loads(Path(path).read_text(encoding="utf-8-sig"))
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
ref = lambda path: {"file": str(Path(path).resolve()), "sha256": sha(path)}

identifier = sys.argv[1]
logical = identifier[:6]
base_path = T / "candidate/r07_c05-candidate-hard-1672ae5e4698.assembly.json"
base = read(base_path)
source = T / "native" / (identifier + ".png")
generation = read(source.with_suffix(".png.generation.json"))
assert generation["sha256"] == sha(source) and [generation["width"], generation["height"]] == [1254,1254]
destination = D / ("trial-" + identifier)
assert not destination.exists()
destination.mkdir()
canvas = Image.new("RGB", (4096,4096))
sources = []
for entry in base["nativeSources"]:
    item = dict(entry)
    if item["id"] == logical:
        item.update(ref(source))
        item["generationRecord"] = ref(source.with_suffix(".png.generation.json"))
    assert sha(item["file"]) == item["sha256"]
    with Image.open(item["file"]) as opened:
        assert opened.mode == "RGB" and opened.size == (1254,1254)
        core = opened.crop((115,115,1139,1139))
    x, y = (item["column"]-1)*1024, (item["row"]-1)*1024
    canvas.paste(core, (x,y))
    assert canvas.crop((x,y,x+1024,y+1024)).tobytes() == core.tobytes()
    sources.append(item)
candidate = destination / "qa-only-hard-native-core-trial.png"
canvas.save(candidate)
target = next(item for item in sources if item["id"] == logical)
x,y = (target["column"]-1)*1024, (target["row"]-1)*1024
boxes = [("west",[x-160,y,x+160,y+1024],True),
         ("north",[x,y-160,x+1024,y+160],False),
         ("east",[x+864,y,x+1184,y+1024],True),
         ("south",[x,y+864,x+1024,y+1184],False)]
for name,px,py in [("northwest",x,y),("northeast",x+1024,y),
                   ("southwest",x,y+1024),("southeast",x+1024,y+1024)]:
    boxes.append((name,[px-160,py-160,px+160,py+160],False))
qa=[]
for name,box,rotate in boxes:
    assert 0<=box[0]<box[2]<=4096 and 0<=box[1]<box[3]<=4096
    crop=canvas.crop(box)
    if rotate: crop=crop.transpose(Image.Transpose.ROTATE_90)
    path=destination/(name+".png");crop.save(path)
    qa.append({"name":name,**ref(path),"cropLTRB":box,"rotationCCW90":rotate,
               "pixels":list(crop.size),"sourceResampled":False,"nativePixelScale":1,
               "derivedFrom":ref(candidate),"actuallyViewed":False,"verdict":"pending"})
manifest={"schemaVersion":1,"role":"QA-only trial, not selected production candidate",
          "baseManifest":ref(base_path),"replacementNative":ref(source),
          "output":ref(candidate),"nativeSources":sources,"qa":qa,
          "pixelProof":{"status":"passed","checkedPixels":4096*4096,
                        "allPixelsExactNativeCoreAtRecordedWorldCoordinates":True},
          "sourceSelectionModified":False,"formalAccepted":False}
path=destination/"trial-manifest.json"
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"manifest":ref(path),"candidate":manifest["output"],"qaCount":8},indent=2))
