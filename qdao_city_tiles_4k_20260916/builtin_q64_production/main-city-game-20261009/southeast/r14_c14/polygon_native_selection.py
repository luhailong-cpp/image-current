from pathlib import Path
import sys,json,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selection',T/'selective_replay.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
def apply(native_version,label,polygons):
 d=T/'repairs'/native_version;p=s.read(d/'preparation.json');g=s.read(d/'generation.json');polygons=json.loads(polygons)
 cur=s.read(T/'repairs/latest-repair.json')
 for k in ['candidate','context']:s.check(cur[k])
 for a in [g['native'],g['originalOutput'],g['receipt'],g['preparation'],p['rawTarget'],p['sourceCandidate'],p['request'],p['prompt']]+p['references']:s.check(a)
 out=T/'repairs'/label;out.mkdir(exist_ok=False)
 mask=Image.new('L',(1254,1254),0);dr=ImageDraw.Draw(mask)
 for points in polygons:
  s.need(all(0<=x<1254 and 0<=y<1254 for x,y in points),'Polygon bounds')
  dr.polygon([tuple(a) for a in points],fill=255)
 inner1=np.array(mask.filter(ImageFilter.MinFilter(3)));inner2=np.array(mask.filter(ImageFilter.MinFilter(5)))
 alpha=np.where(inner2==255,255,np.where(inner1==255,128,0)).astype(np.uint8)
 base=np.array(Image.open(cur['candidate']['path']).convert('RGB'));gen=np.array(Image.open(g['native']['path']).convert('RGB'));raw=np.array(Image.open(p['rawTarget']['path']).convert('RGB'))
 x,y,x1,y1=p['sourceCropIn4096'];old=base[y:y1,x:x1].copy()
 s.need(np.array_equal(old[alpha>0],raw[alpha>0]),'Changed applied region')
 a=alpha[:,:,None].astype(np.uint32);base[y:y1,x:x1]=((old.astype(np.uint32)*(255-a)+gen.astype(np.uint32)*a+127)//255).astype(np.uint8)
 s.png(out/'alpha.png',Image.fromarray(alpha));candidate=T/'candidate'/('r14_c14-4k-'+label+'.png');s.png(candidate,Image.fromarray(base))
 ctx=np.array(Image.open(cur['context']['path']).convert('RGB'));ctx[115:4211,115:4211]=base
 context=T/'candidate'/('r14_c14-context-'+label+'.png');s.png(context,Image.fromarray(ctx));s.png(out/'review-1254.png',Image.fromarray(base[y:y1,x:x1]))
 m={'version':label,'tile':'r14_c14','sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'candidate':s.art(candidate),'context':s.art(context),'native':g['native'],'generation':s.art(d/'generation.json'),'preparation':s.art(d/'preparation.json'),'receipt':g['receipt'],'originalOutput':g['originalOutput'],'placement':p['sourceCropIn4096'],'alpha':s.art(out/'alpha.png'),'polygonsInNative':polygons,'compositor':s.art(Path(__file__)),'rule':'Unscaled actual native polygon union. Polygon rasterization uses Pillow ImageDraw. Outer boundary excluded; one eroded pixel128 alpha, two eroded pixels255. uint32 rounded composition. No resize, no generated painting by code. All outside pixels unchanged.','formalAccepted':False}
 s.write(out/'composition.json',m);s.replay(str(out/'composition.json'));return {'candidate':m['candidate'],'review':str(out/'review-1254.png'),'manifest':str(out/'composition.json')}
if __name__=='__main__':print(json.dumps(apply(*sys.argv[1:]),indent=2))

