from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa'/'native-repairs';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mask=Image.open(Q/'m03-mask.png').convert('L');pix=mask.load()
for y in range(600,1254):
 for x in range(300,384):pix[x,y]=round(255*min(1,(x-300+1)/16,(y-600+1)/16))
p=Q/'m03-shared-full-mask.png';mask.save(p)
record={'native':str(T/'native'/'m03.png'),'nativeSha256':sha(T/'native'/'m03.png'),'mask':str(p),'maskSha256':sha(p),'originRelativeToR07c14':[-384,2842],'westCropLocalBox':[300,600,384,1254],'westPasteTileBox':[4012,3442,4096,4096],'westOrigin':[3712,2842],'eastIntegratedMask':str(Q/'m03-mask.png'),'inputRecord':str(Q/'m03-input.json'),'notes':'Use exact same native/mask; west only x<384. Own tile integrated x>=384. 16px taper only on outer left and top of west strip; no taper at shared boundary.'}
(Q/'m03-shared-handoff.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record))
