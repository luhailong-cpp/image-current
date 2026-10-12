from pathlib import Path
from datetime import datetime,timezone
import sys,shutil
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
D=T/'bridges/shared-east-lower-03';host=Path('C:/Users/luyua/.codex/generated_images/01a12075-f5cf-7c30-9edc-ceb79ed8cfbd/exec-e11a311b-1f9a-40f0-867e-ab588b3d49b4.png');native=D/'native.png';assert not native.exists();shutil.copy2(host,native)
ref=lambda f:{'file':str(f),'sha256':p.sha(f)}
im=Image.open(native).convert('RGB');assert im.size==(1254,1254) and p.sha(host)==p.sha(native)
p.write_json(D/'generation.json',{'id':'shared-east-lower-03','file':str(native),'sha256':p.sha(native),'sourceHostFile':str(host),'sourceHostSha256':p.sha(host),'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'request':ref(D/'request.json'),'toolReceipt':ref(D/'tool-receipt.json'),'worldBox':[19853,26776,21107,28030],'tileOrigins':{'r07_c05':[3469,2200],'r07_c06':[-627,2200]},'nativePixels':[1254,1254],'sourceResampled':False,'status':'mixed_result_local_rois_pending_review','wholeSourceApproved':False,'createdAtUtc':datetime.now(timezone.utc).isoformat()},replace=False)
base=Image.open(T/'bridges/shared-east-lower-02/trial-native-roi.png').convert('RGB');roi=[606,795,657,910];trial=base.copy();trial.paste(im.crop(roi),(roi[0],roi[1]));trial.save(D/'trial-bottom-only.png')
for name,b in [('original-top-attempt',[567,175,687,255]),('original-middle-attempt',[557,677,717,817]),('bottom-detail',[567,765,697,940])]:im.crop(b).save(D/(name+'.png'))
for name,b in [('trial-bottom-detail',[567,765,697,940]),('trial-top-perimeter',[576,765,687,825]),('trial-bottom-perimeter',[576,880,687,940]),('trial-left-perimeter',[576,775,636,930]),('trial-right-perimeter',[627,775,687,930])]:trial.crop(b).save(D/(name+'.png'))
p.write_json(D/'trial-bottom-only.json',{'candidate':ref(D/'trial-bottom-only.png'),'base':ref(T/'bridges/shared-east-lower-02/trial-native-roi.png'),'source':ref(native),'sourceROI':roi,'worldROI':[19853+roi[0],26776+roi[1],19853+roi[2],26776+roi[3]],'splitSourceROIs':{'r07_c05':[606,795,627,910],'r07_c06':[627,795,657,910]},'tileROIs':{'r07_c05':[4075,2995,4096,3110],'r07_c06':[0,2995,30,3110]},'status':'pending_visual_review','sourceResampled':False,'formalAccepted':False},replace=False)
print({'sourceSha256':p.sha(native),'trial':str(D/'trial-bottom-only.png')})
