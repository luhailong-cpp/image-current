from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent.parent;Q=B/'pipeline-tools/local-delivery-inventory-20261013'
d=json.loads((Q/'inventory.json').read_text(encoding='utf-8'));art=176;cell=188;rowheight=224;header=68
canvas=Image.new('RGB',(8*cell,header+8*rowheight),(24,28,35));draw=ImageDraw.Draw(canvas)
draw.text((12,10),'SOUTHWEST COVERAGE QA ONLY - NOT A FINAL MAP',fill='white');draw.text((12,30),'64 tiles | 15 full candidates | 3 partial | 46 untouched | 766 missing patches | accepted 0',fill=(230,230,230))
for i,t in enumerate(d['tiles']):
 x=(i%8)*cell+6;y=header+(i//8)*rowheight;tileim=Image.new('RGB',(art,art),(55,59,67))
 if t['candidate']:tileim=Image.open(t['candidate']['file']).convert('RGB').resize((art,art),Image.Resampling.LANCZOS)
 elif t['selectedNativePatchCount']:
  for n in t['selectedNativeRecords']:
   pid=n['patch'];r=int(pid[1:3])-1;c=int(pid[4:6])-1;im=Image.open(n['file']).convert('RGB').crop((115,115,1139,1139)).resize((44,44),Image.Resampling.LANCZOS);tileim.paste(im,(c*44,r*44))
 else:ImageDraw.Draw(tileim).text((15,80),'No native artwork',fill=(180,180,190))
 canvas.paste(tileim,(x,y+20));count=t['selectedNativePatchCount'];draw.text((x,y),f'{t["tile"]} {count}/16',fill=(240,185,65) if count else (165,165,175));draw.text((x,y+art+25),'Pending QA' if count==16 else f'Missing {16-count}',fill=(210,210,210))
p=Q/'coverage-QA-only-v02.png';assert not p.exists();canvas.save(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(Q/'preview-v02-derivation.json').write_text(json.dumps({'file':str(p),'sha256':sha(p),'inventory':str(Q/'inventory.json'),'inventorySha256':sha(Q/'inventory.json'),'QAOnly':True,'notFinalArtwork':True,'resizedOnlyForPreview':True,'rowSpacingIncreasedForNonOverlappingLabels':True,'originalPreviewPreserved':str(Q/'coverage-QA-only.png')},indent=2)+'\n',encoding='utf-8')
print(p)
