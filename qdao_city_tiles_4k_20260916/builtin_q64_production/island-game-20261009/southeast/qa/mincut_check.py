"""Read-only source selection experiment: no blur, blending, warp or paint."""
from pathlib import Path
import numpy as np,json,hashlib,importlib.util
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
helper=Path('D:/work/image/tianyong_festival_hd_20260910/seam_helpers.py')
spec=importlib.util.spec_from_file_location('map_seam',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
a=ROOT/'native/r09_c12_p11_v01.png';b=ROOT/'native/r09_c12_p12_v04.png'
left=np.array(Image.open(a).convert('RGB'));right=np.array(Image.open(b).convert('RGB'));seam=mod._minimum_vertical_seam(left[:,-230:],right[:,:230]);mask=np.arange(230)[None,:]>=seam[:,None]
overlap=np.where(mask[:,:,None],right[:,:230],left[:,-230:]);join=np.concatenate([left[:,:-230],overlap,right[:,230:]],axis=1)
out=ROOT/'qa/p11-p12-v04.mincut-unblended-native.png';Image.fromarray(join[:,883:1395]).save(out)
data={'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':'minimum-error seam through original native overlap, binary source selection only','sources':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in[a,b]],'algorithm':str(helper),'algorithmSha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'nativePreviewCrop':[883,0,1395,1254],'seamLocalXByY':seam.tolist(),'featherRadius':0,'sourceResampling':False,'geometryWarp':False,'colorMatching':False,'status':'pending_native_visual_inspection_not_accepted'}
(ROOT/'qa/p11-p12-v04.mincut.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(str(out))
