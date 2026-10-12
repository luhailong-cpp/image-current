from pathlib import Path
from PIL import Image
import json
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
rois={'E':(530,800,900,1024),'W':(200,800,540,1024),'N':(480,800,660,1024),'NE':(560,800,800,1024),'NW':(250,770,520,1024),'S':(440,800,710,1024),'SE':(400,800,650,1024),'SW':(220,800,550,1024)}
out={}
for d,box in rois.items():
 p=r/f'candidate/run/{d}/02.png'
 a=Image.open(p).getchannel('A')
 reg=a.crop(box);b=reg.point(lambda v:255 if v>128 else 0).getbbox()
 out[d]={'manuallyChosenSupportBootROI':box,'opaqueExtentInROI':[b[0]+box[0],b[1]+box[1],b[2]+box[0],b[3]+box[1]]}
print(json.dumps(out))

