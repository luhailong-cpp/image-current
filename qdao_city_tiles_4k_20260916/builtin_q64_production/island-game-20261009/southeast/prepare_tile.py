from pathlib import Path
from PIL import Image
import sys,json
from workflow import ROOT,read,write,sha,now
refs=read(ROOT/'references.json')
plan=read(ROOT/'coordinate-plan.json')
for tid in sys.argv[1:]:
 tile=next(t for t in plan['tiles'] if t['id']==tid)
 with Image.open(refs[0]['file']) as im:
  for p in tile['patches']:
   file=ROOT/'guides'/f"{p['id']}.layout-only.png"
   if file.exists():continue
   im.transform((1254,1254),Image.Transform.EXTENT,tuple(p['layoutReferenceBox']),Image.Resampling.BICUBIC).save(file)
   write(Path(str(file)+'.generation.json'),{'file':file.as_posix(),'sha256':sha(file),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','operation':'mechanical fractional-coordinate crop and enlargement, layout-only; never final artwork','derivedFrom':[refs[0]],'sourceCropBox':p['layoutReferenceBox'],'globalBox':p['nativeGlobalBox'],'usableAsFinalArt':False})
 print(tid)

