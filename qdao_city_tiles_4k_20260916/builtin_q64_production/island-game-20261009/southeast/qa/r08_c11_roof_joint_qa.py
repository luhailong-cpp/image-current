from pathlib import Path
from PIL import Image
import os,json,hashlib
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.new('RGB',(4608,4352));p34=Image.open(R/'native/r08_c11_p34_v01.png').convert('RGB');p44=Image.open(R/'native/r08_c11_p44_v01.png').convert('RGB');p43=Image.open(R/'native/r08_c11_p43_v02.png').convert('RGB');j=Image.open(R/'native/r08_c11_roof_joint_v01.png').convert('RGB');east=Image.open(R/'tiles/r08_c12.candidate-v15.png').convert('RGB')
im.paste(p34.crop((0,0,1254,1139)),(2957,1933));im.paste(p44,(2957,2957));im.paste(p43.crop((115,115,1139,1139)),(2048,3072));im.paste(east.crop((0,0,512,4096)),(4096,0))
im.paste(j.crop((115,115,1139,1139)),(3072,2528));out=Q/'roof-joint-core-trial.png';im.save(out)
e=[]
for name,box in [('top',[3072,2272,4096,2784]),('bottom',[3072,3296,4096,3808]),('right',[3840,2528,4352,3552]),('left-lower',[2816,3072,3328,3552]),('left-upper-halo-only',[2957,2528,3187,3072]),('old-join',[3072,2816,4096,3328])]:
 f=Q/f'roof-joint-{name}.png';im.crop(box).save(f);e.append({'file':str(f),'sha256':sh(f),'tileCrop':box,'nativeScale':True,'scope':'Context halo only, p33 not yet generated' if name=='left-upper-halo-only' else 'Actual generated neighboring core/candidate pixels'})
(Q/'roof-joint-core-trial.json').write_text(json.dumps({'status':'pending_visual_QA','native':str(R/'native/r08_c11_roof_joint_v01.png'),'nativeSha256':sh(R/'native/r08_c11_roof_joint_v01.png'),'sourceCrop':[115,115,1139,1139],'destinationBox':[3072,2528,4096,3552],'evidence':e,'partialBlackAreasNotFinalArt':True,'formalAccepted':False},indent=2))
print('Saved exact1024 repair-core trial and six native-scale edge crops.')
