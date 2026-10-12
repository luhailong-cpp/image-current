"""Read-only pixel checks and text review inventory for W attack01-06 repair."""
from pathlib import Path
from collections import deque
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def metrics(path):
    im=Image.open(path); a=np.array(im); mask=(a[:,:,3]>150)&(a[:,:,:3].max(axis=2)<185)
    mask[:1010]=False;mask[:,:510]=False;mask[:,780:]=False
    components=[]
    for y,x in zip(*np.where(mask)):
        if not mask[y,x]:continue
        q=deque([(int(y),int(x))]);mask[y,x]=False;pts=[]
        while q:
            yy,xx=q.popleft();pts.append((xx,yy))
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny,nx=yy+dy,xx+dx
                if 0<=ny<a.shape[0] and 0<=nx<a.shape[1] and mask[ny,nx]:mask[ny,nx]=False;q.append((ny,nx))
        if len(pts)>200:
            z=np.array(pts); components.append({'area':len(pts),'center':[round(float(v),2) for v in z.mean(axis=0)],'bounds':[int(v) for v in [z[:,0].min(),z[:,1].min(),z[:,0].max()+1,z[:,1].max()+1]]})
    components=sorted(sorted(components,key=lambda v:-v['area'])[:2],key=lambda v:v['center'][0])
    edges={s:{'maxAlpha':int(v.max()),'pixelsAbove64':int((v>64).sum())} for s,v in zip(('top','bottom','left','right'),(a[0,:,3],a[-1,:,3],a[:,0,3],a[:,-1,3]))}
    return {'size':list(im.size),'mode':im.mode,'alphaRange':list(im.getchannel('A').getextrema()),'strongEdgePixels':edges,'shoeDarkComponents':components}
baseline=ROOT/'repair-inputs/baseline-W.png'
review={'checkedAt':datetime.now(timezone.utc).isoformat(),'scope':'attack/W01-06','method':'Author actually viewed core E/W/style references, each edit target, every native result and every final exported PNG. Static sequential pose comparison plus read-only native alpha-edge and dark-shoe component measurements. No continuous playback or client approval claimed.','status':'static-reviewed-pending-root-sequence-verification','anatomy':'Each reviewed output remains true rear three-quarter W with visible back hair, two hands (anatomical left supports crescent harp; right plucks), two rear-facing staggered shoes, no wings/tail.','correction':'AI local lower-body edits remove original wide-foot stance while retaining frame-specific plucking poses. Frame03 required an additional real AI ribbon-edge correction. No code-created pose, mirror, interpolation or per-frame re-alignment used.','measurementLimitation':'Shoe centers are auxiliary dark connected-component centroids with y>=1010, 510<=x<780, maxRGB<185, alpha>150 in native1254 coordinates; not literal anatomical joints or foot-ground contacts. Small drawing deformation remains and requires sequence review.','baseline':{'path':str(baseline),'sha256':sha(baseline),'metrics':metrics(baseline)},'frames':[],'nativeSources':[]}
for i in range(1,7):
    rec=ROOT/'records/attack-W'/f'{i:02}.generation.json';r=load(rec)
    if 'guardfix-20261008' not in r['prompt']:continue
    native=Path(r['derivedFrom']['path']);out=ROOT/r['file']
    review['frames'].append({'frame':i,'file':r['file'],'sha256':sha(out),'record':rec.relative_to(ROOT).as_posix(),'native':str(native),'nativeSha256':sha(native),'metrics':metrics(native),'exportMode':Image.open(out).mode,'exportSize':list(Image.open(out).size),'exportSHAAgrees':sha(out)==r['sha256'],'observed':'Native and final export viewed; narrowed rear shoes, left harp support and right plucking arm intact. Frame-to-frame plucking hand differences retained; exact playback pending.'})
    for p in sorted((ROOT/'records/attack-W').glob(f'{i:02}.guardfix-20261008*.generation.json')):
        c=load(p);selected=Path(c['file'])==native
        c['disposition']='selected current final export' if selected else ('superseded by later AI ribbon-edge correction' if i==3 else 'superseded by later AI shoe-position precision correction')
        if i==6 and not selected:c['disposition']='rejected: upper torso drift and diminished extended follow-through; retained initial corrected frame06'
        c['currentRecord']=rec.relative_to(ROOT).as_posix();save(p,c)
        review['nativeSources'].append({'path':c['file'],'sha256':c['sha256'],'record':p.relative_to(ROOT).as_posix(),'selected':selected,'eligibleForRootCleanupAfterFinalVerification':True})
review['completed']=len(review['frames']);review['expected']=6
review['distinctFinalSHA']=len({f['sha256'] for f in review['frames']})==len(review['frames'])
review['noCodeCreatedPose']=True
review['residualStaticVariation']='Frame04 lower shoe retains about18 native pixels (about14 export pixels) horizontal dark-body-center difference from baseline, with upper shoe near fixed and no swapped foot. Frame06 retains about14 native pixels lower-shoe x/y drawing variation. This is disclosed for root sequence review; not called zero-slip or dynamic approval.'
review['exportContract']={'canvas':[1024,1024],'fixedWholeCanvasResize':[960,960],'fixedOffset':[32,16],'perFrameAlignment':False}
observations={1:'Starting curled right fingers near central strings; narrowed guard shoe positions match baseline closely.',2:'Right wrist/fingers visibly lifted for preparation; supporting palm remains under the harp.',3:'Right fingers bend inward near strings; original ribbon-edge clipping repaired through a second AI edit.',4:'Right wrist reaches toward strings with bent fingers at release, retains support hand and full rear silhouette.',5:'Right wrist lowers into the stroke; rear feet show small natural drawing variation without wide lateral stance.',6:'Extended right fingers and wrist show follow-through; left hand continues to support the same harp.'}
for f in review['frames']:f['poseObservation']=observations[f['frame']]
review['nativeEdgeCheckPassed']=all(not e['pixelsAbove64'] for f in review['frames'] for e in f['metrics']['strongEdgePixels'].values())
save(ROOT/'records/attack-W/guardfix-early-review-20261008.json',review)
save(ROOT/'records/attack-W/guardfix-early-native-inventory-20261008.json',{'scope':'attack/W01-06 own generated sources only','deleteOnlyAfterFinalVerification':True,'items':review['nativeSources']})
print(json.dumps({'completed':review['completed'],'expected':6,'nativeEdgeCheckPassed':review['nativeEdgeCheckPassed'],'feet':[{'frame':f['frame'],'components':f['metrics']['shoeDarkComponents']} for f in review['frames']],'baseline':review['baseline']['metrics']['shoeDarkComponents']},ensure_ascii=False))
