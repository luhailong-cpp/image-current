"""Join vertically overlapping original AI pixels, then retain one complete-object hard mask.
No resampling, painting, feathering or color adjustment. All outputs are new files.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,importlib.util,re
import numpy as np
from PIL import Image,ImageDraw
Z=Path(__file__).resolve().parents[1];QA=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def inp(r):
 p=Path(r['path']);assert sha(p)==r['sha256'];return p
def rgb(p):
 im=Image.open(p);assert im.mode in ['RGB','RGBA'];assert im.mode=='RGB' or im.getextrema()[3]==(255,255);return np.asarray(im.convert('RGB')).copy()
def savepng(p,a):
 assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(rgb(p),a);return ref(p)
def savenpy(p,a):
 assert not p.exists();np.save(p,a);assert np.array_equal(np.load(p),a);return ref(p)
def savejson(p,a):
 assert not p.exists();p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');return ref(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);arg=ap.parse_args();m=read(arg.manifest);prefix=m['outputPrefix'];assert re.fullmatch('repair-[a-z0-9_-]+',prefix)
 s=importlib.util.spec_from_file_location('long_repair_helper',Z/'tools/seam_helpers.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
 sources=m['nativeSources'];assert len(sources)==2
 for source,generation in zip(sources,m['nativeGenerationRecords']):
  record=read(inp(generation));assert record['sha256']==source['sha256']
 a,b=[rgb(inp(v)) for v in sources];assert a.shape==b.shape==(1254,1254,3)
 stride=m['stride'];overlap=1254-stride;assert 0<overlap<1254
 seam=h._minimum_vertical_seam(a[stride:].transpose(1,0,2),b[:overlap].transpose(1,0,2)).astype(np.int32)
 assert seam.shape==(1254,) and 0<=seam.min()<=seam.max()<overlap and np.all(np.abs(np.diff(seam))<=1)
 long=np.concatenate([a,b[overlap:]],axis=0);ids=np.ones(long.shape[:2],dtype=np.uint8);ids[1254:]=2
 yy=np.arange(overlap)[:,None];choose=yy>=seam[None,:];long[stride:1254]=np.where(choose[:,:,None],b[:overlap],a[stride:]);ids[stride:1254]=np.where(choose,2,1)
 for idx,pixels,start in [(1,a,0),(2,b,stride)]:
  sel=ids[start:start+1254]==idx;assert np.array_equal(long[start:start+1254][sel],pixels[sel])
 longref=savepng(QA/(prefix+'-native-1254x'+str(len(long))+'.png'),long);idsref=savenpy(QA/(prefix+'-native-source-ids.npy'),ids)
 base=rgb(inp(m['baseContext']));assert base.shape==(4326,4326,3);box=m['tileContextBox'];cb=[v+115 for v in box];x1,y1,x2,y2=cb;assert x2-x1==1254 and y2-y1==len(long) and 0<=x1<x2<=4326 and 0<=y1<y2<=4326;old=base[y1:y2,x1:x2].copy()
 # Exterior polygon contains full visible object plus at most a narrow edge/shadow allowance.
 poly=m['objectPolygon'];assert len(poly)>=4 and all(len(p)==2 and all(type(v)==int for v in p) and 0<=p[0]<1254 and 0<=p[1]<len(long) for p in poly)
 maskim=Image.new('L',(1254,len(long)),0);ImageDraw.Draw(maskim).polygon([tuple(p) for p in poly],fill=1);mask=np.asarray(maskim).astype(bool)
 # Optional side seams lie outside the object faces. They only limit exterior selection.
 paths=[]
 for side,(lo,hi) in m.get('sideSeamBands',{}).items():
  assert side in ['left','right'] and 0<=lo<hi<=1254
  p=h._minimum_vertical_seam(old[:,lo:hi],long[:,lo:hi]).astype(np.int32)+lo;assert np.all(np.abs(np.diff(p))<=1)
  mask &= np.arange(1254)[None,:]>=p[:,None] if side=='left' else np.arange(1254)[None,:]<p[:,None]
  paths.append({'side':side,'xByLocalRow':p.tolist(),'band':[lo,hi]})
 after=np.where(mask[:,:,None],long,old);context=base.copy();context[y1:y2,x1:x2]=after
 cid=np.zeros((4326,4326),np.uint8);cid[y1:y2,x1:x2]=np.where(mask,ids,0)
 assert np.array_equal(context[cid==0],base[cid==0]);assert np.array_equal(after[mask],long[mask])
 for idx,pixels,start in [(1,a,0),(2,b,stride)]:
  selected=(cid[y1+start:y1+start+1254,x1:x2]==idx);assert np.array_equal(context[y1+start:y1+start+1254,x1:x2][selected],pixels[selected])
 maskref=savenpy(QA/(prefix+'-object-mask.npy'),mask.astype(np.uint8));ctxref=savepng(QA/(prefix+'-context-native.png'),context);core=savepng(QA/(prefix+'-candidate-4096.png'),context[115:4211,115:4211]);cidref=savenpy(QA/(prefix+'-context-source-ids.npy'),cid)
 traces={'schemaVersion':1,'manifest':ref(arg.manifest),'script':ref(Path(__file__)),'baseContext':m['baseContext'],'nativeSources':sources,'nativeGenerationRecords':m['nativeGenerationRecords'],'stride':stride,'overlap':overlap,'horizontalSeamYByColumn':(seam+stride).tolist(),'nativeComposite':longref,'nativeSourceIds':idsref,'tileContextBox':box,'contextBox':cb,'completeObjectMask':maskref,'polygon':poly,'sideSeamPaths':paths,'context':ctxref,'candidate':core,'contextSourceIds':cidref,'identityValidation':'all output pixels equal their recorded original AI source or untouched base; validated exhaustively','nativePixelsResampled':False,'featheringApplied':False,'colorProcessingApplied':False}
 trace=savejson(QA/(prefix+'-trace.json'),traces)
 crops=[]
 for name,box2 in m['qaCrops'].items():
  xx1,yy1,xx2,yy2=box2;assert 0<=xx1<xx2<=1254 and 0<=yy1<yy2<=len(long);p=QA/(prefix+'-'+name+'-100pct.png');r=savepng(p,after[yy1:yy2,xx1:xx2]);r['nativeCompositeBox']=box2;crops.append(r)
 savejson(QA/(prefix+'-qa-crops.json'),{'trace':trace,'crops':crops})
 print(json.dumps({'native':longref,'context':ctxref,'candidate':core,'mask':maskref,'trace':trace}))
if __name__=='__main__':main()
