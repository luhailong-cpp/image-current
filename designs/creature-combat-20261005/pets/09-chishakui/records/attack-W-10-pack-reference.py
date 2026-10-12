from PIL import Image
from pathlib import Path
import json,hashlib
r=Path(r'D:/work/image/designs/creature-combat-20261005/pets/09-chishakui')
paths=[r/'runtime/attack/W/09.png',r/'runtime/attack/W/11.png']
im=Image.new('RGBA',(2048,1024),(0,0,0,0))
for x,p in enumerate(paths):
 s=Image.open(p).convert('RGBA'); assert s.size==(1024,1024); im.paste(s,(x*1024,0))
p=r/'records/attack-W-10-neighbors.reference.png'; im.save(p)
(p.with_suffix('.png.source.json')).write_text(json.dumps({'purpose':'reference-only exact pixel contact sheet, never runtime or generated pose','layout':'left W09, right W11','operation':'unscaled side-by-side packing, no pose editing','sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]},indent=2),encoding='utf-8')
print(p)

