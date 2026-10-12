from PIL import Image, ImageDraw
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
args=sys.argv[1:]
if args and args[0]=='import':
 invp=R/'inventory-hit.json'; inv=json.loads(invp.read_text(encoding='utf-8-sig'))
 for stem in args[1:]:
  rp=R/'reviews'/f'{stem}.generation.json';rec=json.loads(rp.read_text(encoding='utf-8-sig'));native=R/rec['file'];im=Image.open(native).convert('RGBA')
  assert min(im.size)>=1024
  outrel=f"frames/run/{rec['direction']}/{rec['frame']:02}.png"; out=R/outrel
  im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
  rel=str(rp.relative_to(R)).replace('\\','/')
  rec.update(status='generated_exported_sequence_review_pending',formalImport=True,nativeDimensions={'width':im.width,'height':im.height,'format':'PNG','mode':'RGBA'},native_size=list(im.size),visual_status='two_frame_position_candidate_full_sequence_pending')
  rec['export']={'file':outrel,'sha256':sha(out),'width':1024,'height':1024,'operation':'uniform full-canvas LANCZOS downsample; no bbox scaling, mirror, warp, or per-frame floor translation','derivedFrom':{'file':rec['file'],'sha256':sha(native),'record':rel}}
  rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
  side={'file':outrel,'sha256':sha(out),'generationRecord':rel,'derivedFrom':dict(rec['export']['derivedFrom'],generationRecord=rel),'operation':rec['export']['operation'],'actualModel':None,'actualQuality':None,'unverifiedReason':rec['unverifiedReason']}
  out.with_suffix('.png.generation.json').write_text(json.dumps(side,ensure_ascii=False,indent=2),encoding='utf-8')
  ent={'action':'run','direction':rec['direction'],'frame':rec['frame'],'path':outrel,'native_size':list(im.size),'native_path':rec['file'],'native_sha256':sha(native),'native_evidence':rel,'source_record':rel,'sha256':sha(out),'visual_status':rec['visual_status']}
  inv['frames']=[f for f in inv['frames'] if not(f['action']=='run' and f['direction']==rec['direction'] and f['frame']==rec['frame'])]+[ent]
  print(outrel,sha(out))
 invp.write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
for direction in ['S','SW']:
 sheet=Image.new('RGB',(1600,860),(225,230,234));draw=ImageDraw.Draw(sheet);order=list(range(7,15))+[15,16,1,2,3,4,5,6]
 for i,n in enumerate(order):
  p=R/f'frames/run/{direction}/{n:02}.png';im=Image.open(p).convert('RGBA');x=(i%8)*200;y=(i//8)*430
  sheet.paste(im.resize((200,200)),(x,y+25),im.resize((200,200)))
  crop=im.crop((200,620,850,1024)).resize((200,124));sheet.paste(crop,(x,y+235),crop)
  draw.text((x+6,y+4),f'{direction} {n:02} | '+('RIGHT' if i<8 else 'LEFT')+f' pair{i%8//2+1}',fill=(30,40,50))
 sheet.save(R/f'previews/run-{direction}-position-pairs-hit-review.png')
