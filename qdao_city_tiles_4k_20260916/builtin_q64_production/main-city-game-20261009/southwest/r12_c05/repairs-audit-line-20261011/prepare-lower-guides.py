from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";A=B.parent/"pipeline-tools/local-continuation-audit-20261011/topology-followup/patch-endpoints.json";data=json.loads(A.read_text())
ids=["p03_01","p03_02","p03_03","p04_01","p04_02"]
for key in ids:
 p=next(x for x in data["patches"] if x["id"]==key);im=Image.new("RGB",(1254,1254),(221,219,214));draw=ImageDraw.Draw(im)
 cream=(232,227,216);blue=(165,180,189)
 if key=="p03_01":
  draw.rectangle((0,0,1253,1253),fill=cream);draw.rectangle((0,125,915,1013),fill=(221,219,214));draw.rectangle((0,1118,272,1253),fill=blue)
 elif key=="p03_02":
  draw.rectangle((0,0,554,1253),fill=cream);draw.polygon([(948,1254),(1254,1044),(1254,1254)],fill=cream)
 elif key=="p03_03":
  draw.polygon([(0,1202),(722,705),(894,566),(1254,313),(1254,679),(952,893),(424,1254),(0,1254)],fill=cream)
  draw.polygon([(424,1254),(952,893),(1254,679),(1254,1254)],fill=blue)
 elif key=="p04_01":
  draw.rectangle((0,0,1253,1253),fill=cream);draw.rectangle((0,94,272,1253),fill=blue)
 elif key=="p04_02":
  draw.rectangle((0,0,554,1253),fill=cream);draw.polygon([(554,501),(1254,20),(1254,363),(554,841)],fill=cream)
  draw.polygon([(554,841),(1254,363),(1254,1019),(916,1254),(554,1254)],fill=blue)
  draw.polygon([(916,1254),(1254,1019),(1254,1254)],fill=cream)
 segs=[{"lineId":s["lineId"],"kind":s["kind"],"nativeEndpoints":s["nativeEndpoints"]} for s in p["segments"]]
 if key in ["p03_01","p03_02"]:
  a,b=(915,1254) if key=="p03_01" else (0,554)
  for name,y in [("creamBandH1-corrected-omission",412),("creamBandH2-corrected-omission",941)]:
   segs.append({"lineId":name,"kind":"weak_joint","nativeEndpoints":[[a,y],[b,y]]})
 for s in segs:
  if key=="p03_03" and s["lineId"]=="Ylower":s["nativeEndpoints"][-1]=[382,939]
  pts=[tuple(x) for x in s["nativeEndpoints"]];kind=s["kind"]
  color=(139,134,128) if kind not in ["weak_joint","color_edge"] else ((171,165,157) if kind=="weak_joint" else (130,144,151))
  draw.line(pts,fill=color,width=3 if kind=="weak_joint" else 4)
 path=D/(key+".geometry-only-guide-v02.png");im.save(path)
 evidence={"file":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"guideOnly":True,"gameArt":False,"finalCandidate":False,"nativePixels":[1254,1254],"segments":segs,"source":str(A),"sourceSha256":hashlib.sha256(A.read_bytes()).hexdigest(),"uncertaintyNativePixels":52.26,"corrections":["Faint cream-band horizontal seams source y907.0 and917.1 extend only worldx17183.6..17847.3; independently verified wider original source; omitted in prior audit graph.","p0303 Ylower snapped6px up to actual SErim intersection; it terminates, never crosses."],"sourceReviewImage":str(D/"qa-macro-round-01/west-frame-source-nearest20x.png")}
 path.with_suffix(".provenance.json").write_text(json.dumps(evidence,indent=2))
 print(path)

