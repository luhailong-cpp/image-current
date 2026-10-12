from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
selected=R/'selected-patches.json';before=sha(selected);sel=rd(selected);src=R/sel['patches']['p11']
joint=R.parent/'r12_c08/repairs/r12c08-rail-joint-v4-edge-color.png'
assert sha(joint)=='1cc01d1e79dd7a1aebb9935f814d8b0c62af2cb7ef74bfe3c224e2bd9c02ec4f'
out=R/'processed/rail-v4-provisional';out.mkdir(exist_ok=True)
im=Image.open(src).convert('RGB');j=Image.open(joint).convert('RGB')
im.paste(j.crop((503,125,650,550)),(0,125));p=out/'p11-rail-v4-edge-color-provisional.png';im.save(p)
a=np.array(Image.open(src));b=np.array(im);assert np.array_equal(a[:125],b[:125]) and np.array_equal(a[550:],b[550:]) and np.array_equal(a[:,147:],b[:,147:])
assert sha(selected)==before
d={'tile':R.name,'patch':'p11','status':'provisional_not_selected','file':str(p),'sha256':sha(p),'base':str(src),'baseSha256':sha(src),'joint':str(joint),'jointSha256':sha(joint),'jointDerivation':str(joint)+'.derivation.json','jointDerivationSha256':sha(str(joint)+'.derivation.json'),'jointWorldBox':[32150,44941,33404,46195],'sharedAdoptionWorldBox':[32470,45066,32800,45491],'localIntersectionWorldBox':[32653,45066,32800,45491],'sourceCrop':[503,125,650,550],'destination':[0,125,147,550],'changedCoreWorldBox':[32768,45066,32800,45491],'adoptionCorePixels':13600,'haloIncluded':True,'resampling':False,'blur':False,'pixelBlending':False,'nativeSize':[1254,1254],'outsideAdoptionExactlyUnchanged':True,'activeSelectionUnchanged':True,'priorActiveSelectionSha256':before,'readyToSelect':False,'reasonPending':'Neighbor c08 p14 has unresolved wall/rock G4/G5 below this accepted rail; joint must be adopted consistently after those repairs. Shared rail geometry pass alone is not whole-edge acceptance.'}
wr(str(p)+'.derivation.json',d);wr(out/'provisional-selection.json',d)
print(json.dumps({'file':str(p),'sha256':sha(p),'coreAdoptionPixels':13600,'selected':False}))
