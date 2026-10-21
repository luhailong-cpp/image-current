"""Native tile-local repair preparation, byte ingest and deterministic uint32 composition."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime,sys,shutil
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,j):
 p=Path(p);assert not p.exists(),str(p);p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def png(p,im):assert not Path(p).exists();im.save(p)
cmd,key=sys.argv[1:3];R=T/'repairs'/key
if cmd=='prepare':
 R.mkdir(parents=True,exist_ok=False)
 base=read(T/'candidate/latest-assembly.json');B=Image.open(base['candidate']['path']).convert('RGB')
 refs=read(T/'records/p01_01_v20261013T162414_105e59f2.reference-evidence.json')[:3]
 if key.startswith('south-post'):
  box=[1520,2842,2774,4096];target=B.crop(box);region=[1880,3760,2370,4096]
  goal='Remove ONLY the extra narrow mini-column immediately attached to the RIGHT side of the existing broad front-wall stone post near the bottom. Keep ONE broad square stone post, with its existing single wide cap and full shaft. Its right boundary is around target x650. The unwanted narrow extra post is around target x650..770, y960..1254. Replace that extra post with the continuation of the normal horizontal lower wall and its flat cap from the right, joined cleanly into the right side of the original broad post. Retain the original broad post at target x380..650 and its cap at y~990; do not remove that broad post. The normal low wall cap on the right stays at y~1140 and is connected to the broad post. Preserve the paving above, all rear wall, existing shadows, scale and framing. No new column, duplicate cap, steps, finials, ornament, moss or foliage.'
  if 'v2' in key:
   region=[2140,3830,2340,4096]
   goal='Remove ONLY the unwanted narrow extra stone column at target x650..772, y1015..1254, immediately to the RIGHT of the existing broad front-wall post. Keep the broad post at x380..655 and its cap at y1030..1165 exactly unchanged. Keep the original normal wall to the RIGHT of x780 exactly unchanged: its TOP edge is at y1161, NOT y1140, and its front-face edge is at y1240. Replace the unwanted narrow column footprint above y1161 with the same pale paved floor, continuing existing slab texture. From y1161 down, extend that original right-hand normal wall cap leftwards until it joins the broad post right edge x655. Do not level or raise the entire right wall to the left wall height: the broad post conceals the small left/right cap-height difference. No extra column, no cap fragment, no step at x780, no new grout in empty paving. Preserve all pixels outside x640..790,y1000..1254, including complete original top/rear wall, broad post, old left wall, and right wall.'
 elif key.startswith('west-grout'):
  box=[-627,1900,627,3154];west=read(T.parent/'r15_c14/candidate/latest-assembly.json');N=Image.open(west['candidate']['path']).convert('RGB');target=Image.new('RGB',(1254,1254));target.paste(N.crop((3469,1900,4096,3154)),(0,0));target.paste(B.crop((0,1900,627,3154)),(627,0));region=[0,2230,200,2810];base['neighbor']=west['candidate']
  goal='Fix ONLY the NEW CHILD side to the RIGHT of vertical x627. The entire LEFT x0..627 is the immutable r15_c14 neighbor core: preserve it pixel-identically. At target x627,y~504, a short horizontal stone groove starts abruptly at the vertical tile boundary and runs right to x~712; the same old slab on the left has no groove. Remove that isolated groove only in the child side and continue the broad stone slab seamlessly from left. Maintain every true long slab edge and the vertical grout at x~712; do not draw a new horizontal line across immutable left. Also match the existing fine pale/blue-grey stone texture continuously near the boundary without moving, zooming, blurring, or shifting the paving. Keep other blue inset/slab structure and shadows. Do not add scraps, objects or plants.'
 else:raise ValueError(key)
 assert target.size==(1254,1254)
 png(R/'target-native-1254.png',target)
 a=np.zeros((1254,1254),dtype=np.uint8);x0,y0,x1,y1=region;xx0,yy0,xx1,yy1=x0-box[0],y0-box[1],x1-box[0],y1-box[1];a[yy0:yy1,xx0:xx1]=255
 png(R/'edit-mask-1254.png',Image.fromarray(a))
 prompt='Use case: precise-object-edit. ONE real native opaque 1254x1254 output. Inputs1/2/3 style references only, input4 LAST image is sole actual edit target. Fixed giant map detail crop, not whole scene. '+goal+' Match the target native material and clean Taoist chibi painted finish. Uniform sharp detail, no bokeh/blur. Keep canvas, camera, perspective, dimensions and every unaffected object exactly fixed. Do not redraw whole scene or import reference architecture. No text, UI, watermark. Output exactly1254x1254 without resizing.'
 (R/'prompt.txt').write_text(prompt,encoding='utf-8')
 request={'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs]+[str(R/'target-native-1254.png')],'transparent_background':False}
 write(R/'request.json',request)
 write(R/'preparation.json',{'tile':T.name,'repair':key,'preparedAt':now(),'base':base,'cropBoxInCoreCoordinates':box,'requestedPasteRegion':region,'references':refs,'target':ref(R/'target-native-1254.png'),'mask':ref(R/'edit-mask-1254.png'),'prompt':ref(R/'prompt.txt'),'request':ref(R/'request.json'),'tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'resized':False})
 print(json.dumps({'request':str(R/'request.json'),'target':str(R/'target-native-1254.png')}))
elif cmd=='ingest':
 source=Path(sys.argv[3]);I=Image.open(source);assert I.format=='PNG' and I.size==(1254,1254)
 assert not (R/'native.png').exists();shutil.copyfile(source,R/'native.png')
 write(R/'receipt.json',{'tool':'image_gen.imagegen','route':'builtin','status':'succeeded_pending_visual_qa','generatedAt':now(),'originalOutputPath':str(source),'sourceSha256':sha(source),'saved':ref(R/'native.png'),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False})
 print(json.dumps(ref(R/'native.png')))
elif cmd=='compose':
 P=read(R/'preparation.json');base=Path(sys.argv[3]) if len(sys.argv)>3 else Path(P['base']['candidate']['path'])
 B=Image.open(base).convert('RGB');N=Image.open(R/'native.png').convert('RGB');bx,by,_,_=P['cropBoxInCoreCoordinates'];x0,y0,x1,y1=P['requestedPasteRegion'];crop=[x0-bx,y0-by,x1-bx,y1-by]
 w,h=x1-x0,y1-y0;alpha=np.full((h,w),255,dtype=np.uint8)
 for i in range(2):
  v=round((i+1)*255/3)
  if x0>0:alpha[:,i]=np.minimum(alpha[:,i],v)
  if x1<4096:alpha[:,-i-1]=np.minimum(alpha[:,-i-1],v)
  if y0>0:alpha[i,:]=np.minimum(alpha[i,:],v)
  if y1<4096:alpha[-i-1,:]=np.minimum(alpha[-i-1,:],v)
 old=np.asarray(B.crop((x0,y0,x1,y1))).astype(np.uint32);new=np.asarray(N.crop(crop)).astype(np.uint32);A=alpha.astype(np.uint32)[:,:,None]
 out=((new*A+old*(255-A)+127)//255).astype(np.uint8);B.paste(Image.fromarray(out),(x0,y0))
 dest=T/'candidate'/('r15_c15-4k-'+key+'.png');png(dest,B);png(R/'alpha.png',Image.fromarray(alpha));png(R/'after-native-1254.png',B.crop((max(0,bx),by,max(0,bx)+1254,by+1254)) if bx>=0 else B.crop((0,by,1254,by+1254)))
 contextPath=P['base']['context']['path'];C=Image.open(contextPath).convert('RGB');C.paste(B,(115,115));context=T/'candidate'/('r15_c15-context-4326-'+key+'.png');png(context,C)
 write(R/'composition.json',{'tile':T.name,'repair':key,'base':ref(base),'native':ref(R/'native.png'),'receipt':ref(R/'receipt.json'),'preparation':ref(R/'preparation.json'),'nativeCrop':crop,'tilePlacement':[x0,y0,x1,y1],'alpha':ref(R/'alpha.png'),'formula':'uint8((new_uint32*alpha_uint32 + old_uint32*(255-alpha_uint32)+127)//255)','resize':False,'warp':False,'colorCorrection':False,'candidate':ref(dest),'contextBase':ref(contextPath),'context':ref(context),'contextOperation':'paste entire corrected4096 core at115,115; original context halo retained nonauthoritative','formalAccepted':False,'status':'composed_pending_visual_qa'})
 print(json.dumps({'candidate':str(dest),'sha256':sha(dest),'context':str(context),'manifest':str(R/'composition.json')}))
else:raise ValueError(cmd)
