from workflow import *
from PIL import Image
import numpy as np
im=Image.open(ROOT/'tiles/r11_c12.candidate-v01.png').convert('RGB')
prior=read(ROOT/'qa/capacity-gate/r11_c12-partial/index.json')
rows=[]
for e in prior['entries']:
 a=Image.open(e['file']).convert('RGB');b=im.crop(e['sourceCrop'])
 rows.append({'id':e['id'],'matchesPriorReviewedPixels':np.array_equal(np.array(a),np.array(b)),'priorFile':e['file'],'priorStatus':e['status']})
assert all(e['matchesPriorReviewedPixels'] for e in rows)
write(ROOT/'qa/r11_c12-v01/prior-reviewed-pixel-replay.json',{'entries':rows,'allMatch':True})
north=Image.open(ROOT/'tiles/r10_c12.candidate-v02.png').convert('RGB');es=[]
for c in range(4):
 out=ROOT/'qa/r11_c12-v01'/f'north-{c+1}.png';q=Image.new('RGB',(1024,512));q.paste(north.crop((c*1024,3840,(c+1)*1024,4096)),(0,0));q.paste(im.crop((c*1024,0,(c+1)*1024,256)),(0,256));q.save(out)
 es.append({'file':str(out),'sha256':sha(out),'northSourceCrop':[c*1024,3840,(c+1)*1024,4096],'southSourceCrop':[c*1024,0,(c+1)*1024,256]})
write(ROOT/'qa/r11_c12-v01/north-edge.json',{'sources':['tiles/r10_c12.candidate-v02.png','tiles/r11_c12.candidate-v01.png'],'entries':es,'operation':'unscaled exact crops and hard paste'})
print('17 prior-reviewed crops pixel-identical; 4 north edge samples saved')

