from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent.parent
def rd(p): return json.loads(p.read_text(encoding='utf8'))
def wr(p,x): p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
stem='r10_c04_s04_02_v02'
req=rd(R/'prompts/r10_c04_s04_02_v01.request.json')
base=R/'native/r10_c04_s04_02_v01.png';right=R/'native/r10_c04_s04_03_v01.png';top=R/'guides/r10_c04_s03_02_v02.postfoot-context.png'
guide=R/'guides'/(stem+'.native-overlap-guide.png');assert not guide.exists()
im=Image.open(base).convert('RGB');im.paste(Image.open(right).crop((0,0,230,1254)),(1024,0));im.paste(Image.open(top).crop((0,1024,1254,1254)),(0,0));im.save(guide)
wr(Path(str(guide)+'.derivation.json'),{'operation':'same-coordinate native source crop/paste guide only, original sources unchanged; no resampling','nativeGlobalBox':req['coordinates']['nativeGlobalBox'],'sources':[{'path':base.as_posix(),'sha256':sha(base),'crop':[0,0,1254,1254],'destination':[0,0]},{'path':right.as_posix(),'sha256':sha(right),'crop':[0,0,230,1254],'destination':[1024,0]},{'path':top.as_posix(),'sha256':sha(top),'crop':[0,1024,1254,1254],'destination':[0,0]}],'sha256':sha(guide)})
req['references'][0]={'path':guide.as_posix(),'sha256':sha(guide),'dimensions':[1254,1254],'role':'precise edit target: v01 plus actual fixed TOP/RIGHT; remove right half geometry step with AI'}
req['references'][1]={'path':right.as_posix(),'sha256':sha(right),'dimensions':[1254,1254],'role':'right neighbor only, fixed native continuation and tile-row scale'}
req['repairOf']='r10_c04_s04_02_v01';req['repairReason']='Gold/red curve and blue rows shifted about 100px downward at RIGHT core seam; correct whole curved geometry, keep true native right strip.'
wr(R/'prompts'/(stem+'.request.json'),req);wr(R/'prompts'/(stem+'.coordinates.json'),req['coordinates'])
wr(R/'qa/r10_c04_s04_02_v01-rejection.json',{'status':'rejected','reason':req['repairReason'],'nativeEvidence':'qa/r10_c04_s04_02_v01-right-column-right-native100.png'})
for ref in req['references']: assert sha(Path(ref['path']))==ref['sha256']
print(json.dumps({'guide':guide.as_posix(),'refs':[x['path'] for x in req['references']]}))
