from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parents[1];O=W/'center-final';O.mkdir(exist_ok=True)
sys.path.insert(0,str(B/'work-r03_c04'))
from apply_r03_c04_repairs import window_mask
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resolve(p):return Path(p) if Path(p).is_absolute() else B/p
def save(p,a):Image.fromarray(a).save(p)
id='r03c03_c04_r04c03_c04_center_foot_ground_whole_bridge_v01';p=W/(id+'.png');gen=read(str(p)+'.generation.json');assert sha(p)==gen['sha256'];box=gen['globalNativeBox'];repair=np.asarray(Image.open(p).convert('RGB'))
inputs=read(B/'work-r03_c03/joint-final/center-current-mechanical-check.json')['inputs'];base=np.asarray(Image.open(W/(id+'.guide.png')).convert('RGB')).copy()
# The contribution also removes the existing clipped masonry-course join immediately behind the same foot.
# It never changes the outer 360-pixel context or any upper paving patch.
win=[360,360,1030,1160];mask,path=window_mask(base,repair,win);new=base.copy();new[mask]=repair[mask]
save(O/'center-applied.100pct.png',new);save(O/'center-mask.png',(mask*255).astype(np.uint8));save(O/'center-foot.100pct.png',new[650:1000,450:900]);save(O/'center-intersection.100pct.png',new[350:850,350:950])
for name,r in [('north',(360,360,1030,590)),('south',(360,930,1030,1160)),('west',(360,360,590,1160)),('east',(800,360,1030,1160))]:save(O/('window-'+name+'.100pct.png'),new[r[1]:r[3],r[0]:r[2]])
sources=[];byfile={};arrays={};contrib=[]
def add(s):
 p=resolve(s['file']);rp=resolve(s.get('generationRecord',str(p)+'.generation.json'));g=read(rp);key=str(p.resolve()).lower()
 if key in byfile:return byfile[key]
 assert sha(p)==g['sha256'];sid=len(sources)+1;byfile[key]=sid
 sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'globalNativeBox':g['globalNativeBox'],'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),'nativeScaleResampled':False})
 arrays[sid]=np.asarray(Image.open(p).convert('RGB'));return sid
newid=add({'file':str(p)});artifacts=[];regionids=np.zeros((1254,1254),np.uint16)
for item in inputs:
 tile=item['tile'];r,c=[int(a[1:]) for a in tile.split('_')];ox,oy=(c-1)*4096,(r-1)*4096
 assert sha(item['file'])==item['sha256'] and sha(item['sourceIdFile'])==item['sourceIdSHA256']
 image=np.asarray(Image.open(item['file']).convert('RGB')).copy();original=image.copy();oldids=np.asarray(Image.open(item['sourceIdFile']));ids=np.zeros((4096,4096),np.uint16)
 manifest=read(item['assembly']);registry={s.get('jointSourceId',s.get('sourceId')):s for s in manifest['sources']}
 for old in np.unique(oldids):ids[oldids==old]=add(registry[int(old)])
 hit=[max(ox,box[0]),max(oy,box[1]),min(ox+4096,box[2]),min(oy+4096,box[3])];tx0,ty0,tx1,ty1=[hit[0]-ox,hit[1]-oy,hit[2]-ox,hit[3]-oy];sx0,sy0,sx1,sy1=[hit[0]-box[0],hit[1]-box[1],hit[2]-box[0],hit[3]-box[1]]
 assert np.array_equal(image[ty0:ty1,tx0:tx1],base[sy0:sy1,sx0:sx1])
 m=mask[sy0:sy1,sx0:sx1];image[ty0:ty1,tx0:tx1][m]=repair[sy0:sy1,sx0:sx1][m];ids[ty0:ty1,tx0:tx1][m]=newid
 regionids[sy0:sy1,sx0:sx1]=ids[ty0:ty1,tx0:tx1]
 total=0;parts=[]
 for sid in np.unique(ids):
  yy,xx=np.nonzero(ids==sid);s=sources[int(sid)-1];sx=xx+ox-s['globalNativeBox'][0];sy=yy+oy-s['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(image[yy,xx],arrays[int(sid)][sy,sx]);total+=len(xx);parts.append({'sourceId':int(sid),'pixels':len(xx)})
 assert total==16777216
 op=O/(tile+'.center-final.png');ip=O/(tile+'.source-id.png');save(op,image);save(ip,ids)
 changed=np.any(image!=original,axis=2);cp=O/(tile+'.changed-pixels.png');save(cp,(changed*255).astype(np.uint8));yy,xx=np.nonzero(changed)
 artifacts.append({'tile':tile,'file':str(op),'sha256':sha(op),'globalBox':[ox,oy,ox+4096,oy+4096],'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'changedPixels':int(changed.sum()),'changedGlobalBoundingBox':[int(xx.min()+ox),int(yy.min()+oy),int(xx.max()+ox+1),int(yy.max()+oy+1)] if len(xx) else None,'changedPixelMask':{'file':str(cp),'sha256':sha(cp)},'base':item,'proof':{'pixels':total,'mismatches':0,'contributions':parts}})
save(O/'center-source-id.png',regionids)
write(O/'joint-assembly.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'status':'center-repaired-pending-visual-review','formalAccepted':False,'sources':sources,'artifacts':artifacts,'newNativeSourceId':newid,'nativeBox':box,'contributionWindow':win,'contributionPath':path,'wholeCoreForced':False,'nativePixelsSelected':int(mask.sum()),'proof':{'pixels':67108864,'mismatches':0},'resample':False,'feather':False,'pixelPainting':False,'guidePixelsUsed':False,'allPixelsNative':True,'script':str(Path(__file__)),'scriptSha256':sha(__file__),'actualModel':None,'actualQuality':None,'pending':'northern paving rebase remains separate; these four candidates preserve baseline paving status'})
print(json.dumps({'out':str(O),'sources':len(sources),'nativePixelsSelected':int(mask.sum()),'pixelsVerified':67108864,'mismatches':0,'changes':[{k:v for k,v in a.items() if k in ['tile','sha256','changedPixels','changedGlobalBoundingBox']} for a in artifacts]}))
