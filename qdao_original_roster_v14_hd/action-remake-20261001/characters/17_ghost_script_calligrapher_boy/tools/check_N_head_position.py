from pathlib import Path
from PIL import Image
import json
b=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
out=[]
for old,new in [("run-N-08-v2","run-N-08-v3"),("run-N-10-v1","run-N-10-v2"),("run-N-13-v1","run-N-13-v2"),("run-N-04-v2","run-N-04-v3"),("run-N-12-v1","run-N-12-v2"),("run-N-15-v1","run-N-15-v2"),("run-N-16-v1","run-N-16-v2")]:
    tops=[]
    for key in (old,new):
        with Image.open(b/"staging"/(key+".png")) as im:
            a=im.getchannel("A").crop((350,0,950,560)); box=a.point(lambda x:255 if x>=240 else 0).getbbox()
            tops.append(box[1])
    out.append({"before":old,"after":new,"headTopAlpha240InFixedRoi":[350,0,950,560],"topY":tops,"deltaY":tops[1]-tops[0]})
print(json.dumps(out))

