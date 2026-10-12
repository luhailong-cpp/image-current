from pathlib import Path
import sys,json,importlib.util,shutil
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;R=W.parent
spec=importlib.util.spec_from_file_location('assembly',R/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
action,ident,leftname,rightname=sys.argv[1:5]
lp=R/'native'/f'{leftname}.png';rp=R/'native'/f'{rightname}.png'
lr=m.read(str(lp)+'.generation.json');rr=m.read(str(rp)+'.generation.json')
origin=[lr['globalNativeBox'][0]+512,lr['globalNativeBox'][1]];box=origin+[origin[0]+1254,origin[1]+1254];core=[box[0]+115,box[1]+115,box[2]-115,box[3]-115]
left=np.array(Image.open(lp).convert('RGB'));right=np.array(Image.open(rp).convert('RGB'))
base,baseids,bd=m.append_hard(left,np.ones((1254,1254),np.uint8),right,np.full((1254,1254),2,np.uint8),'base-left-right')
guide=W/'guides'/f'{ident}.layout-and-native-overlap.png'
if action=='prepare':
 assert not guide.exists(); im=Image.fromarray(base).crop([512,0,1766,1254]);sources=[lp,rp]
 if len(sys.argv)>5:
  nl=R/'native'/f'{sys.argv[5]}.png';nr=R/'native'/f'{sys.argv[6]}.png';a=np.array(Image.open(nl).convert('RGB'));b=np.array(Image.open(nr).convert('RGB'));north,_,nd=m.append_hard(a,np.ones((1254,1254),np.uint8),b,np.full((1254,1254),2,np.uint8),'north')
  im.paste(Image.fromarray(north).crop([512,1024,1766,1254]),(0,0));sources += [nl,nr]
 im.save(guide);m.write_json(Path(str(guide)+'.derivation.json'),{'globalNativeBox':box,'globalCoreBox':core,'role':'native hardcut edit target only','scale':1,'sources':[{'file':str(p),'sha256':m.sha(p)} for p in sources],'baseCut':bd,'sha256':m.sha(guide)})
elif action=='record':
 reqp=W/'receipts'/f'{ident}.request.json';recp=W/'receipts'/f'{ident}.receipt.json';req=m.read(reqp);receipt=m.read(recp);p=R/'native'/f'{ident}.png';assert not p.exists();shutil.copyfile(receipt['originalFile'],p)
 with Image.open(p) as im: assert im.size==(1254,1254)
 d={'file':str(p),'sha256':m.sha(p),'generatedAt':receipt['returnedAt'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':lr['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool exposes no model/quality selectors and returns no model/quality evidence.','evidence':{'receipt':str(recp),'request':str(reqp),'fields':['output_hint']},'prompt':req['promptFile'],'references':[{'file':f,'sha256':m.sha(f),'role':role} for f,role in zip(req['referenced_image_paths'],req['referenceRoles'])],'globalNativeBox':box,'globalCoreBox':core,'nativeCoreCropBox':[115,115,1139,1139],'status':'candidate-pending-seam-review','nativeScaleResampled':False,'purpose':'internal native bridge; not grid patch'};m.write_json(Path(str(p)+'.generation.json'),d)
 print(json.dumps({'file':str(p),'sha256':m.sha(p),'globalNativeBox':box}))
elif action=='qa':
 p=R/'native'/f'{ident}.png';a=np.array(Image.open(p).convert('RGB'));old=base[:,512:1766];L,lc=m.minimum_vertical_seam(old[:,:115],a[:,:115]);RR,rc=m.minimum_vertical_seam(a[:,1139:],old[:,1139:]);RR+=1139
 mask=(np.arange(1254)[None,:]>=L[:,None])&(np.arange(1254)[None,:]<RR[:,None]);base[:,512:1766]=np.where(mask[...,None],a,old);baseids[:,512:1766]=np.where(mask,17,baseids[:,512:1766]);prefix=W/'qa'/ident
 Image.fromarray(base).save(str(prefix)+'.diagnostic.png');Image.fromarray(baseids).save(str(prefix)+'.source-id.png')
 for label,crop in [('left',[362,0,827,1254]),('right',[1451,0,1916,1254]),('center',[824,0,1454,1254])]:Image.fromarray(base).crop(crop).save(str(prefix)+'.'+label+'.100pct.png')
 d={'file':str(p),'sha256':m.sha(p),'globalNativeBox':box,'globalCoreBox':core,'baseGlobalOrigin':lr['globalNativeBox'][:2],'leftSource':str(lp),'rightSource':str(rp),'leftXByY':L.tolist(),'rightXByY':RR.tolist(),'method':'outer115 side native hardcut; entire core forced; no blend/resize','diagnostic':str(prefix)+'.diagnostic.png'}
 if len(sys.argv)>5:
  nl=R/'native'/f'{sys.argv[5]}.png';nr=R/'native'/f'{sys.argv[6]}.png';a=np.array(Image.open(nl).convert('RGB'));b=np.array(Image.open(nr).convert('RGB'));north,ni,nd=m.append_hard(a,np.ones((1254,1254),np.uint8),b,np.full((1254,1254),2,np.uint8),'north')
  j,ji,jd=m.append_hard(north.transpose(1,0,2),ni.T,base.transpose(1,0,2),baseids.T,'north-to-bridged-row');j=j.transpose(1,0,2);Image.fromarray(j).crop([512,824,1766,1454]).save(str(prefix)+'.north.100pct.png');d['northCut']=jd
 m.write_json(Path(str(prefix)+'.diagnostic.json'),d)
print(action,ident)
