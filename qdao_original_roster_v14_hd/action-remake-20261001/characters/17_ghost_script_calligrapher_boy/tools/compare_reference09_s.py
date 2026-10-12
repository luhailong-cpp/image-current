from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy');R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl');O=B/'review/reference09-S';O.mkdir(exist_ok=True)
m=json.loads((R/'manifest.json').read_text(encoding='utf-8'));s=next(x for x in m['sequences'] if x['label']=='run/S')
print(json.dumps({'status':m['status'],'checkedAtUtc':m['checkedAtUtc'],'sequence':{k:s.get(k) for k in ['label','count','ms']},'frames':[{k:f.get(k) for k in ['slot','file','sha256','visualApproval','dynamicApproval']} for f in s['frames']]}))
sel=json.loads((B/'review/review-run-S.json').read_text(encoding='utf-8'))['frames'];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
evidence=[]
for half in range(2):
 sheet=Image.new('RGB',(960,1080),(39,45,49));d=ImageDraw.Draw(sheet)
 for offset in range(8):
  i=half*8+offset;n=i+1;x=(offset%2)*480;y=(offset//2)*270
  rp=R/'runtime/run/S'/f'{n:02d}.png';sp=B/sel[i]['file']
  for dx,p,label in [(0,rp,f'09 approved reference S{n:02d}'),(240,sp,f'17 selected S{n:02d}')]:
   im=Image.open(p).convert('RGBA').resize((240,240),Image.Resampling.LANCZOS)
   d.text((x+dx+4,y+5),label,font=font,fill='white');sheet.paste(im,(x+dx,y+27),im)
  evidence.append({'frame':n,'referenceFile':str(rp),'referenceSha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'referenceSize':list(Image.open(rp).size),'manifestSha256Matches':hashlib.sha256(rp.read_bytes()).hexdigest()==s['frames'][i]['sha256'],'selected17':sel[i]['file'],'selected17Sha256':sel[i]['sha256']})
 sheet.save(O/f'pair-{half+1}-240.png')
(O/'input-evidence.json').write_text(json.dumps({'manifestSha256':hashlib.sha256((R/'manifest.json').read_bytes()).hexdigest(),'timing':json.loads((R/'animation-timing.json').read_text(encoding='utf-8')),'frames':evidence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

