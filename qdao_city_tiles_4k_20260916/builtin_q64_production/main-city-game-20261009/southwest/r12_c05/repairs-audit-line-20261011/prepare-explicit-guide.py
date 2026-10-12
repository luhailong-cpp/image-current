from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";P=D/"p02_02.geometry-only-guide.png"
I=Image.new("RGB",(1254,1254),(221,219,214));d=ImageDraw.Draw(I)
d.polygon([(0,940),(554,940),(554,1254),(0,1254)],fill=(230,223,211))
lines=[[(0,177),(262,349),(1192,997),(1254,1048)],[(0,541),(262,349),(789,0)],[(0,940),(554,940),(554,1254)],[(554,940),(1029,1254)],[(1192,997),(1254,954)]]
for points in lines:d.line(points,fill=(133,128,122),width=4)
I.save(P)
ref=B/"guides/p02_02.layout-only.png"
(P.with_suffix(".provenance.json")).write_text(json.dumps({"file":str(P),"sha256":hashlib.sha256(P.read_bytes()).hexdigest(),"guideOnly":True,"gameArt":False,"finalCandidate":False,"operation":"explicit geometric line diagram for builtin guidance, no native output claimed","nativePixels":[1254,1254],"polylineCoordinates":lines,"sourceGuide":str(ref),"sourceGuideSha256":hashlib.sha256(ref.read_bytes()).hexdigest(),"sourceUncertaintyNativePixels":52.26},indent=2))
print(str(P))

