from pathlib import Path
from PIL import Image
import json
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011/qa-macro-round-01";im=Image.open(B/"pipeline/output/3bd6fffd207bcdf3/r12_c05.candidate.context.png")
for name,w in [("roof-horizontal-native-preview",[19341,47501,20595,48755]),("roof-vertical-native-preview",[18829,47873,20083,49127])]:
 box=[w[0]-16269,w[1]-44941,w[2]-16269,w[3]-44941];im.crop(box).save(D/(name+".png"))
 (D/(name+".json")).write_text(json.dumps({"source":"pipeline/output/3bd6fffd207bcdf3/r12_c05.candidate.context.png","sourceWorldBox":[16269,44941,20595,49267],"worldBox":w,"cropBox":box,"resized":False,"qaOnly":True},indent=2))

