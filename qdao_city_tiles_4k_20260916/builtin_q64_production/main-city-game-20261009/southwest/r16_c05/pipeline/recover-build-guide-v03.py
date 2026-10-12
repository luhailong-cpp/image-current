import json,hashlib,pathlib
from PIL import Image,ImageDraw
t=pathlib.Path(__file__).resolve().parents[1]
p=t/'pipeline/prompts/p02_01.recover-course-v03.request.json'
r=json.loads(p.read_text(encoding='utf-8'))
s=pathlib.Path(r['referenced_image_paths'][0]);im=Image.open(s).convert('RGB');d=ImageDraw.Draw(im)
d.line([(0,730),(1253,730)],fill=(100,91,79),width=6)
d.line([(0,835),(1253,835)],fill=(190,179,161),width=6)
d.line([(768,230),(768,730)],fill=(113,106,94),width=4)
d.line([(98,835),(98,1253)],fill=(123,115,102),width=4)
o=t/'pipeline/guides/p02_01.recover-course-v03.mechanical-lines-not-art.png'
assert not o.exists();im.save(o)
h=lambda x:hashlib.sha256(pathlib.Path(x).read_bytes()).hexdigest()
o.with_suffix('.png.derivation.json').write_text(json.dumps({'source':str(s),'sourceSha256':h(s),'outputSha256':h(o),'purpose':'mechanical guide only, never final artwork','pixelResampling':False,'nativeTop230Preserved':True,'lines':{'course':[730,835],'upperJoint':768,'lowerJoint':98}},indent=2),encoding='utf-8')
r['references'][0]={'file':str(o),'sha256':h(o),'role':'mechanical positional guide only; TOP230 exact native; no final artwork'}
r['referenced_image_paths'][0]=str(o)
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(o)
