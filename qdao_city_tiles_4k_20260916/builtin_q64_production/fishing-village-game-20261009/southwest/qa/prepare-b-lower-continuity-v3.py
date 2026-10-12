import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path(__file__).resolve().parents[1];a=Z/'native/r09_c06_repair_b_complete_upper_v3.png';b=Z/'qa/repair-r09_c06-b-complete-center-post-lower-source-native-v3.png';dst=Z/'qa/repair-r09_c06-b-complete-center-post-lower-continuity-native-v3.png'
assert not dst.exists();upper=np.asarray(Image.open(a).convert('RGB'));lower=np.asarray(Image.open(b).convert('RGB')).copy();lower[:230]=upper[1024:1254];Image.fromarray(lower).save(dst)
assert np.array_equal(np.asarray(Image.open(dst))[:230],upper[1024:1254]);assert np.array_equal(np.asarray(Image.open(dst))[230:],np.asarray(Image.open(b).convert('RGB'))[230:])
ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rec={'file':ref(dst),'dimensions':[1254,1254],'tileContextBox':[1360,1524,2614,2778],'operation':'exact native integer copy; original lower crop plus upper final 230 rows in top 230 rows','base':ref(b),'continuitySource':ref(a),'sourceBox':[0,1024,1254,1254],'destinationBox':[0,0,1254,230],'nativePixelsResampled':False,'colorProcessingApplied':False,'pixelIdentityAssertionsPassed':True}
Path(str(dst)+'.derivation.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');print(ref(dst))
