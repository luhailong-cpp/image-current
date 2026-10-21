from workflow import ROOT,read,write,sha,now,patch
from pathlib import Path
from PIL import Image
import shutil,sys,re
pid,v,receipt=sys.argv[1:]
assert pid[:7] in ['r13_c13','r14_c13','r13_c14','r12_c14']
rp=Path(receipt);rec=read(rp);args=rec['submittedArguments']
src=Path(re.search(r'as (C:\\[^\r\n]+?\.png) by default',rec['output_hint']).group(1))
out=ROOT/'native'/f'{pid}_{v}.png'
if out.exists():assert sha(out)==sha(src),'Never overwrite an existing different original'
else:shutil.copy2(src,out)
with Image.open(out) as im:im.load();size=list(im.size);mode=im.mode
assert size==[1254,1254],size
pf=ROOT/'prompts'/f'{pid}_{v}.submitted-exact.prompt.txt'
if pf.exists():assert pf.read_text(encoding='utf-8')==args['prompt']
else:pf.write_text(args['prompt'],encoding='utf-8')
refs=[{'file':x,'sha256':sha(Path(x)),'role':'actually submitted image reference'} for x in args.get('referenced_image_paths',[])]
meta=Path(str(out)+'.generation.json');old=read(meta) if meta.exists() else {}
coordpath=ROOT/'prompts'/f'{pid}_{v}.registered.json'
coordinate=read(coordpath) if coordpath.exists() else patch(pid)
old.update({'file':str(out),'sha256':sha(out),'generatedAt':old.get('generatedAt',now()),'width':1254,'height':1254,'format':'PNG','mode':mode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'prompt':str(pf),'promptSha256':sha(pf),'references':refs,'coordinate':coordinate,'evidence':{'toolReceipt':str(rp),'returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'resizedAfterGeneration':False,'status':old.get('status','native_saved_pending_actual_seam_review')})
write(meta,old)
print({'file':str(out),'sha256':sha(out),'nativePixels':size,'actualReferenceCount':len(refs)})
