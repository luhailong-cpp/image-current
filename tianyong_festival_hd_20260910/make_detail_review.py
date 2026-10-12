from pathlib import Path
from PIL import Image
import json
r=Path(r'E:\work\image\tianyong_festival_hd_20260910')
im=Image.open(r/'tianyong_city_master_6144.png').convert('RGB')
guide=Image.open(r/'layout-guide-6144.png').convert('RGB')
boxes={'main_hall':(2432,1024,3456,2048),'central_plaza_seam':(2560,2432,3584,3456),'market':(448,2816,1472,3840),'south_gate_seam':(2560,4800,3584,5824),'moon_rabbit_garden':(4928,4544,5952,5568)}
records=[]
for name,box in boxes.items():
 final=im.crop(box)
 final.save(r/'qa'/f'{name}_100percent.png')
 before=guide.crop(box)
 pair=Image.new('RGB',(2048,1024));pair.paste(before,(0,0));pair.paste(final,(1024,0))
 pair.save(r/'qa'/f'{name}_before_after.png')
 records.append({'name':name,'pixelBox':box,'cropPixels':'unresampled 1024x1024','comparison':'left enlarged old layout preview, right regenerated final at same coordinates'})
(r/'qa'/'detail-review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('5 targeted native crops and matching before/after evidence saved.')
