from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
prefix=sys.argv[1]; art=ROOT/'qa'/(prefix+'-candidate-4096.png'); im=Image.open(art).convert('RGB'); assert im.size==(4096,4096)
views=[]
for ri in range(4):
    out=Image.new('RGB',(1500,1024))
    for ci,x in enumerate((1024,2048,3072)):out.paste(im.crop((x-250,ri*1024,x+250,(ri+1)*1024)),(ci*500,0))
    p=ROOT/'qa'/(prefix+f'-vertical-row{ri+1}-native100.png');out.save(p);views.append(str(p))
for ci in range(4):
    out=Image.new('RGB',(1024,1500))
    for ri,y in enumerate((1024,2048,3072)):out.paste(im.crop((ci*1024,y-250,(ci+1)*1024,y+250)),(0,ri*500))
    p=ROOT/'qa'/(prefix+f'-horizontal-column{ci+1}-native100.png');out.save(p);views.append(str(p))
dump(ROOT/'qa'/(prefix+'-native-views.json'),{'source':metadata(art,'native4096 same-coordinate candidate'),'operation':'crop and concatenate at 1:1 for QA only, adjacent panels are separate seam views','views':views})
print(json.dumps({'views':len(views),'sourceSha256':hashfile(art)}))
