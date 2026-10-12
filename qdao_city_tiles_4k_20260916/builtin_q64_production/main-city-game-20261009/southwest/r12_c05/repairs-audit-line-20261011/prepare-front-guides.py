from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";A=B.parent/"pipeline-tools/local-continuation-audit-20261011/topology-followup/patch-endpoints.json";data=json.loads(A.read_text())
polys={"p01_01":[[(0,458),(632,0),(1254,0),(1254,5),(0,913)]],"p01_02":[[(0,0),(237,0),(0,172)]],"p01_04":[[(225,0),(478,0),(1254,526),(1254,686)]],"p02_01":[[(0,940),(1254,940),(1254,1254),(915,1254),(915,1149),(0,1149)]]}
for key,areas in polys.items():
 p=next(x for x in data["patches"] if x["id"]==key);im=Image.new("RGB",(1254,1254),(221,219,214));draw=ImageDraw.Draw(im)
 for poly in areas:draw.polygon(poly,fill=(232,227,216))
 segs=[]
 for s in p["segments"]:
  points=[tuple(v) for v in s["nativeEndpoints"]]
  if key=="p01_04" and s["lineId"]=="U2" and s["segment"]==2:points[-1]=(1228,669)
  color=(171,165,157) if s["kind"]=="weak_joint" else (139,134,128)
  draw.line(points,fill=color,width=3 if s["kind"]=="weak_joint" else 4)
  segs.append({"lineId":s["lineId"],"kind":s["kind"],"nativeEndpoints":points})
 path=D/(key+".geometry-only-guide.png");im.save(path)
 (path.with_suffix(".provenance.json")).write_text(json.dumps({"file":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"guideOnly":True,"gameArt":False,"finalCandidate":False,"operation":"explicit diagram traced from approved macro topology; no generated native pixels claimed","nativePixels":[1254,1254],"segments":segs,"creamGuidePolygons":areas,"source":str(A),"sourceSha256":hashlib.sha256(A.read_bytes()).hexdigest(),"sourceGuide":str(B/"guides"/(key+".layout-only.png")),"uncertaintyNativePixels":52.26,"junctionSnapNote":"p0104 U2 terminates at actual NE1 intersection(1228,669), a sub-source-pixel correction to prevent overshooting border" if key=="p01_04" else None},indent=2))
 print(path)

