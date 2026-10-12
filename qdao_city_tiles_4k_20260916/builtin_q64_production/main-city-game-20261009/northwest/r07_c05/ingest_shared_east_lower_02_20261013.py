from pathlib import Path
from datetime import datetime, timezone
import shutil, sys
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent; Z=T.parent; sys.path.insert(0,str(Z))
import production_v2 as p
D=T/'bridges/shared-east-lower-02'
host=Path('C:/Users/luyua/.codex/generated_images/01a12075-f5cf-7c30-9edc-ceb79ed8cfbd/exec-663155ed-ac85-47f9-86f4-d7a359d0950d.png')
native=D/'native.png'; assert not native.exists(); shutil.copy2(host,native)
im=Image.open(native).convert('RGB'); assert im.size==(1254,1254)
assert p.sha(native)==p.sha(host)
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
p.write_json(D/'generation.json',{'id':'shared-east-lower-02','route':'builtin_image_gen','generatedAtUtc':datetime.now(timezone.utc).isoformat(),'file':str(native),'sha256':p.sha(native),'sourceHostFile':str(host),'sourceHostSha256':p.sha(host),'worldBox':[19853,26776,21107,28030],'tileOrigins':{'r07_c05':[3469,2200],'r07_c06':[-627,2200]},'nativePixels':[1254,1254],'request':ref(D/'request.json'),'toolReceipt':ref(D/'tool-receipt.json'),'actualModel':None,'actualQuality':None,'sourceResampled':False,'newSourceAdopted':False,'status':'native_candidate_pending_roi_review'},replace=False)
base=Image.open(T/'bridges/shared-east-lower-01/edit-target.png').convert('RGB')
roi=[590,473,678,596]
trial=base.copy(); trial.paste(im.crop(roi),(roi[0],roi[1])); f=D/'trial-native-roi.png';trial.save(f)
for name,box in [('repair-detail',[540,425,740,635]),('upper-perimeter',[560,443,708,503]),('lower-perimeter',[560,566,708,626]),('left-perimeter',[560,450,620,620]),('right-perimeter',[648,450,708,620])]:trial.crop(box).save(D/(name+'.png'))
a=np.asarray(trial); b=np.asarray(base); mask=np.any(a!=b,axis=2); outside=mask.copy();outside[roi[1]:roi[3],roi[0]:roi[2]]=False
assert not outside.any()
p.write_json(D/'roi-trial-proof.json',{'candidate':ref(f),'source':ref(native),'sourceROI':roi,'worldROI':[19853+roi[0],26776+roi[1],19853+roi[2],26776+roi[3]],'targetBoxes':{'r07_c05':[4059,2673,4096,2796],'r07_c06':[0,2673,51,2796]},'splitSourceROIs':{'r07_c05':[590,473,627,596],'r07_c06':[627,473,678,596]},'exactSameWorldNativeSelection':True,'changedPixels':int(mask.sum()),'pixelsChangedOutsideROI':int(outside.sum()),'programDrawing':False,'visualStatus':'pending'},replace=False)
print({'native':str(native),'sha256':p.sha(native),'roi':roi,'changedPixels':int(mask.sum())})
