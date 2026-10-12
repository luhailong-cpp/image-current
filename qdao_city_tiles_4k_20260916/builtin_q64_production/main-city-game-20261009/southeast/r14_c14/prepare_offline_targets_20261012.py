from pathlib import Path
from datetime import datetime,timezone
import sys,json,uuid,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';S=T.parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):p=Path(p);d={'path':str(p.resolve()),'sha256':sha(p)}
def asset(p):
 p=Path(p);a={'path':str(p.resolve()),'sha256':sha(p)}
 try:a['size']=list(Image.open(p).size)
 except OSError:pass
 return a
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False)
def png(p,im):
 with p.open('xb') as f:im.save(f,format='PNG')
auth=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json');assert rd(auth)['newArtworkGenerationAllowed']
cur=rd(T/'candidate/latest-assembly.json');freeze=rd(S/'migration-freeze-20261011.json');f={a['tile']:a for a in freeze['selectedCandidatePaths']}
for a in [cur['candidate'],cur['context'],f['r14_c13']['candidate'],f['r13_c14']['candidate']]:assert sha(a['path'])==a['sha256']
p0=rd(R/'west-lower-dark-structure-20261011T183323-f81535a7/preparation.json');refs=p0['references'][:3]
for a in refs:assert sha(a['path'])==a['sha256']
now=datetime.now(timezone.utc).isoformat();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
results=[]
for label in ['west-material-major','north-platform-boundary']:
 d=R/(label+'-'+stamp+'-'+uuid.uuid4().hex[:8]);d.mkdir();raw=Image.new('RGB',(1254,1254));mask=Image.new('L',(1254,1254),0)
 if label=='west-material-major':
  neighbor=f['r14_c13']['candidate'];nc=[3456,2000,4096,3254];cc=[0,2000,614,3254];raw.paste(Image.open(neighbor['path']).convert('RGB').crop(nc),(0,0));raw.paste(Image.open(cur['candidate']['path']).convert('RGB').crop(cc),(640,0))
  box=[640,400,920,1100];ImageDraw.Draw(mask).rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=255)
  a=np.array(raw);dark=(a.astype(np.uint16).sum(axis=2)<360);protect=Image.fromarray(dark.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(35));ma=np.array(mask);ma[np.array(protect)>0]=0;mask=Image.fromarray(ma)
  prompt="""Use case: precise-object-edit. Edit ONLY the LAST image: exact native1254x1254 crop of existing Q-style Taoist game-map grey stone pavement. First3 images provide approved illustration/material style only. Fill only the MAGENTA stone-surface pixels. All visible nonmagenta stone, shadows, outlines and grooves are immutable. The LEFT640px are the exact already-made west neighbor; its cool grey stone tone, surface texture and soft tree shadow are the matching reference. The marked part on the right currently has a warmer, brighter vertical tile boundary: remove that artificial vertical color division by continuing the left stone/shadow naturally into the magenta area. Smoothly match the visible fixed right, top and bottom stone too. Existing dark grout and white bevels remain visibly preserved through the hole: keep every groove in the exact same pixels, width, angle and topology. Do not generate new cracks or grooves, simplify grain, move shadows, smooth away crisp illustrated texture, or add any objects. No blue bands, text, new red paper, zoom, pan or resizing. Return one opaque native1254x1254PNG at identical framing, all magenta removed. Final use is only the selected right-side stone surface; the left neighbor never changes."""
  meta={'direction':'west','neighborPlacement':[0,0,640,1254],'currentPlacement':[640,0,1254,1254],'targetSeam':{'axis':'x','value':640},'rectanglesBeforeProtection':[box],'maskRule':'Mask right x640..919,localy400..1099 (corey2400..3099), except RGBsum<360 grout pixels expanded by35px square MaxFilter. Fixed grout/bevel protection guides only, not final paint.','protectionRule':{'rgbSumBelow':360,'pillowMaxFilterSize':35},'sourceCoreProblemY':[2540,2880],'desiredFinalApplication':'Right side only; exact saved mask, with inner perimeter feather that does not change any protected grout pixel; no alpha on neighbor.'}
 else:
  neighbor=f['r13_c14']['candidate'];nc=[2842,3456,4096,4096];cc=[2842,0,4096,614];raw.paste(Image.open(neighbor['path']).convert('RGB').crop(nc),(0,0));raw.paste(Image.open(cur['candidate']['path']).convert('RGB').crop(cc),(0,640))
  box=[0,640,1254,1020];ImageDraw.Draw(mask).rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=255)
  prompt="""Use case: precise-object-edit. Edit ONLY the LAST exact1254x1254 crop of our existing Q-style game-map wooden platform/porch structure. First3 images are style references, not objects to add. Fill ONLY the solid MAGENTA lower band. The UPPER640px are the immutable real core of the north neighboring tile. Continue its existing massive partial wooden pillar, long platform ledges and diagonal sunlight/shadow downward into the missing band, matching the exact top boundary geometry, wood grain, bright bevels and brown recesses. Match the existing visible lower part too. Repair the horizontal cut in the long wooden ledge and broad shadow at y640: all edges and shadows must flow continuously, with no offset ledge, sudden thickness change, dangling black line, horizontal light bar or rectangular shadow truncation. Keep every existing giant local structure at the same crop scale and angle; never complete it into a whole building or add legs, rails, steps, posts or decorations. Do not add lanterns, parasols, foliage, signs, blue road bands, text or UI. Preserve all nonmagenta pixels and original framing; no zoom, pan or resize. Opaque native1254x1254PNG, all magenta removed. Final selected artwork affects only the current tile below y640; north neighbor is immutable."""
  meta={'direction':'north','neighborPlacement':[0,0,1254,640],'currentPlacement':[0,640,1254,1254],'targetSeam':{'axis':'y','value':640},'rectanglesBeforeProtection':[box],'maskRule':'Single magenta rectangle local x0..1253,y640..1019, corresponding corex2842..4095,y0..379. All source pixels outside hole remain unchanged.','sourceCoreProblemBox':[2842,0,4096,380],'desiredFinalApplication':'Current lower614 side only; save actual native1254 without scaling. Use mask and a current-side transition, never neighbor alpha. Check left crop boundary to adjacent existing column and lower transition.'}
 png(d/'source-1254.png',raw);png(d/'edit-mask.png',mask);a=np.array(raw);a[np.array(mask)>0]=[255,0,255];png(d/'target-1254.png',Image.fromarray(a))
 (d/'prompt.txt').write_text(prompt,encoding='utf-8');rr=refs+[{**asset(d/'target-1254.png'),'role':'LAST exact native edit target with documented magenta guide mask'}]
 request={'prompt':prompt,'referenced_image_paths':[a['path'] for a in rr],'transparent_background':False};write(d/'request.json',request)
 prep={'schemaVersion':1,'tile':'r14_c14','version':d.name,'preparedAt':now,'status':'prepared_offline_not_generated','networkCallMade':False,'authority':asset(auth),'sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'neighborCore':neighbor,'neighborCoreCrop':nc,'currentCoreCrop':cc,'rawTarget':asset(d/'source-1254.png'),'guide':asset(d/'target-1254.png'),'editMask':asset(d/'edit-mask.png'),'guideFillRGB':[255,0,255],'references':rr,'request':asset(d/'request.json'),'prompt':asset(d/'prompt.txt'),'actualModel':None,'actualQuality':None,'resized':False,'formalAccepted':False,'reservedCorner':[0,0,630,630],**meta}
 write(d/'preparation.json',prep);results.append({'version':d.name,'preparation':asset(d/'preparation.json'),'request':asset(d/'request.json'),'target':asset(d/'target-1254.png'),'raw':asset(d/'source-1254.png'),'sourceCandidate':cur['candidate'],'problem':meta.get('sourceCoreProblemY',meta.get('sourceCoreProblemBox'))})
out=T/'review/resume-offline-20261012/prepared-imagegen-handoff.json';write(out,{'preparedAt':now,'networkCallMade':False,'targets':results,'rootSteps':['View all referenced local images and raw source before imagegen.','Pass exact request.json object to builtin imagegen. Do not use API or resize.','Save real output receipt and original path/hash; ingest as native1254 with actualModel/Quality null.','Do not change guide or preparation; use new version for changes.','No automatic formal acceptance; target selection masks preserve fixed neighbor andNW630corner.'],'candidateUnchanged':True})
print(json.dumps({'handoff':asset(out),'targets':results},indent=2))

