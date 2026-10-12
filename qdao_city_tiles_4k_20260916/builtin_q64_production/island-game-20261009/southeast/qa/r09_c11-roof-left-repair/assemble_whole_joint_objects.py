from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,os,math
import sys
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
V=sys.argv[1] if len(sys.argv)>1 else 'v01'
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
base=[R/'tiles/r09_c11.candidate-v04.png',R/'tiles/r09_c12.candidate-v08.png'];b=Image.new('RGB',(8192,4096))
for i,p in enumerate(base):b.paste(Image.open(p).convert('RGB'),(i*4096,0))
up=R/'native/r09_c11_roof_color_upper_v01.png';whole=R/'native/r09_c11_roof_whole_joint_v01.png'
U=np.asarray(Image.open(up).convert('RGB'));W=np.asarray(Image.open(whole).convert('RGB'));B=np.asarray(b.crop((3230,0,4554,1624))).copy();C=B.copy();C[:400,70:]=U[:400];C[400:,0:1254]=W[30:]
upperWholeBoundary=[];wOwn=np.zeros((1624,1324),bool);wOwn[400:,:1254]=True
if V in ['v04','v05']:
 # Complete curved collars belong to W, with U supplying only the body above.
 # This replaces a horizontal cut through multiple gutters with actual object
 # top edges; all pixels remain at their exact native world coordinates.
 upperWholeBoundary=[(0,650),(70,650),(165,75),(175,62),(210,58),(250,63),(290,78),(325,104),(350,129),(365,157),(375,155),(400,154),(430,159),(460,170),(490,186),(508,196),(512,176),(550,170),(590,178),(635,197),(679,225),(717,261),(745,297),(760,322),(775,317),(815,315),(855,324),(900,344),(944,374),(979,413),(1007,452),(1021,473),(1035,461),(1080,455),(1125,463),(1170,482),(1213,511),(1253,548)]
 if V=='v05':upperWholeBoundary=[(x,max(0,y-30)) for x,y in upperWholeBoundary]
 cuts=np.interp(np.arange(1254),[x for x,y in upperWholeBoundary],[y for x,y in upperWholeBoundary])+370
 wOwn[:,:]=False;wOwn[:,:1254]=np.arange(1624)[:,None]>=cuts[None,:]
 C=B.copy();C[:1254,70:]=U
 wCanvas=B.copy();wCanvas[370:,:1254]=W;C[wOwn]=wCanvas[wOwn]
# Physical side trough, then entire source terminal objects. All coordinates
# below are in a fixed two-tile canvas; none alter a source's pixel coordinates.
left=[(3716,0),(3700,70),(3680,105),(3640,155),(3600,205),(3550,265),(3500,330),(3445,400),(3405,450),(3340,530),(3280,610),(3230,675),(3230,1623)]
if V in ['v02','v03','v04','v05']:
 left=left[:9]+[(3230+x,370+y) for x,y in [(220,79),(270,92),(315,117),(350,150),(367,165),(365,180),(400,178),(444,180),(480,192),(511,207),(450,280),(360,390),(280,490),(190,600),(115,680),(80,710),(40,760),(16,810),(25,861),(60,900),(60,1253)]]
right=[(4484,0),(4484,1045),(4430,1125),(4380,1190),(4330,1255),(4275,1326),(4220,1388),(4181,1435),(4185,1498),(4190,1623)]
im=Image.new('1',(1324,1624));ImageDraw.Draw(im).polygon([(x-3230,y) for x,y in left+right[::-1]],fill=1);mask=np.asarray(im).copy()
physicalGrooveTrace=[]
if V in ['v03','v04','v05']:
 for y in range(210,706):
  expect=int(511-.855*(y-207));lo=max(0,expect-22);hi=min(1254,expect+22);lum=W[y,lo:hi].mean(1);x=int(lum.argmin())+lo-2
  mask[y+370,:max(0,x)]=False
  oldleft=next((i for i,v in enumerate(mask[y+370]) if v),1254)
  if x<oldleft:mask[y+370,max(0,x):oldleft]=True
  physicalGrooveTrace.append([x+3230,y+370])
def blue(a):
 a=a.astype(np.int16);return (a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>a[:,:,1]+15)&(a[:,:,2]>45)
roof=blue(C)|blue(B);bottom=1623-roof[::-1].argmax(0)+2;foot=Image.fromarray((np.arange(1624)[:,None]<=bottom[None,:]).astype(np.uint8)*255);d=ImageDraw.Draw(foot)
ellipses=[]
def add_ellipse(cx,cy,ax,by,deg,role):
 t=math.radians(deg);pts=[]
 for a in np.linspace(0,2*math.pi,96,endpoint=False):
  x=ax*math.cos(a);y=by*math.sin(a);pts.append((round(cx+x*math.cos(t)-y*math.sin(t)),round(cy+x*math.sin(t)+y*math.cos(t)+370)))
 d.polygon(pts,fill=255);ellipses.append({'centerInWholeNative':[cx,cy],'axes':[ax,by],'rotationDegrees':deg,'role':role})
# Native and old footprints are both included, so no old gold crescent remains.
# The complete own cast-shadow footprint travels with each source object.
for e in [(166,916,87,58,35,'new first complete medallion'),(186,930,87,58,35,'old first medallion footprint'),(452,1024,88,59,35,'second complete medallion'),(808,1043,88,60,35,'third complete medallion'),(177,979,88,43,25,'first complete cast shadow'),(191,994,88,43,25,'old first shadow footprint'),(450,1104,91,40,25,'second cast shadow'),(808,1128,88,39,25,'third cast shadow')]:add_ellipse(*e)
mask&=np.asarray(foot)>0
out=np.asarray(b).copy();out[:1624,3230:4554][mask]=C[mask];sid=np.zeros((4096,8192),np.uint8);r=sid[:1624,3230:4554];r[mask&~wOwn]=1;r[mask&wOwn]=3
outputs=[]
for i,tid in enumerate(['r09_c11','r09_c12']):
 f=Q/f'{tid}-trial-whole-object-{V}.png';Image.fromarray(out[:,i*4096:(i+1)*4096]).save(f);sf=Q/f'{tid}-source-id-whole-object-{V}.png';Image.fromarray(sid[:,i*4096:(i+1)*4096]).save(sf);outputs.append({'tile':tid,'file':str(f),'sha256':sh(f),'sourceID':str(sf),'sourceIDSha256':sh(sf),'base':str(base[i]),'baseSha256':sh(base[i])})
trial=Image.fromarray(out);evidence=[]
for n,box in [('left-top',[3230,0,3830,675]),('left-foot',[3020,650,3760,1450]),('upper-whole',[3230,272,4554,528]),('complete-foot',[3230,1050,4484,1690]),('right-top',[4290,0,4600,1045]),('right-foot',[4080,1045,4580,1670]),('shared',[3840,0,4352,1670]),('original-bar',[3600,0,4028,1500])]:
  f=Q/f'whole-object-{n}-{V}.png';trial.crop(box).save(f);evidence.append({'file':str(f),'sha256':sh(f),'canvasCrop':box})
maskfile=Q/f'whole-object-combined-mask-{V}.png';Image.fromarray(mask.astype(np.uint8)*255).save(maskfile)
wr(Q/f'whole-object-trial-{V}.json',{'status':'pending_final_boundary_QA','outputs':outputs,'sources':[{'id':1,'file':str(up),'sha256':sh(up),'originInTwoTileCanvas':[3300,0]},{'id':3,'file':str(whole),'sha256':sh(whole),'originInTwoTileCanvas':[3230,370]}],'source0':'exact previous candidate at same coordinate','leftAnatomicalBoundary':left,'physicalDarkGrooveTrace':physicalGrooveTrace,'traceMethod':'Only within a manually identified native dark gutter, choose its dark center and own the complete gutter with the new tile; not a minimum old/new RGB difference route.','rightAnatomicalBoundary':right,'completeObjectFootprints':ellipses,'upperWholeCutY':None if V in ['v04','v05'] else 400,'upperWholeObjectBoundaryInWholeNative':upperWholeBoundary,'mask':str(maskfile),'maskSha256':sh(maskfile),'evidence':evidence,'RGBChanged':False,'resized':False,'blended':False,'formalAccepted':False})
print('Whole source roof/medallions trial saved. No main tile changes.')
