import json
from pathlib import Path
from PIL import Image
import pipeline as p
root=p.ROOT;out=root/'root-external-qa-v1';out.mkdir(exist_ok=True)
upper=root/'r03_c04/candidate/r03_c04-pipeline-minimum-error-5a45bea8726a-ccd4a3.png'
lower=root/'r04_c04/candidate/r04_c04-pipeline-minimum-error-774db18be885-bd8f13.png'
a=Image.open(upper).convert('RGB');b=Image.open(lower).convert('RGB');items=[]
for i in range(4):
    im=Image.new('RGB',(1024,320));im.paste(a.crop((i*1024,3936,(i+1)*1024,4096)),(0,0));im.paste(b.crop((i*1024,0,(i+1)*1024,160)),(0,160))
    info=p.save_png(out/f'r03_c04-to-r04_c04-segment{i+1:02d}.png',im);items.append({**info,'sources':[{'file':str(upper),'sha256':p.sha(upper)},{'file':str(lower),'sha256':p.sha(lower)}],'boundaryWorldY':12288})
    neighbor=p.selected(p.tile_dir('r05_c04',p.contract()),f's01_{i+1:02d}');n=Image.open(neighbor).convert('RGB')
    im=Image.new('RGB',(1024,320));im.paste(b.crop((i*1024,3936,(i+1)*1024,4096)),(0,0));im.paste(n.crop((115,115,1139,275)),(0,160))
    info=p.save_png(out/f'r04_c04-to-r05_c04-segment{i+1:02d}.png',im);items.append({**info,'sources':[{'file':str(lower),'sha256':p.sha(lower)},p.native_info(neighbor)],'boundaryWorldY':16384})
p.put_json(out/'manifest.json',{'images':items,'nativeScale':1,'boundaryAtImageY':160,'formalAccepted':False})
print(out)
