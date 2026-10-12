"""Check existing AI frames, create a truthful manifest and browser/contact previews."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,collections
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
CONTRACT={'hit':(6,40),'attack':(12,30),'cast':(16,45)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
frames=[];missing=[];issues=[];groups=[]
visual_file=ROOT/'QA'/'visual-review.json'
visual=json.loads(visual_file.read_text(encoding='utf-8')) if visual_file.exists() else {}
qa=ROOT/'QA'; qa.mkdir(exist_ok=True)
for action,(count,ms) in CONTRACT.items():
 for direction in ['E','W']:
  group={'action':action,'direction':direction,'durationMs':ms,'expectedFrames':count,'frames':[]}
  for i in range(1,count+1):
   path=ROOT/'runtime'/action/direction/f'{i:02}.png'
   if not path.exists(): missing.append(path.relative_to(ROOT).as_posix());continue
   with Image.open(path) as im:
    assert im.mode=='RGBA',f'{path}: RGBA required'
    alpha=im.getchannel('A');hist=alpha.histogram(); box=alpha.point(lambda x:255 if x>16 else 0).getbbox()
    entry={'file':path.relative_to(ROOT).as_posix(),'action':action,'direction':direction,'frame':i,'durationMs':ms,'width':im.width,'height':im.height,'pivot':[0.5,0.08],'footAnchorTopLeft':[512,942],'event':'impact' if action=='attack' and i==7 else 'release' if action=='cast' and i==10 else None,'sha256':sha(path),'alpha':{'min':alpha.getextrema()[0],'max':alpha.getextrema()[1],'transparentPixels':hist[0],'partialPixels':sum(hist[1:255]),'opaquePixels':hist[255],'contentBBoxAlpha16':box},'generationRecord':f'generation/{action}/{direction}/{i:02}.generation.json','visualStatus':'pending sequence review','clientStatus':'not integrated or tested'}
    entry['pixelSHA256']=hashlib.sha256(im.tobytes()).hexdigest()
    entry['mirroredPixelSHA256']=hashlib.sha256(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes()).hexdigest()
    if im.size!=(1024,1024):issues.append({'file':entry['file'],'issue':'incorrect dimensions'})
    if hist[0]==0 or hist[255]==0:issues.append({'file':entry['file'],'issue':'alpha lacks fully transparent or opaque pixels'})
    if not (ROOT/entry['generationRecord']).exists():issues.append({'file':entry['file'],'issue':'generation record missing'})
    else:
     rec=json.loads((ROOT/entry['generationRecord']).read_text(encoding='utf-8-sig'))
     if rec.get('sha256')!=entry['sha256']:issues.append({'file':entry['file'],'issue':'generation SHA mismatch'})
     prompt=Path(rec['prompt']);prompt=prompt if prompt.is_absolute() else ROOT/prompt
     if not prompt.is_file():issues.append({'file':entry['file'],'issue':'prompt missing'})
     if rec.get('actualModel') is not None or rec.get('actualQuality') is not None:issues.append({'file':entry['file'],'issue':'unexpected asserted model/quality'})
     entry['sourceSHA256']=rec['native']['sha256']
     entry['exportTransform']=rec.get('operation')
     entry['modelTarget']=rec['configSnapshot']['model'];entry['qualityTarget']=rec['configSnapshot']['quality']
     entry['actualModel']=None;entry['actualQuality']=None
    if visual.get('completed'):entry['visualStatus']='reviewed: all frames, normal/quarter speed and stepping; see QA/visual-review.json'
    frames.append(entry);group['frames'].append(entry)
  groups.append(group)
  if group['frames']:
   size=320;cols=4;rows=(len(group['frames'])+cols-1)//cols
   sheet=Image.new('RGB',(cols*size,rows*(size+24)), '#e9e5da'); draw=ImageDraw.Draw(sheet)
   for k,frame in enumerate(group['frames']):
    x=k%cols*size;y=k//cols*(size+24)
    for yy in range(y,y+size,20):
     for xx in range(x,x+size,20):
      if ((xx-x)//20+(yy-y)//20)%2:draw.rectangle((xx,yy,xx+19,yy+19),fill='#cdd1cd')
    with Image.open(ROOT/frame['file']) as im:
     thumb=im.resize((size,size),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb)
    draw.text((x+10,y+size+4),f'{action} {direction} {frame["frame"]:02} / {ms}ms',fill='#183f36')
   sheet.save(qa/f'{action}-{direction}-contact.png')
hashes=collections.defaultdict(list)
for f in frames:hashes[f['sha256']].append(f['file'])
duplicates=[v for v in hashes.values() if len(v)>1]
pixel_hashes=collections.defaultdict(list)
for f in frames:pixel_hashes[f['pixelSHA256']].append(f['file'])
pixel_duplicates=[v for v in pixel_hashes.values() if len(v)>1]
mirrors=[{'file':f['file'],'matches':pixel_hashes[f['mirroredPixelSHA256']]} for f in frames if f['mirroredPixelSHA256'] in pixel_hashes]
source_hashes=collections.defaultdict(list)
for f in frames:source_hashes[f.get('sourceSHA256','missing')].append(f['file'])
source_duplicates=[v for v in source_hashes.values() if len(v)>1]
if source_duplicates:issues.append({'issue':'duplicate native sources','files':source_duplicates})
if pixel_duplicates:issues.append({'issue':'duplicate pixels','files':pixel_duplicates})
if mirrors:issues.append({'issue':'mirrored duplicate pixels','files':mirrors})
manifest={'character':'14-feierling','name':'绯耳灵','updatedAt':datetime.now(timezone.utc).isoformat(),'expectedFrameCount':68,'frameCount':len(frames),'directions':{'E':'front three-quarter southeast','W':'rear three-quarter northwest; independently generated'},'pivot':[0.5,0.08],'clientValidation':'not performed','frames':frames}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
check={'updatedAt':manifest['updatedAt'],'expected':68,'present':len(frames),'missing':missing,'issues':issues,'duplicateByteHashes':duplicates,'technicalChecksPassed':len(frames)==68 and not missing and not issues and not duplicates,'visualValidation':'see QA/visual-review.json' if visual.get('completed') else 'pending, do not infer from technical result','clientValidation':'not performed'}
(qa/'technical-validation.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'SHA256SUMS.txt').write_text(''.join(f'{f["sha256"]}  {f["file"]}\n' for f in frames),encoding='utf-8')
overview=Image.new('RGB',(960,696),'#e9e5da');od=ImageDraw.Draw(overview)
try:font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
except OSError:font=ImageFont.load_default()
for row,d in enumerate(['E','W']):
 for col,(a,i,label) in enumerate([('hit',3,'受击'),('attack',7,'普攻'),('cast',10,'施法')]):
  p=ROOT/'runtime'/a/d/f'{i:02}.png';x=col*320;y=row*348
  for yy in range(y,y+320,20):
   for xx in range(x,x+320,20):
    if ((xx-x)//20+(yy-y)//20)%2:od.rectangle((xx,yy,xx+19,yy+19),fill='#cdd1cd')
  if p.exists():
   with Image.open(p) as im:
    thumb=im.resize((320,320),Image.Resampling.LANCZOS);overview.paste(thumb,(x,y),thumb)
  od.text((x+12,y+323),f'{label} · {d} · {i:02}',font=font,fill='#183f36')
overview.save(qa/'overview.png')
template=(ROOT/'preview-template.html').read_text(encoding='utf-8')
(ROOT/'preview.html').write_text(template.replace('__GROUPS__',json.dumps(groups,ensure_ascii=False)),encoding='utf-8')
print(json.dumps({'present':len(frames),'missing':len(missing),'issues':issues,'duplicates':duplicates},ensure_ascii=False))
