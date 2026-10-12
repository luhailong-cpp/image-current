from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";A=B.parent/"pipeline-tools/local-continuation-audit-20261011/topology-followup/patch-endpoints.json";j=json.loads(A.read_text())
spec=[]
for key in ["p01_03","p02_03","p02_04"]:
 p=next(x for x in j["patches"] if x["id"]==key);im=Image.new("RGB",(1254,1254),(221,219,214));dr=ImageDraw.Draw(im)
 if key=="p02_04":
  dr.polygon([(347,1254),(1015,783),(1254,614),(1254,1254)],fill=(232,227,216))
  dr.polygon([(863,1254),(1254,976),(1254,1254)],fill=(158,177,194))
 for line in p["segments"]:dr.line([tuple(z) for z in line["nativeEndpoints"]],fill=(139,134,128),width=4)
 path=D/(key+".coherent-geometry-guide-v03.png");im.save(path)
 prov={"guideOnly":True,"gameArt":False,"finalCandidate":False,"source":str(A),"sourceSha256":hashlib.sha256(A.read_bytes()).hexdigest(),"segments":p["segments"],"note":"explicit geometry-only global world-coordinate topology; all final art will be builtin native output"}
 path.with_suffix(".provenance.json").write_text(json.dumps(prov,indent=2))
 prompt="Render IMAGE1 diagram as clean matte stone game artwork at EXACT1254square crop. Retain every line, T/X intersection, endpoint, width and color boundary pixel-for-pixel; no added or missing joints. Preserve IMAGE1 warm-neutral gray and subtle cream colors, and muted blue-gray paving if present. Do NOT shift gray faces blue/cyan. IMAGE5 provides the quiet neutral limestone surface: plain broad untextured faces with gentle soft shading, absolutely NO visible grain, mesh, flakes, cells, brush weave or little repeating pattern. Keep all joints narrow and broad stone faces almost featureless. Shallow narrow seams with tiny bevel only, flat paving with no stairs, walls or objects. Images2-4 approved context only. Native1254opaquePNG, no rescaling."
 spec.append({"id":key,"attempt":key+"-coherent-geometry-v03","target":str(path),"targetRole":"precise global-coordinate geometry diagram; guide only, render game art","materialReference":str(D/"p02_02-geometry-quiet-v01/native.png"),"prompt":prompt})
(D/"batch-three-old-coherent.json").write_text(json.dumps(spec,indent=2))
print(str(D/"batch-three-old-coherent.json"))

