from pathlib import Path
from PIL import Image
import json,hashlib,sys
from datetime import datetime,timezone
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
A=json.loads((B/"pipeline/output/d2f5b37ffa7b74b2/assembly.json").read_text())
im=Image.open(A["contextOutput"]["file"])
base=json.loads((D/"p03_02-neutral-stone-v02/request.json").read_text())
specs=[
{"attempt":"seam-V2-row1-v01","box":[1536,0,2790,1254],"prompt":"Edit IMAGE1 at precisely the same native1254 square crop. Repair the two disconnected diagonal stone joints near the central vertical zone: reconnect each opposite pair as a SINGLE smooth straight very thin engraved joint, retaining the existing left and right continuation directions. No new branch, no deleted joint, no stair-step, no double ghost line. The ascending and descending joints remain separate where they already are. Make the light gray stone faces continuous across the central ragged pasted color edge: remove the abrupt cream/gray pasted silhouette, use the same quiet very pale neutral gray with subtle broad tonal variation. Preserve geometry at all four crop edges exactly, keep the top120pixel strip unchanged, do not move the distant crossing or any edge entry. All stone is quiet broad limestone, no small grain/mesh/lattice/cells or repeated pattern. IMAGE5 is only quiet material reference; preserve IMAGE1 overall color, not a blue cast. Images2-4 are context only: add no building, object, line or border. Opaque native1254 PNG, no scaling, rotation or reframing."},
{"attempt":"roof-horizontal-join-v01","box":[3072,2560,4326,3814],"prompt":"Edit only IMAGE1, same native1254 square crop. It is a close crop of ONE continuous gold roof rail rising from lower left into the large golden round boss on the right. Repair the visible pasted join near the center: remove the extra short upper golden tongue with its abrupt free cut end, integrate this gold material into a SINGLE continuous smoothly rising golden rail. Keep the existing large golden boss, its right contour, and the gold rail's lower-left entry exactly in place. Keep the continuous dark teal supporting molding beneath the rail, and retain the red-brown support at bottom. No new roof tip, scroll, branch, tile field, post, or repeated ornament. Blend the ragged light/dark blue-gray pavement paste boundary into one quiet stone surface; keep the cream pavement border at upper-left and its original direction, smoothly repair its tiny step if present. Preserve the outer120pixels and all existing entry and exit silhouettes, especially the far right edge. Images2-4 are approved city/style context only; no full city output. IMAGE5 is material restraint only. Same view, geometry scale, lighting and gold color. Opaque native1254 PNG, no resize or reframing."}
]
out=[]
for s in specs:
 f=D/s["attempt"];f.mkdir(exist_ok=False)
 crop=im.crop(s["box"]);assert crop.size==(1254,1254);crop.save(f/"input.png")
 pf=f/"prompt.txt";pf.write_text(s["prompt"],encoding="utf-8")
 refs=[dict(x) for x in base["references"]];refs[0]={"file":str(f/"input.png"),"sha256":sha(f/"input.png"),"role":"native1to1 assembled crop; edit this image only"}
 q={k:v for k,v in base.items() if k not in ["coordinates","id","configSnapshot"]}
 q.update(attempt=s["attempt"],operation="native cross-seam localized repair; not a selected slot",prompt=s["prompt"],promptFile=str(pf),promptSha256=sha(pf),references=refs,referenced_image_paths=[x["file"] for x in refs],sourceAssembly=str(B/"pipeline/output/d2f5b37ffa7b74b2/assembly.json"),sourceContext=A["contextOutput"],sourceCrop=s["box"],cropWorldBox=[s["box"][0]+16269,s["box"][1]+44941,s["box"][2]+16269,s["box"][3]+44941],resized=False,preparedAtUtc=datetime.now(timezone.utc).isoformat())
 (f/"request.json").write_text(json.dumps(q,indent=2),encoding="utf-8");out.append(q)
print(json.dumps(out))

