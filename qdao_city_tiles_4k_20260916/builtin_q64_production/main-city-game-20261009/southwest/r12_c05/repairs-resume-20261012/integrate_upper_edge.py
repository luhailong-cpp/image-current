from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,datetime
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05')
D=B/'repairs-resume-20261012';T=D/'upper-cream-step-local-v02';O=D/'integrated-local-v08';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def desc(p):return {'file':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size)}
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
A=json.loads((B/'repairs-audit-line-20261011/integrated-local-v06/assembly.json').read_text());src=Path(A['contextOutput']['file'])
orig=Image.open(T/'input.png').convert('RGB');native=Image.open(T/'native.png').convert('RGB');base=Image.open(src).convert('RGB')
assert orig.size==native.size==(1254,1254) and sha(src)=='7217476a67e3f26ace57938baf737cc3e028f853a964287882585659b3cc76e2'
# QA-selected actual missing boundary corridor. The mask is a copy instruction, not synthetic final art.
poly=[(674,222),(980,3),(980,70),(674,283)]
mask=Image.new('L',(1254,1254),0);ImageDraw.Draw(mask).polygon(poly,fill=255)
# Two one-pixel erosions bound the only alpha transition to two native pixels.
e1=mask.filter(ImageFilter.MinFilter(3));e2=e1.filter(ImageFilter.MinFilter(3))
ma=np.asarray(mask);a=np.where(np.asarray(e2)>0,255,np.where(np.asarray(e1)>0,170,np.where(ma>0,85,0))).astype(np.uint8)
applied=Image.composite(native,orig,Image.fromarray(a));applied.save(T/'applied-crop.png');mask.save(T/'copy-mask.png');Image.fromarray(a).save(T/'alpha.png')
origarr=np.asarray(orig);app=np.asarray(applied);changed=np.any(app!=origarr,axis=2);outside=int((changed&(ma==0)).sum());assert outside==0
result=base.copy();result.paste(applied,(2560,2160));gm=np.zeros((4326,4326),bool);gm[2160:3414,2560:3814]=ma>0
outsidefull=int((np.any(np.asarray(result)!=np.asarray(base),axis=2)&~gm).sum());assert outsidefull==0
result.save(O/'r12_c05.candidate.context.png');result.crop((115,115,4211,4211)).save(O/'r12_c05.candidate.png');result.resize((1082,1082)).save(O/'context-preview-resized.png')
for name,im in [('original',orig),('applied',applied),('native',native)]:
 im.crop((620,0,1040,330)).save(T/(name+'-ROI-native-QA.png'))
result.crop((3007,2163,3367,3187)).save(O/'V3-3-native-QA.png');result.crop((3187,1983,4211,2343)).save(O/'H2-4-native-QA.png')
proposal={'attempt':'upper-cream-step-local-v02','input':desc(T/'input.png'),'native':desc(T/'native.png'),'request':desc(T/'request.json') if False else {'file':str(T/'request.json'),'sha256':sha(T/'request.json')},'receipt':{'file':str(T/'receipt.json'),'sha256':sha(T/'receipt.json')},'sourceContext':desc(src),'cropContextBox':[2560,2160,3814,3414],'copyMask':desc(T/'copy-mask.png'),'alpha':desc(T/'alpha.png'),'appliedCrop':desc(T/'applied-crop.png'),'maskPolygonLocal':poly,'maskRule':'copy generated actual edge corridor only; two one-pixel erosions; no geometry painted by code','maximumFeatherPixels':2,'sourceResampling':False,'outsideMaskChangedPixels':outside,'changedPixels':int(changed.sum()),'roofOutsideMask':True,'actualModel':None,'actualQuality':None,'formalAccepted':False,'internalAccepted':False,'localVisualAssessment':'Whole missing gray/cream thin-edge segment restored using generated pixels; native mask perimeter and 24 internal seams pending final review.'}
write(T/'proposal.json',proposal)
write(O/'assembly.json',{'sourceAssembly':str(B/'repairs-audit-line-20261011/integrated-local-v06/assembly.json'),'appliedProposals':[str(T/'proposal.json')],'contextOutput':desc(O/'r12_c05.candidate.context.png'),'output':desc(O/'r12_c05.candidate.png'),'outsideUnionChangedPixels':outsidefull,'coreEqualsContextCrop':True,'maximumFeatherPixels':2,'sourceResampling':False,'formalAccepted':False,'internalAccepted':False})
write(D/'lane-state.json',{'tile':'r12_c05','status':'active_local_repairs','candidateAssembly':str(O/'assembly.json'),'baselineAssembly':str(B/'repairs-audit-line-20261011/integrated-local-v06/assembly.json'),'successfulBuiltinCalls':6,'rejectedAttempts':['V1-row1-quiet-v01','blue-band-east-join-v01','blue-band-east-join-v02','blue-band-east-join-v03','upper-cream-step-small-v01'],'openIssues':['Final review of upper cream step repair mask boundaries','large blue/cream notch and blue field tonal seam','24 internal seam review','quiet material variation across patches','roof small color discontinuity'],'formalAccepted':False,'internalAccepted':False,'updatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualModel':None,'actualQuality':None})
print(json.dumps({'assembly':str(O/'assembly.json'),'output':desc(O/'r12_c05.candidate.png'),'context':desc(O/'r12_c05.candidate.context.png'),'outsideMask':outside,'outsideUnion':outsidefull,'changedPixels':int(changed.sum())}))
