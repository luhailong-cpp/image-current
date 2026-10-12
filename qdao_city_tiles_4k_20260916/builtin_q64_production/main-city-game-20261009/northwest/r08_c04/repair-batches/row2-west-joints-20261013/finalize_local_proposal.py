from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
B=Path(__file__).resolve().parent;D1=B/'joint-x2048-01';D2=B/'joint-x2048-02';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def ref(f):return {'file':str(f),'sha256':sha(f)}
for d,stem,status in [(D1,'lower-masked-v2','passed_local_native_roi'),(D2,'upper','passed_local_native_roi')]:
 crops=[d/(stem+'-'+tag+'.png') for tag in ['detail','north','south','west','east']]
 data={'reviewer':'/root/r08_c04_row2_local_repair','actuallyViewed':True,'status':status,'nativePixelScale':1,'cropReviews':[dict(ref(f),status='passed') for f in crops],'finding':'Grout now connects naturally; local native ROI perimeter preserves entering edges without clipped joints. Only candidate ROI passes, not full edge or full tile.','fullTileInternalQAPassed':False,'formalAccepted':False}
 (d/(stem+'-review.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
base=Image.open(D1/'edit-target.png').convert('RGB');trial=base.copy();owner=np.zeros((1254,1254),dtype=np.uint8);sources=[]
for idx,(d,maskfile) in enumerate([(D1,'lower-selection-mask-v2.png'),(D2,'upper-selection-mask.png')],1):
 src=Image.open(d/'native.png').convert('RGB');m=Image.open(d/maskfile);arr=np.array(m);assert set(np.unique(arr)).issubset({0,255});trial.paste(src,(0,0),m);owner[arr==255]=idx;sources.append({'ownerIndex':idx,'native':ref(d/'native.png'),'mask':ref(d/maskfile),'worldBox':[13709,29581,14963,30835],'originInTile':[1421,909],'pixelCount':int((arr==255).sum())})
trial.save(B/'x2048-combined-native-trial.png');Image.fromarray(owner).save(B/'x2048-combined-owner-index.png');trial.crop((467,115,787,1139)).save(B/'x2048-combined-west-seam.png')
t=np.array(trial);a=np.array(base);assert np.array_equal(t[owner==0],a[owner==0])
for i,(d,_) in enumerate([(D1,'lower-selection-mask-v2.png'),(D2,'upper-selection-mask.png')],1):assert np.array_equal(t[owner==i],np.array(Image.open(d/'native.png').convert('RGB'))[owner==i])
(B/'combined-provenance.json').write_text(json.dumps({'base':ref(D1/'edit-target.png'),'sources':sources,'ownerIndex':ref(B/'x2048-combined-owner-index.png'),'trial':ref(B/'x2048-combined-native-trial.png'),'worldBox':[13709,29581,14963,30835],'originInTile':[1421,909],'outsideMasksPixelIdentical':True,'eachOwnedPixelMatchesNativeExactly':True,'resampled':False,'blended':False,'formalAccepted':False},indent=2),encoding='utf-8')
print({'sourceCount':2,'combinedPixels':int((owner>0).sum())})

