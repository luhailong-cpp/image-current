import sys,json
from pathlib import Path
from PIL import Image,ImageDraw
run=Path(__file__).resolve().parent/'runs'/sys.argv[1]
m=json.loads((run/'manifest.json').read_text())
items=[x for x in m['artifacts'] if x.get('pixels')==[1024,320]]
for k in range(0,len(items),4):
 part=items[k:k+4]; canvas=Image.new('RGB',(1024,len(part)*348),(20,24,28));draw=ImageDraw.Draw(canvas)
 for j,item in enumerate(part):
  draw.text((8,j*348+6),Path(item['file']).stem,fill='white');canvas.paste(Image.open(item['file']),(0,j*348+28))
 canvas.save(run/f'view-batch-{k//4+1:02}.png')
print(json.dumps({'batches':(len(items)+3)//4,'items':len(items)}))
