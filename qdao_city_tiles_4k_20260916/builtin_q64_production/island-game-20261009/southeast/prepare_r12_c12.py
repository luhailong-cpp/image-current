from workflow import *
from PIL import Image
import subprocess,sys
tid='r12_c12';subprocess.run([sys.executable,str(ROOT/'prepare_tile.py'),tid],check=True)
ref=read(ROOT/'references.json')[0];tile=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']==tid);im=Image.open(ref['file']).convert('RGB')
scale=1254/57344;box=[11*4096*scale,11*4096*scale,12*4096*scale,12*4096*scale]
im.transform((1024,1024),Image.Transform.EXTENT,tuple(box),Image.Resampling.BICUBIC).save(ROOT/'guides/r12_c12.whole-layout-only.png')
prog=ROOT/'progress-r12_c12.json'
if not prog.exists():write(prog,{'tile':tid,'updatedAt':now(),'status':'preparing','generatedNativeCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'nextStep':'Continue from accepted r11c12 south edge using exact native sources.'})
base=ROOT/'tiles/r11_c12.candidate-v02.png';bim=Image.open(base).convert('RGB');topofTile=11*4096;leftofTile=11*4096
for col in range(1,5):
 pid=f'{tid}_p1{col}';p=patch(pid);guide=Image.open(ROOT/'guides'/f'{pid}.layout-only.png').convert('RGB');xb=p['nativeGlobalBox'][0]-leftofTile;x0=max(0,xb);x1=min(4096,xb+1254);crop=[x0,3981,x1,4096];dest=[x0-xb,0];guide.paste(bim.crop(crop),dest);out=ROOT/'guides'/f'{pid}.native-context-v01.png';assert not out.exists();guide.save(out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'derivedFrom':[{'file':str(base),'sha256':sha(base),'sourceCrop':crop,'destination':dest}],'role':'Native north115 halo anchor from accepted adjacent candidate at exact world coordinates; blurry remainder layout only.','usableAsFinalArt':False})
print('prepared')

