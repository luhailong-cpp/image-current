from pathlib import Path
import json,hashlib,argparse
Z=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
for name in ("r05c03-image","r05c03-record","r05c04-image","r05c04-record","output"):ap.add_argument("--"+name,required=True)
a=ap.parse_args()
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
prior=Z/"qa/connected-closure-current-v5.manifest.json";data=json.loads(prior.read_text())
top=[next(t for t in data["tiles"] if t["tileId"]==tid) for tid in ("r04_c03","r04_c04")]
bottom=[]
for tid,p,r in (("r05_c03",a.r05c03_image,a.r05c03_record),("r05_c04",a.r05c04_image,a.r05c04_record)):
 bottom.append(dict(tileId=tid,image=info(Path(p)),record=info(Path(r))))
manifest=dict(schemaVersion=1,tileMatrix=[top,bottom],preservedPriorSharedBoundary=dict(manifest=info(prior),closure=info(Z/"qa/connected-closure-final-v1/closure.json"),wrapper=info(Z/"qa/build_next_connected_preserving_prior.py"),policy="Top-row vertical join fixed to native core boundary115; other two joins use normal DP."))
with Path(a.output).open("x",encoding="utf8") as f:json.dump(manifest,f,indent=2)
print(a.output)

