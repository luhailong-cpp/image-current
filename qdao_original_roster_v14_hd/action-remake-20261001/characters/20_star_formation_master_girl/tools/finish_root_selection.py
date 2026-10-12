from pathlib import Path
import json
r=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
p=r/"grounding4/NW/selected.json";x=json.loads(p.read_text(encoding="utf-8-sig"))
for frame,name in [(15,"16-pairs-v3"),(16,"15-pairs-v3")]:
 f=f"grounding4/NW/{name}-1024.png";x.append({"frame":frame,"exportFile":f,"nativeFile":f.replace("-1024.png",".png"),"generationRecord":f.replace("-1024.png",".png.generation.json"),"supportFoot":"left","position":"rear_push","mode":"replace_or_rephase","visualStaticReviewed":False,"requestedSlot":int(name[:2])})
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

