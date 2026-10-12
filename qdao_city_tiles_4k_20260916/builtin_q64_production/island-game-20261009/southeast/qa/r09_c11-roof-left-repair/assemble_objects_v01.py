from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,os
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
p=json.loads((Q/'rect-trial-v01.json').read_text());b=Image.new('RGB',(8192,4096))
for i,o in enumerate(p['outputs']):b.paste(Image.open(o['base']).convert('RGB'),(4096*i,0))
U=np.asarray(Image.open(p['sources'][0]['file']).convert('RGB'));L=np.asarray(Image.open(p['sources'][1]['file']).convert('RGB'));B=np.asarray(b.crop((3300,0,4554,1854))).copy();C=B.copy();C[:737]=U[:737];C[737:]=L[137:]
# Manually traced anatomical boundary: side trough, curved transverse joint,
# next side trough, terminal transverse joint, and whole old left terminal edge.
# These are ownership coordinates only. No source RGB or coordinate is changed.
left=[(416,0),(400,70),(380,105),(340,155),(300,205),(250,265),(200,330),(150,395),(105,438),(110,450),(150,448),(195,460),(235,485),(275,520),(300,534),(310,545),(340,553),(370,568),(405,590),(406,600),(317,700),(227,800),(140,900),(53,1000),(4,1055),(0,1087),(40,1081),(75,1102),(120,1106),(170,1122),(215,1146),(260,1180),(303,1215),(325,1238),(310,1280),(285,1315),(258,1350),(250,1370),(265,1390)]
im=Image.new('1',(1254,1854));ImageDraw.Draw(im).polygon(left+[(265,1853),(1253,1853),(1253,0)],fill=1);mask=np.asarray(im).copy()
# Complete gold medallions and blue barrel feet belong together. A bounded
# material classifier is used solely to trace the outside roof/wood contour.
a=C.astype(np.int16);blue=(a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>a[:,:,1]+15)&(a[:,:,2]>45)
gold=(a[:,:,0]>100)&(a[:,:,1]>a[:,:,0]*.57)&(a[:,:,1]>a[:,:,2]*1.5)&(a[:,:,2]<155)
caps=np.interp(np.arange(1254),[0,150,250,400,550,650,800,900,1050,1253],[1370,1390,1430,1470,1490,1510,1540,1580,1630,1670])
old=B.astype(np.int16);oldblue=(old[:,:,2]>old[:,:,0]+25)&(old[:,:,2]>old[:,:,1]+15)&(old[:,:,2]>45)
roof=(blue|oldblue)&(np.arange(1854)[:,None]<caps[None,:]);bottom=1853-roof[::-1].argmax(0)+1
foot=Image.fromarray((np.arange(1854)[:,None]<=bottom[None,:]).astype(np.uint8)*255)
# Explicit complete medallion silhouettes (including prior-position footprint)
# prevent a color classifier from cutting a dark golden rim. Only the mask is
# drawn; every output RGB pixel still comes from its unmodified source coordinate.
d=ImageDraw.Draw(foot)
gold_polys=[([(276,750),(291,727),(325,719),(372,729),(415,759),(432,799),(422,830),(386,850),(339,840),(300,813),(274,778)],(32,12)), ([(655,774),(670,750),(705,748),(754,769),(794,803),(807,842),(791,868),(754,882),(712,870),(673,842),(653,806)],(6,2)), ([(973,871),(993,847),(1036,854),(1080,882),(1115,920),(1125,951),(1110,978),(1075,985),(1032,968),(995,940),(973,912)],(3,1))]
for poly,(dx,dy) in gold_polys:
 for sx,sy in [(0,0),(dx,dy)]: d.polygon([(x+sx,y+600+sy) for x,y in poly],fill=255)
d.polygon([(x,y+600) for x,y in [(270,716),(330,710),(402,725),(469,790),(472,845),(445,882),(389,885),(322,851),(270,793)]],fill=255)
mask&=np.asarray(foot)>0
# The right cut remains at the closest exact original pixel column, outside the
# main corrected object. Its material seam remains separately subject to QA.
mask[:,1230:]=False
out=np.asarray(b).copy();out[:1854,3300:4554][mask]=C[mask]
sid=np.zeros((4096,8192),np.uint8);z=sid[:1854,3300:4554];z[mask&(np.arange(1854)[:,None]<737)]=1;z[mask&(np.arange(1854)[:,None]>=737)]=2
for i,o in enumerate(p['outputs']):
 f=Q/f"{o['tile']}-trial-object-v01.png";Image.fromarray(out[:,i*4096:(i+1)*4096]).save(f);sf=Q/f"{o['tile']}-source-id-object-v01.png";Image.fromarray(sid[:,i*4096:(i+1)*4096]).save(sf);o.update(file=str(f),sha256=sh(f),sourceID=str(sf),sourceIDSha256=sh(sf))
trial=Image.fromarray(out);ev=[]
boxes=[('object-top',[3300,0,4050,650]),('object-middle',[3300,400,4100,1100]),('object-terminal',[3250,1000,4050,1575]),('object-foot-right',[3950,1250,4554,1730])]
for n,box in boxes:
 f=Q/f'{n}-v01.png';trial.crop(box).save(f);ev.append({'file':str(f),'sha256':sh(f),'canvasCrop':box})
for label,a in [('old',B),('new',C)]:
 for n,box in [('joint-upper',[0,350,550,650]),('joint-terminal',[0,1020,450,1400])]:
  Image.fromarray(a).crop(box).save(Q/f'{n}-{label}-100pct.png')
maskfile=Q/'complete-object-mask-v01.png';Image.fromarray(mask.astype(np.uint8)*255).save(maskfile)
p.update(status='pending_anatomical_boundary_review',manualAnatomicalLeftBoundary=left,maskFile=str(maskfile),maskSha256=sh(maskfile),evidence=ev,formalAccepted=False)
wr(Q/'object-trial-v01.json',p);print('Saved anatomical ownership trial only; main candidates untouched.')
