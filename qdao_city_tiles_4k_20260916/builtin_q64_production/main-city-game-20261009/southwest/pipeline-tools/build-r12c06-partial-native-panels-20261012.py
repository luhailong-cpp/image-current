from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
a=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'));im=Image.open(a['output']['file']).convert('RGB');w,h=im.size
Q=B/'r12_c06/pipeline/qa'/Path(sys.argv[1]).parent.name/'root-native-panels';Q.mkdir(parents=True,exist_ok=True)
for x in [1024,2048,3072]:
    panel=Image.new('RGB',(256*(h//1024),1048),(255,255,255));d=ImageDraw.Draw(panel)
    for row in range(h//1024):panel.paste(im.crop((x-128,row*1024,x+128,(row+1)*1024)),(row*256,24));d.text((row*256+4,4),f'V{x//1024} row{row+1}',fill='black')
    panel.save(Q/f'V{x//1024}-native-panel.png')
for y in range(1024,h,1024):
    panel=Image.new('RGB',(1024,4*280),'white');d=ImageDraw.Draw(panel)
    for c in range(4):panel.paste(im.crop((c*1024,y-128,(c+1)*1024,y+128)),(0,c*280+24));d.text((4,c*280+4),f'H{y//1024} col{c+1}',fill='black')
    panel.save(Q/f'H{y//1024}-native-panel.png')
atomic_json(Q/'manifest.json',{'assembly':sys.argv[1],'source':a['output'],'nativePixelPanels':True,'resampling':False})
print(Q)

