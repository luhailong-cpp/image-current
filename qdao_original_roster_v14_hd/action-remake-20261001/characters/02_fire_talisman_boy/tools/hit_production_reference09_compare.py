import json,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[1]
ref=root.parent/'09_bamboo_archer_girl'
manifest=json.loads((ref/'manifest.json').read_text(encoding='utf-8-sig'))
own=json.loads((root/'inventory-hit.json').read_text(encoding='utf-8-sig'))
ownmap={(x['action'],x['direction'],x['frame']):x for x in own['frames']}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
record={'createdAt':datetime.datetime.now(ZoneInfo('America/New_York')).isoformat(),'referenceRoot':str(ref),'manifestSHA256':hashlib.sha256((ref/'manifest.json').read_bytes()).hexdigest(),'purpose':'用户经统筹明确授权09当前版本作为动作参照；只读09，整画布比较，不把09未审范围扩大为整段通过','frames':[],'sheets':[]}
for action,direction in [('run','S'),('run','SW'),('hit','E'),('hit','W')]:
 seq=next(x for x in manifest['sequences'] if x['action']==action and x['direction']==direction)
 refmap={x['frame']:x for x in seq['frames']}
 groups=[(1,8),(9,16)] if action=='run' else [(1,6)]
 outdir=root/('work/run-'+direction if action=='run' else 'work/hit')
 for first,last in groups:
  cols=4 if action=='run' else 3
  pairs=(last-first+1+cols-1)//cols
  w,h=cols*320,pairs*2*352
  sheet=Image.new('RGB',(w,h),(230,233,234))
  draw=ImageDraw.Draw(sheet)
  for idx,n in enumerate(range(first,last+1)):
   for rowtag,item,path in [('09',refmap[n],ref/refmap[n]['file']),('02',ownmap[(action,direction,n)],root/ownmap[(action,direction,n)]['path'])]:
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha==item['sha256'],str(path)+' current SHA mismatch'
    col=idx%cols;pair=idx//cols;row=pair*2+(rowtag=='02');x=col*320;y=row*352
    draw.text((x+8,y+4),f'{rowtag} {action}/{direction}/{n:02}',font=font,fill=(20,30,40))
    for yy in range(0,320,20):
     for xx in range(0,320,20):
      draw.rectangle((x+xx,y+32+yy,x+xx+19,y+32+yy+19),fill=((242,244,245) if ((xx//20+yy//20)%2) else (218,222,225)))
    im=Image.open(path).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS)
    sheet.paste(im,(x,y+32),im)
    record['frames'].append({'character':rowtag,'action':action,'direction':direction,'frame':n,'file':str(path),'sha256':sha,'sourceStatus':item.get('visualApproval',item.get('visual_status'))})
  out=outdir/f'ref09-{action}-{direction}-{first:02}-{last:02}-contact-sheet.png'
  sheet.save(out)
  record['sheets'].append({'file':str(out.relative_to(root)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':'整1024画布固定缩为320并排，未裁剪/配准/改变源像素。'})
out=root/'records/run-S-reference09-comparison-inputs-20261003.json'
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'readAllManifestBytes':(ref/'manifest.json').stat().st_size,'selectedFrames':len(record['frames']),'sheets':record['sheets']},ensure_ascii=True))

