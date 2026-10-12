import json,pathlib,hashlib
from PIL import Image,ImageDraw
t=pathlib.Path(__file__).resolve().parents[1]
p=t/'pipeline/prompts/p02_02.recover-20261013b-v01.request.json';r=json.loads(p.read_text(encoding='utf-8'))
s=pathlib.Path(r['referenced_image_paths'][0]);im=Image.open(s).convert('RGB');d=ImageDraw.Draw(im)
lines=[([230,730,1253,730],[100,91,79],4),([230,835,1253,835],[190,179,161],4),([975,230,975,730],[113,106,94],4),([420,835,420,1253],[123,115,102],4)]
for xy,c,w in lines:d.line(xy,fill=tuple(c),width=w)
o=t/'pipeline/guides/p02_02.recover-20261013b-v01.mechanical-lines-not-art.png';assert not o.exists();im.save(o)
h=lambda x:hashlib.sha256(pathlib.Path(x).read_bytes()).hexdigest()
o.with_suffix('.png.derivation.json').write_text(json.dumps({'source':str(s),'sourceSha256':h(s),'outputSha256':h(o),'purpose':'mechanical guide only never final art','pixelResampling':False,'nativeTopAndLeft230Preserved':True,'lines':lines},indent=2),encoding='utf-8')
r['references'][0]={'file':str(o),'sha256':h(o),'role':'mechanical exact geometry guide only; TOP230 LEFT230 exact native unchanged'};r['referenced_image_paths'][0]=str(o)
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(o)
