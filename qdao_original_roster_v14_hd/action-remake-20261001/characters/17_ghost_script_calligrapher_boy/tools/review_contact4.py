from pathlib import Path
from PIL import Image,ImageDraw
import json
b=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
for direction in ['N','NW']:
 rev=json.loads((b/('review-run-'+direction+'.json')).read_text(encoding='utf-8-sig'))
 keys=[Path(x['file']).stem for x in rev['selectedForSequenceReview']]
 for mode in ['240','feet']:
  w,h=(240,265) if mode=='240' else (330,280)
  sheet=Image.new('RGB',(4*w,2*h),(220,222,221));d=ImageDraw.Draw(sheet)
  for ii,n in enumerate([1,2,3,4,9,10,11,12]):
   k=keys[n-1];im=Image.open(b/'staging'/(k+'.png')).convert('RGBA')
   if mode=='feet': im=im.crop((330,740,1000,1254))
   im.thumbnail((w,h-25));x=(ii%4)*w+(w-im.width)//2;y=(ii//4)*h+25
   sheet.paste(im,(x,y),im);d.text(((ii%4)*w+4,(ii//4)*h+5),k,fill='black')
  sheet.save(b/'review'/('contact4-'+direction+'-before-'+mode+'.png'))

