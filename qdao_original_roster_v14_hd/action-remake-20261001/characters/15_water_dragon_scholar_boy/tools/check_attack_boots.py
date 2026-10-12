from pathlib import Path
from PIL import Image
import json
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy")
q=json.loads((B/"audit/attack-selection.json").read_text(encoding="utf-8-sig"))
for r in q["frames"]:
 if r["direction"]!="W":continue
 out=[]
 for key in [Path(r["source"]).stem,f'attack-W-{r["frame"]:02}-foot-v1']:
  p=B/"sources/new"/(key+".png")
  if not p.exists():continue
  a=Image.open(p).getchannel("A").point(lambda x:255 if x>64 else 0)
  box=a.getbbox()
  out.append([key,box, a.crop((0,1000,700,1254)).getbbox(),a.crop((700,1000,1254,1254)).getbbox()])
 print(json.dumps(out))

