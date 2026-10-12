"""Build manifest, technical checks and visual review artifacts from real frames."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, math
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SPECS={'hit':(6,40),'attack':(12,30),'cast':(16,45)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,obj): (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
out=ROOT/'preview'; out.mkdir(exist_ok=True)
frames=[]; errors=[]; sheets=[]; groups=[]; hashes={}; pixel_hashes={}
for action,(count,ms) in SPECS.items():
 for direction in ['E','W']:
  group=[]; thumbs=[]; animation=[]
  for n in range(1,count+1):
   rel=f'runtime/{action}/{direction}/{n:02}.png'; p=ROOT/rel
   if not p.exists(): errors.append({'file':rel,'error':'missing frame'}); continue
   im=Image.open(p); im.load(); h=sha(p)
   if im.size!=(1024,1024) or im.mode!='RGBA': errors.append({'file':rel,'error':'size/mode','size':im.size,'mode':im.mode}); continue
   alpha=im.getchannel('A'); extrema=alpha.getextrema(); visible=alpha.point(lambda a:255 if a>16 else 0).getbbox()
   if extrema!=(0,255): errors.append({'file':rel,'error':'unexpected alpha range','range':extrema})
   if not visible or visible[0]<=0 or visible[1]<=0 or visible[2]>=1024 or visible[3]>=1024: errors.append({'file':rel,'error':'visible contour touches canvas','visibleBbox':visible})
   if h in hashes: errors.append({'file':rel,'error':'duplicate bytes','matches':hashes[h]})
   hashes[h]=rel
   pixel_sha=hashlib.sha256(im.tobytes()).hexdigest()
   if pixel_sha in pixel_hashes:errors.append({'file':rel,'error':'duplicate RGBA pixels','matches':pixel_hashes[pixel_sha]})
   pixel_hashes[pixel_sha]=rel
   ownrec=Path(str(p)+'.generation.json')
   if ownrec.exists(): source=str(ownrec.relative_to(ROOT)).replace('\\','/')
   else:
    exact=ROOT/'records'/f'{action}-{direction}-{n:02}.generation.json'
    candidates=[exact] if exact.exists() else [x for x in (ROOT/'records').glob(f'{action}-{direction}-{n:02}*.generation.json') if 'candidate' not in x.name]
    source=str(candidates[0].relative_to(ROOT)).replace('\\','/') if candidates else None
   if source is None: errors.append({'file':rel,'error':'missing source record'})
   record={'file':rel,'action':action,'direction':direction,'frame':n,'width':1024,'height':1024,'durationMs':ms,'pivot':[0.5,0.08],'anchorTopLeftPx':[512,942],'event':('impact' if action=='attack' and n==7 else 'release' if action=='cast' and n==10 else None),'sha256':h,'alphaExtrema':extrema,'visibleBboxAlphaGT16':visible,'sourceRecord':source,'visualStatus':'pending-sequence-review'}
   record['pixelSHA256']=pixel_sha
   frames.append(record); group.append(record); animation.append(im.resize((512,512),Image.Resampling.LANCZOS))
   tile=Image.new('RGB',(256,284),(231,230,214)); tile.paste(im.resize((256,256),Image.Resampling.LANCZOS),(0,0),im.resize((256,256),Image.Resampling.LANCZOS)); ImageDraw.Draw(tile).text((8,261),f'{action} {direction} {n:02} / {count}  {ms} ms',fill=(20,55,43)); thumbs.append(tile)
  groups.append({'action':action,'direction':direction,'expectedFrames':count,'durationMs':ms,'frames':group})
  if thumbs:
   cols=3 if action=='hit' else 4; sheet=Image.new('RGB',(cols*256,math.ceil(len(thumbs)/cols)*284),(210,218,206))
   for j,tile in enumerate(thumbs): sheet.paste(tile,((j%cols)*256,(j//cols)*284))
   name=f'{action}-{direction}-frames.jpg'; sheet.save(out/name,quality=94); sheets.append('preview/'+name)
   if len(animation)==count:
    for suffix,factor in [('normal',1),('slow',4)]:
     animation[0].save(out/f'{action}-{direction}-{suffix}.webp',save_all=True,append_images=animation[1:],duration=ms*factor,loop=0,lossless=True)
   page=(out/'index.html').read_text(encoding='utf-8').replace('<html lang="zh-CN">',f'<html lang="zh-CN" data-group="{action}-{direction}">')
   (out/f'{action}-{direction}.html').write_text(page,encoding='utf-8')
calibration_states=[]
for f in frames:
 g=json.loads((ROOT/f['sourceRecord']).read_text(encoding='utf-8')) if f['sourceRecord'] else {}
 c=g.get('finalDirectionCalibration')
 calibration_states.append(bool(c and c.get('translationPx')==[0,{'E':-15,'W':-4}[f['direction']]] and c.get('outputSHA256')==f['sha256'] and g.get('sha256')==f['sha256']))
calibrated=len(frames)==68 and all(calibration_states)
if (any(calibration_states) or (ROOT/'records/final-direction-calibration.json').exists()) and not calibrated:errors.append({'error':'partial or stale direction calibration; all 68 source records must match pixels'})
review_path=ROOT/'records/visual-review.json'
review=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
reviewed=(review.get('passed') is True and len(frames)==68 and not errors and review.get('frameSHA256')=={f['file']:f['sha256'] for f in frames})
if reviewed:
 for f in frames:f['visualStatus']='reviewed';f['visualReviewRecord']='records/visual-review.json'
manifest={'character':'符小虎','slug':'legacy-fu-xiao-hu','generatedAt':datetime.now(timezone.utc).isoformat(),'expectedFrameCount':68,'actualFrameCount':len(frames),'status':'in-progress' if errors or len(frames)!=68 else 'technical-check-passed-visual-review-pending','directions':{'E':'three-quarter front facing lower right','W':'true three-quarter rear facing upper left'},'coordinateSystem':'exported 1024 canvas; no per-frame alignment','transform':{'E':{'resize':[1024,1024],'translationPx':[0,-15] if calibrated else [0,0]},'W':{'resize':[1024,1024],'translationPx':[0,-4] if calibrated else [0,0]}},'clientIntegration':'not-performed','frames':frames}
if reviewed:manifest['status']='complete-assets-reviewed';manifest['visualReviewRecord']='records/visual-review.json'
dump('manifest.json',manifest)
dump('validation.json',{'checkedAt':datetime.now(timezone.utc).isoformat(),'frameCount':len(frames),'expectedFrameCount':68,'technicalPassed':not errors and len(frames)==68,'errors':errors,'duplicatesChecked':'SHA256 exact bytes AND decoded RGBA pixels; visual similarity reviewed separately','visibleContourThreshold':16,'sourceRecords':'per-frame records present check; full reference audit in records/source-audit.json','artReview':'reviewed' if reviewed else 'pending','clientIntegration':'not-performed'})
(out/'data.js').write_text('window.COMBAT_DATA = '+json.dumps(groups,ensure_ascii=False)+';',encoding='utf-8')
print(json.dumps({'frames':len(frames),'errors':len(errors),'sheets':sheets}))
