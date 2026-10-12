from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=json.loads((D/"roof-horizontal-protected-v02/request.json").read_text())
Afile=D/"integrated-local-v04/assembly.json";A=json.loads(Afile.read_text());im=Image.open(A["contextOutput"]["file"])
specs=[
{"attempt":"roof-vertical-join-v01","box":[2560,2932,3814,4186],"prompt":"Edit IMAGE1 only, exact same native1254 crop. Fix the ONE visible vertical pasted join running through the rising gold roof rail, dark teal molding and red support near the middle x550..750. Smoothly align the upper gold outline, the long teal molding ridges, and the red beam contours across that join, making each a single continuous curve with no cut, ledge, step or duplicate line. Keep the left golden roof tip, all outer edges and all objects precisely in place. Keep original textures, highlights, hue and brightness; no recoloring or surface cleanup. Keep the pavement background and cream edge unchanged. Repair only this local joint, no new ornament, no reshaping the building. Images2-5 context only, no copied objects. Opaque1254PNG, no resize or reframing."},
{"attempt":"blue-border-south-join-v01","box":[1980,2680,3234,3934],"prompt":"Edit IMAGE1 only, same native1254 crop. Repair the pasted steps along the diagonal cream stone band and adjacent muted blue-gray pavement. Both long boundaries of the cream band must flow continuously in their existing directions, without the three abrupt stair-step notches caused by pasted patches. Preserve the band width, original endpoints at the four crop edges, and the existing thin gray stone joints at top. Replace only the pasted central notches and ragged blue color seams by continuous calm blue-gray matte paving of matching surrounding color, with no added texture pattern. Preserve the golden roof ornament at lower right and every object exactly. Keep all other geometry and colors unchanged; no new seam, crack, tile, structure or border. Images2-5 approved context only. Opaque native1254PNG, no scaling, reframing or rotation."}
]
out=[]
for s in specs:
 f=D/s["attempt"];f.mkdir(exist_ok=False);im.crop(s["box"]).save(f/"input.png");pf=f/"prompt.txt";pf.write_text(s["prompt"])
 refs=[dict(x) for x in base["references"]];refs[0]={"file":str(f/"input.png"),"sha256":sha(f/"input.png"),"role":"native1to1 assembled crop; local edit target"}
 q=dict(base);q.update(attempt=s["attempt"],prompt=s["prompt"],promptFile=str(pf),promptSha256=sha(pf),references=refs,referenced_image_paths=[x["file"] for x in refs],sourceAssembly=str(Afile),sourceContext=A["contextOutput"],sourceCrop=s["box"],cropWorldBox=[s["box"][0]+16269,s["box"][1]+44941,s["box"][2]+16269,s["box"][3]+44941],preparedAtUtc=datetime.now(timezone.utc).isoformat())
 (f/"request.json").write_text(json.dumps(q,indent=2));out.append(q)
print(json.dumps(out))

