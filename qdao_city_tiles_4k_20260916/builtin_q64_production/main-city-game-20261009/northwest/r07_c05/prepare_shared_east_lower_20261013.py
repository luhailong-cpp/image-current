from pathlib import Path
import sys
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
D=T/'bridges/shared-east-lower-01';D.mkdir(exist_ok=True)
W=T/'candidate/r07_c05-candidate-native-rois-final-872df04172946ceb/candidate.png';E=Z/'r07_c06/candidate/r07_c06-candidate-native-roi-v07.png';w=Image.open(W).convert('RGB');e=Image.open(E).convert('RGB');im=Image.new('RGB',(1254,1254));im.paste(w.crop((3469,2200,4096,3454)),(0,0));im.paste(e.crop((0,2200,627,3454)),(627,0));f=D/'edit-target.png';assert not f.exists();im.save(f)
p.write_json(D/'placement.json',{'kind':'supplemental-shared-seam-native','tile':'r07_c05','tileOriginXY':[3469,2200],'worldBox':[19853,26776,21107,28030],'nativePixels':[1254,1254],'editTarget':ref(f),'sourceResampled':False,'leftCandidate':ref(W),'rightCandidate':ref(E),'tileBoundaryNativeX':627,'adoptionNotYetApproved':True},replace=False)
for name,box in [('repair-context',[477,278,827,658]),('upper-tip',[537,328,737,448]),('lower-tip',[537,438,737,578])]:im.crop(box).save(D/(name+'.png'))
print(f)
