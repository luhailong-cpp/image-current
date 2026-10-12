from pathlib import Path
from PIL import Image
import numpy as np,runpy,sys,json,hashlib
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;ROOT=B.parents[1]
P=runpy.run_path(str(ROOT/'pipeline.py'))
south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
old=np.array(Image.open(south).convert('RGB'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for version in ['fix07','fix08']:
 D=B/version;newfile=D/'generated.png';new=np.array(Image.open(newfile).convert('RGB'))
 pair,seam=P['append_native'](new.transpose(1,0,2),old.transpose(1,0,2));pair=pair.transpose(1,0,2)
 assert pair.shape==(2278,1254,3)
 inter=pair[1024:1254]
 assert np.all(np.all(inter==new[1024:1254],axis=2)|np.all(inter==old[:230],axis=2))
 im=Image.fromarray(pair)
 out=D/'minimum-error-pair-QA-only.png'
 if out.exists():raise FileExistsError(out)
 im.save(out)
 im.crop((0,819,1254,1459)).save(D/'minimum-error-south-boundary-native.png')
 im.crop((600,1019,1120,1269)).save(D/'minimum-error-rail-boundary-native.png')
 manifest={'role':'QA pairing only, not a replacement source or formally accepted tile','sources':[{'file':str(x),'sha256':sha(x)} for x in [newfile,south]],
           'file':str(out),'sha256':sha(out),'size':[1254,2278],'worldBox':[12173,15245,13427,17523],
           'sourcePixelSelectionOnly':True,'noResampling':True,'sourceReplayPixels':int(pair.shape[0]*pair.shape[1]),
           'seamYForEachNativeX':(seam+1024).tolist(),'seamYRange':[int(seam.min()+1024),int(seam.max()+1024)],
           'actuallyViewed':False,'formalAccepted':False}
 (D/'minimum-error-pair-assembly.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print(json.dumps({'version':version,'seamYRange':manifest['seamYRange'],'nativePixelQA':str(D/'minimum-error-south-boundary-native.png')}))
