from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,datetime
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05');D=B/'repairs-resume-20261012';T=D/'H3-3-blue-edge-gap-v01';O=D/'integrated-local-v11';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def desc(p):return {'file':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size)}
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
src=D/'integrated-local-v10/r12_c05.candidate.context.png';assert sha(src)=='29f28eccdf3adee08173b25eeb322e9946285140cb1f032a198ebd4765e9f57c'
base=Image.open(src).convert('RGB');orig=Image.open(T/'input.png').convert('RGB');native=Image.open(T/'native.png').convert('RGB');assert orig.size==native.size==(1254,1254)
poly=[(621,633),(665,605),(671,630),(627,660)]
mask=Image.new('L',orig.size,0);ImageDraw.Draw(mask).polygon(poly,fill=255)
e1=mask.filter(ImageFilter.MinFilter(3));e2=e1.filter(ImageFilter.MinFilter(3));ma=np.array(mask)
a=np.where(np.array(e2)>0,255,np.where(np.array(e1)>0,170,np.where(ma>0,85,0))).astype('uint8')
app=Image.composite(native,orig,Image.fromarray(a));app.save(T/'applied-crop.png');mask.save(T/'copy-mask.png');Image.fromarray(a).save(T/'alpha.png')
change=np.any(np.array(app)!=np.array(orig),axis=2);outside=int((change&(ma==0)).sum());assert outside==0
res=base.copy();res.paste(app,(1779,2700));gm=np.zeros((4326,4326),bool);gm[2700:3954,1779:3033]=ma>0
outsideglobal=int((np.any(np.array(res)!=np.array(base),axis=2)&~gm).sum());assert outsideglobal==0
res.save(O/'r12_c05.candidate.context.png');res.crop((115,115,4211,4211)).save(O/'r12_c05.candidate.png');res.resize((1082,1082)).save(O/'context-preview-resized.png')
for n,im in [('original',orig),('native',native),('applied',app)]:im.crop((570,575,710,700)).save(T/(n+'-ROI-native-QA.png'))
res.crop((2163,3007,3187,3367)).save(O/'H3-3-native-QA.png');res.crop((1983,3187,2343,4211)).save(O/'V2-4-native-QA.png')
proposal={'attempt':'H3-3-blue-edge-gap-v01','input':desc(T/'input.png'),'native':desc(T/'native.png'),'request':ref(T/'request.json'),'receipt':ref(T/'receipt.json'),'sourceContext':desc(src),'cropContextBox':[1779,2700,3033,3954],'copyMask':desc(T/'copy-mask.png'),'alpha':desc(T/'alpha.png'),'appliedCrop':desc(T/'applied-crop.png'),'maskPolygonLocal':poly,'maskRule':'Copy only generated actual tiny missing-edge neighborhood; two one-pixel erosions constrain alpha transition to2 native pixels. No resampling, warping, recoloring or code-painted final image.','maximumFeatherPixels':2,'sourceResampling':False,'outsideMaskChangedPixels':outside,'changedPixels':int(change.sum()),'formalAccepted':False,'internalAccepted':False,'actualModel':None,'actualQuality':None}
write(T/'proposal.json',proposal)
write(T/'disposition.json',{'native':desc(T/'native.png'),'explicitlyRejected':False,'reason':'Native original retained. Only reviewed tiny gap polygon extracted into v11; full generated crop is not applied, because unrelated line tone and quiet material must remain original. Candidate provisional, visual review pending.','actualModel':None,'actualQuality':None})
write(O/'assembly.json',{'sourceAssembly':str(D/'integrated-local-v10/assembly.json'),'appliedProposals':[str(T/'proposal.json')],'contextOutput':desc(O/'r12_c05.candidate.context.png'),'output':desc(O/'r12_c05.candidate.png'),'outsideUnionChangedPixels':outsideglobal,'coreEqualsContextCrop':True,'maximumFeatherPixels':2,'sourceResampling':False,'formalAccepted':False,'internalAccepted':False})
lane=json.loads((D/'lane-state.json').read_text());lane.update({'candidateAssembly':str(O/'assembly.json'),'currentCandidateAssembly':str(O/'assembly.json'),'successfulBuiltinCalls':9,'failedBuiltinCalls':1,'reviewedNativeInternalSeams':24,'rejectedAttempts':['V1-row1-quiet-v01','blue-band-east-join-v01','blue-band-east-join-v02','blue-band-east-join-v03','upper-cream-step-small-v01','blue-coherent-left-v04','blue-direct-control-left-v05'],'openIssues':['v11 tiny-edge polygon native perimeter review','upper gray/cream restoration left cap kink about20px','large blue/cream notch and blue field tonal seam','small grout gap/cap offsets','quiet stone material variation across patches','roof small color discontinuity'],'updatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()});write(D/'lane-state.json',lane)
print(json.dumps({'assembly':str(O/'assembly.json'),'output':desc(O/'r12_c05.candidate.png'),'context':desc(O/'r12_c05.candidate.context.png'),'outsideMask':outside,'outsideUnion':outsideglobal,'changedPixels':int(change.sum())}))
