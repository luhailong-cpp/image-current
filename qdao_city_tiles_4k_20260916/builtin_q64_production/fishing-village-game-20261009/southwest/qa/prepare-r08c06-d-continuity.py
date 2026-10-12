import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((Z/'native/r08_c06_repair_d_canopyright_v2.request.json').read_text(encoding='utf-8'))
old=Path(j['references'][0]['path']);left=Z/'native/r08_c06_repair_c_canopyleft_v2.png';guide=Z/'qa/repair-r08_c06-d_canopyright-v3-continuity.png'
im=Image.open(old).convert('RGB');im.paste(Image.open(left).crop((1024,0,1254,1254)),(0,0));im.save(guide)
j['stem']='r08_c06_repair_d_canopyright_v3'
j['sourceCrop']=j['references'][0]
j['references']=[{'path':guide.as_posix(),'sha256':sha(guide),'dimensions':[1254,1254],'role':'exact native target plus integer-pasted left 230 pixels from completed adjacent repair'}]
j['submittedParameters']['referenced_image_paths']=[guide.as_posix()]
pp=Z/'native/r08_c06_repair_d_canopyright_v3.prompt.txt'
p=(Z/'native/r08_c06_repair_d_canopyright_v2.prompt.txt').read_text(encoding='utf-8')+' The leftmost 230-pixel strip is the corrected adjacent native canopy. Keep it as an exact color, weave scale and geometry anchor; continue its smooth fabric through the angular patch boundaries to the right. Keep the original upper and lower colors, with no collage-like bands or blocks. No extra objects.'
pp.write_text(p,encoding='utf-8');j['prompt']=pp.as_posix()
(Z/'native/r08_c06_repair_d_canopyright_v3.request.json').write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
(Z/'qa/repair-r08_c06-d_canopyright-v3-guide-trace.json').write_text(json.dumps({'operation':'integer paste only','base':{'path':old.as_posix(),'sha256':sha(old)},'insert':{'path':left.as_posix(),'sha256':sha(left)},'sourceBox':[1024,0,1254,1254],'targetBox':[0,0,230,1254],'output':{'path':guide.as_posix(),'sha256':sha(guide)},'nativePixelsResampled':False},indent=2)+'\n',encoding='utf-8')

