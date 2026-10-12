import json,sys,shutil
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]));import pipeline as p
receipt=p.read(HERE/'tool-result-v1.json');shutil.copy2(receipt['hostSource'],HERE/'raw-v1.png')
a=np.array(Image.open(HERE/'context-native.png').convert('RGB'));b=np.array(Image.open(HERE/'raw-v1.png').convert('RGB'));assert a.shape==b.shape==(1254,1254,3)
y,x=np.indices((1254,1254))
def s(v,lo,hi):
 t=np.clip((v-lo)/(hi-lo),0,1);return t*t*(3-2*t)
alpha=np.rint(255*s(x,587,592)*(1-s(x,632,637))*s(y,440,520)*(1-s(y,715,790))).astype('uint8')
z=((a.astype('uint32')*(255-alpha[...,None])+b.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
assert np.array_equal(z[alpha==0],a[alpha==0])
out=p.save_png(HERE/'derived-v1.png',Image.fromarray(z));mask=p.save_png(HERE/'alpha-v1.png',Image.fromarray(alpha))
p.save_png(HERE/'qa-detail-native.png',Image.fromarray(z).crop((530,450,690,850)))
record={**p.read(HERE/'preparation.json'),'rawFile':str(HERE/'raw-v1.png'),'rawSHA256':p.sha(HERE/'raw-v1.png'),'rawHostSource':receipt['hostSource'],'rawNativePixels':[1254,1254],'submittedParameters':p.read(HERE/'parameters-v1.json'),'actualModel':None,'actualQuality':None,'derived':out,'alpha':mask,'alphaFormula':'round(255*s(x,587,592)*(1-s(x,632,637))*s(y,440,520)*(1-s(y,715,790))), s=smoothstep','blendFormula':'(base*(255-alpha)+raw*alpha+127)//255','resizedAfterGeneration':False,'finalArtUpscaled':False,'spatialBlur':False,'formalAccepted':False,'verifiedOutsideSupportUnchanged':True}
p.put_json(HERE/'derivation-v1.json',record)
spec={'tile':'r04_c04','baseCandidate':record['baseCandidate'],'outputDirectory':'gold-tone-repair/integrated-native-v1','contexts':[{'tileBox':record['contextTileBox'],'derivedFile':out['file'],'supportFile':mask['file'],'manifest':str(HERE/'derivation-v1.json')}]}
p.put_json(HERE/'integration-spec-v1.json',spec)
