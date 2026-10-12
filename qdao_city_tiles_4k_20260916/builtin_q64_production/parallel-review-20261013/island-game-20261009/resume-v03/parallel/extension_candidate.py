import json,hashlib
from pathlib import Path
from PIL import Image
OUT=Path(__file__).parent
s=json.loads((OUT/'snapshot.json').read_text(encoding='utf-8'))
sources=[n for n in s['native'] if n['tileId']=='r03_c05']
canvas=Image.new('RGB',(4096,4096));replay=[]
for n in sources:
 im=Image.open(n['file']).convert('RGB').crop((115,115,1139,1139))
 box=((n['subcolumn']-1)*1024,(n['subrow']-1)*1024)
 canvas.paste(im,box);replay.append({'source':n,'crop':[115,115,1139,1139],'destination':[box[0],box[1],box[0]+1024,box[1]+1024]})
p=OUT/'r03_c05-diagnostic-hard-assembly-4096.png';assert not p.exists();canvas.save(p)
check=Image.open(p).convert('RGB');assert all(check.crop(v['destination']).tobytes()==Image.open(v['source']['file']).convert('RGB').crop(v['crop']).tobytes() for v in replay)
board=Image.new('RGB',(1536,1536));corners=[]
for r in range(1,4):
 for c in range(1,4):
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];crop=canvas.crop(box);name=f'extension-cross-{r}{c}-100pct.png';cp=OUT/name;assert not cp.exists();crop.save(cp);board.paste(crop,((c-1)*512,(r-1)*512));corners.append({'file':cp.as_posix(),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'tileLocalBox':box,'worldIntersection':[16384+c*1024,8192+r*1024]})
bp=OUT/'extension-cross-board-100pct.png';assert not bp.exists();board.save(bp)
record={'file':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[4096,4096],'diagnosticOnly':True,'productionAdopted':False,'formalAccepted':False,'operation':'16 exact native 1024 center cores pasted at integer positions; no resampling, feathering or synthesis','sourceReplayAll16PixelIdentical':True,'pixelCountVerified':4096*4096,'sources':replay,'corners':corners,'cornerBoard':bp.as_posix()}
(OUT/'extension-diagnostic.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(p)
