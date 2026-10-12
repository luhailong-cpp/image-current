from PIL import Image,ImageStat,ImageChops
from pathlib import Path
import json
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast");N=Z/"native";H=115;E=1139
def image(n):return Image.open(N/n).convert("RGB")
def mae(a,b):return sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
out={"purpose":"boundary color step comparison ONLY, supplemental to visual QA","modelQualityClaim":None,"patchVersions":{}}
for v in ["v1","v2","v3","v4"]:
 im=image("r05_c14_p34-"+v+".png"); left=image("r05_c14_p33-v1.png");top=image("r05_c14_p24-v1.png");bottom=image("r05_c14_p44-v1.png")
 out["patchVersions"][v]={"topCoreRGBMeanStep":mae(top.crop((H,E-1,E,E)),im.crop((H,H,E,H+1))),"leftCoreRGBMeanStep":mae(left.crop((E-1,H,E,E)),im.crop((H,H,H+1,E))),"bottomCoreRGBMeanStep":mae(im.crop((H,E-1,E,E)),bottom.crop((H,H,E,H+1))),"causticCompositionMeanChangeFromV1":mae(image("r05_c14_p34-v1.png"),im)}
p=Z/"qa/r05_c14_p34.boundary-step-comparison.json";p.write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out))

