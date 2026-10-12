"""Prepare explicit r03_c04 local-native edit input records, never mutate source records."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parents[2]
a=argparse.ArgumentParser()
a.add_argument("--source",required=True)
a.add_argument("--stem",required=True)
v=a.parse_args()
assert v.source.startswith("r03_c04_") and v.stem.startswith("r03_c04_")
assert v.source[:14]==v.stem[:14] and v.source!=v.stem
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((Z/"guides"/f"{v.source}.input.json").read_text(encoding="utf-8-sig"))
source=Z/"native"/f"{v.source}.png"
gen=Path(str(source)+".generation.json")
assert Image.open(source).size==(1254,1254)
targets=[Z/"guides"/f"{v.stem}.{suffix}.json" for suffix in ("input","references")]
assert all(not p.exists() for p in targets)
old["stem"]=v.stem
old["versionStem"]=v.stem
old["attempt"]=v.stem.rsplit("_",1)[1]
old["operation"]="builtin local native edit; same coordinates and dimensions"
old["inputs"][0]={"path":source.as_posix(),"sha256":sha(source),"nativeSize":[1254,1254],"role":"only native edit target; preserve macro geometry and all areas outside named defect","generationRecord":{"path":gen.as_posix(),"sha256":sha(gen)}}
old["inputs"][1:4]=json.loads((Z/"references.json").read_text(encoding="utf-8-sig"))
for ref in old["inputs"]:
    assert sha(Path(ref["path"]))==ref["sha256"], "Current reference hash mismatch"
old["imageGenReferencedImagePaths"]=[x["path"] for x in old["inputs"]]
old["inputCount"]=len(old["inputs"])
old["originalLayoutGuideDerivation"]=old.pop("guideDerivation",None)
for p,obj in zip(targets,(old,old["inputs"])):
    with p.open("x",encoding="utf-8") as f:json.dump(obj,f,ensure_ascii=False,indent=2)
print(json.dumps({"stem":v.stem,"source":v.source,"inputs":old["imageGenReferencedImagePaths"]}))

