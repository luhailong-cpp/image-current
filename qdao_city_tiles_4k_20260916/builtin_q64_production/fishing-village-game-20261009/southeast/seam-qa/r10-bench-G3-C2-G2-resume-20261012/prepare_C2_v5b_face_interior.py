from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent;m=np.zeros((1254,1254),np.uint8)
for x in range(555,711):
 top=round(754-(x-555)*.505);bottom=top+54;m[top+14:bottom-4,x]=255
p=D/'bench-C2-right-conditioned-v5b-gold-face-interior-adopt-mask-native1254.png';assert not p.exists();Image.fromarray(m,'L').save(p)
req=json.loads((D/'bench-C2-right-conditioned-v5.request.json').read_text(encoding='utf-8-sig'))
req.update({'adoptGuideBox':[555,690,711,804],'adoptWorldBox':[32305,40890,32461,41004],'adoptMaskFile':str(p),'actualGenerationReuse':'Same successful v5 builtin invocation; mechanical native adoption mask now excludes contour/bevel'})
(D/'bench-C2-right-conditioned-v5b.request.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
j=json.loads((D/'bench-C2-right-conditioned-v5.job.json').read_text(encoding='utf-8-sig'));j.update({'stem':'bench-C2-right-conditioned-v5b','adoptGuideBox':[555,690,711,804],'adoptWorldBox':[32305,40890,32461,41004],'adoptMaskFile':str(p)})
(D/'bench-C2-right-conditioned-v5b.job.json').write_text(json.dumps(j,indent=2),encoding='utf-8')
print(Image.fromarray(m).getbbox())

