from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math,datetime
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SPECS={'hit':(6,40),'attack':(12,30),'cast':(16,45)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def resolve(p):
    p=Path(p)
    return p if p.is_absolute() else ROOT/p
preview=ROOT/'preview'; preview.mkdir(exist_ok=True)
qa=ROOT/'qa'; qa.mkdir(exist_ok=True)
review_path=qa/'visual-review.json'
review=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
reviewed_hashes={f['file']:f['sha256'] for f in review.get('frameSnapshot',[])}
reviewed_indices={f['file']:i for i,f in enumerate(review.get('frameSnapshot',[]))}
review_sha=sha(review_path) if review_path.exists() else None
frames=[]; missing=[]; issues=[]; seen={}; groups=[]; preview_records=[]
for action,(count,ms) in SPECS.items():
 for direction in ['E','W']:
  group={'action':action,'direction':direction,'expected':count,'durationMs':ms,'frames':[]}
  thumbs=[]; playback=[]
  for i in range(1,count+1):
   p=ROOT/'runtime'/action/direction/f'{i:02d}.png'
   if not p.exists(): missing.append(rel(p)); continue
   im=Image.open(p); a=np.array(im.getchannel('A')) if im.mode=='RGBA' else np.zeros(im.size,dtype=np.uint8)
   digest=sha(p); duplicate=seen.get(digest); seen[digest]=rel(p)
   side=p.with_suffix('.png.generation.json')
   if not side.exists(): side=p.with_suffix('.generation.json')
   record=json.loads(side.read_text(encoding='utf-8-sig')) if side.exists() else {}
   bad=[]
   if im.size!=(1024,1024) or im.mode!='RGBA':bad.append('size/mode')
   if not (a.min()==0 and a.max()==255):bad.append('alpha range')
   if duplicate:bad.append('duplicate '+duplicate)
   if not record:bad.append('missing generation record')
   elif record.get('sha256')!=digest:bad.append('generation SHA mismatch')
   prompt=record.get('prompt'); evidence=record.get('evidence')
   receipt=evidence if isinstance(evidence,str) else (evidence or {}).get('receipt')
   for label,path in [('prompt',prompt),('receipt',receipt)]:
    if not path or not resolve(path).exists():bad.append('missing '+label)
   bbox=Image.fromarray((a>=16).astype('uint8')*255).getbbox()
   edge=int(np.count_nonzero(a[0]>=16)+np.count_nonzero(a[-1]>=16)+np.count_nonzero(a[:,0]>=16)+np.count_nonzero(a[:,-1]>=16))
   f={'file':rel(p),'action':action,'direction':direction,'frame':i,'width':im.width,'height':im.height,'mode':im.mode,'durationMs':ms,'pivot':[0.5,0.08],'anchorTopLeft':[512,942],'event':('attack' if action=='attack' and i==7 else 'cast' if action=='cast' and i==9 else None),'sha256':digest,'sourceRecord':rel(side) if side.exists() else None,'visualStatus':'pending full sequence review','technical':{'alphaExtrema':[int(a.min()),int(a.max())],'alpha16BBox':bbox,'alpha16EdgePixels':edge,'nonzeroEdgePixels':int(np.count_nonzero(a[0])+np.count_nonzero(a[-1])+np.count_nonzero(a[:,0])+np.count_nonzero(a[:,-1])),'transparentPixels':int(np.count_nonzero(a==0)),'issues':bad}}
   if review.get('status')=='reviewed-with-notes' and not review.get('blockingFindings') and reviewed_hashes.get(rel(p))==digest:
    f['visualStatus']='reviewed-with-notes'
    f['visualReview']={'file':rel(review_path),'sha256':review_sha,'jsonPointer':f'/frameSnapshot/{reviewed_indices[rel(p)]}','frameSHA256':digest}
   frames.append(f);group['frames'].append(f)
   if bad: issues.append({'file':rel(p),'issues':bad})
   if edge:issues.append({'file':rel(p),'issues':['alpha16 touches canvas'],'pixels':edge})
   bg=Image.new('RGBA',(256,282),'#263c38');bg.alpha_composite(im.resize((256,256),Image.Resampling.LANCZOS));draw=ImageDraw.Draw(bg);draw.text((8,259),f'{action} {direction} {i:02d}',fill='white');thumbs.append(bg.convert('RGB'))
   playback.append(im.resize((384,384),Image.Resampling.LANCZOS))
  if thumbs:
   cols=4;rows=math.ceil(len(thumbs)/cols);sheet=Image.new('RGB',(cols*256,rows*282),'#172b28')
   for n,t in enumerate(thumbs):sheet.paste(t,((n%cols)*256,(n//cols)*282))
   contact=preview/f'{action}-{direction}-contact.jpg'
   sheet.save(contact,quality=93)
   preview_records.append({'file':rel(contact),'sha256':sha(contact),'operation':'Scale to256 and composite ordered preview on dark background with labels; not game frames.','derivedFrom':[{'file':f['file'],'sha256':f['sha256']} for f in group['frames']]})
  if len(playback)==count:
   for speed,multiplier in [('1x',1),('025x',4)]:
    output=preview/f'{action}-{direction}-{speed}.png'
    playback[0].save(output,save_all=True,append_images=playback[1:],duration=ms*multiplier,loop=0,disposal=0,blend=0)
    preview_records.append({'file':rel(output),'sha256':sha(output),'format':'APNG','width':384,'height':384,'frameDurationMs':ms*multiplier,'operation':'Whole-canvas384 preview with original ordered AI frames, no motion interpolation.','derivedFrom':[{'file':f['file'],'sha256':f['sha256']} for f in group['frames']]})
  groups.append(group)
manifest={'schemaVersion':1,'pet':'08-zhufengli','name':'竹风狸','expectedFrameCount':68,'frameCount':len(frames),'complete':not missing,'coordinateConvention':'Top-left origin; pivot normalized from bottom-left. Same whole-native-canvas resize to 1024 in every action/direction; no per-frame crop or foot alignment.','clientIntegration':'not performed; asset-only','frames':frames}
manifest['technicalStatus']='pass' if not missing and not issues else 'incomplete-or-needs-review'
manifest['visualStatus']='reviewed-with-notes' if len(frames)==68 and all(f['visualStatus']=='reviewed-with-notes' for f in frames) else 'pending full sequence review'
manifest['visualReview']='qa/visual-review.json' if review else None
manifest['visualReviewSHA256']=review_sha
manifest['deliveryComplete']=manifest['complete'] and manifest['technicalStatus']=='pass' and manifest['visualStatus']=='reviewed-with-notes'
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(f["sha256"]+'  '+f['file'] for f in frames)+'\n',encoding='utf-8')
(qa/'technical.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expected':68,'found':len(frames),'missing':missing,'issues':issues,'duplicateCount':len(frames)-len(seen),'status':'pass' if not missing and not issues else 'incomplete-or-needs-review','scope':'Technical checks only, not art or client acceptance.'},ensure_ascii=False,indent=2),encoding='utf-8')
(preview/'data.js').write_text('window.GROUPS='+json.dumps(groups,ensure_ascii=False)+';',encoding='utf-8')
(preview/'sources.json').write_text(json.dumps(preview_records,ensure_ascii=False,indent=2),encoding='utf-8')
document_files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in {'.md','.json','.txt','.html','.js','.py'} and p.name!='DOCUMENT_SHA256SUMS.txt')
(ROOT/'DOCUMENT_SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+rel(p) for p in document_files)+'\n',encoding='utf-8')
print(json.dumps({'found':len(frames),'missing':len(missing),'issues':issues},ensure_ascii=False))
