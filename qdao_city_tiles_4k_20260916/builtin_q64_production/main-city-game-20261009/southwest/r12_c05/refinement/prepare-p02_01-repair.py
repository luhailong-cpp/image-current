from pathlib import Path
import json,hashlib,copy
B=Path(__file__).resolve().parents[1]
D=Path(__file__).resolve().parent
D.mkdir(exist_ok=True)
original=json.loads((B/"pipeline/prompts/p02_01.resumed-full64-v02.request.json").read_text())
prompt="""Use case: precise-object-edit. Edit ONLY image1, the existing close-up of pale gray stone ground. Keep the exact1254x1254 framing, top diagonal grout, all upper pavement geometry, and daylight. Correct ONLY the lower paving-course proportions: the first horizontal groove must remain at y863. The second horizontal groove currently near y960 must move downward to y1150. There must be exactly TWO horizontal grooves in the whole crop, at y863 and y1150, creating one broad middle stone band287 pixels high. Remove the old y960 groove completely and restore uninterrupted matching native stone there. The lower vertical joints start ONLY at y1150 and continue to the bottom, at x275 and x925. No vertical joints in the broad band from y863 to1150. Keep every pixel above y840 registered, especially the existing upper-right diagonal. Material remains quiet pale gray natural hand-painted stone. Output only this same stone detail. Do not add any architecture, objects, extra grout, decorative stripe, grid, red paper or anything copied from references2-4. Those images are style/layout context only."""
pp=D/"p02_01.geometry-v01.prompt.txt"
rp=D/"p02_01.geometry-v01.request.json"
assert not pp.exists() and not rp.exists()
pp.write_text(prompt,encoding="utf-8")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=B/"native/p02_01.png"
req=copy.deepcopy(original)
req.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())
req["references"][0]={"file":str(source),"sha256":sha(source),"role":"edit target: native1254 stone geometry, move only lower horizontal and transverse joints"}
req["referenced_image_paths"]=[r["file"] for r in req["references"]]
req["refinementOf"]={"file":str(source),"sha256":sha(source),"issue":"lower second horizontal groove190px too high"}
rp.write_text(json.dumps(req,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"request":str(rp),"target":str(source)}))
