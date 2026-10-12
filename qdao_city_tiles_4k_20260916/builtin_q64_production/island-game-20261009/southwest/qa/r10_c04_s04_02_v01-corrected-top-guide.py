from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
s='r10_c04_s04_02_v01'
reqp=R/'prompts'/(s+'.request.json');req=read(reqp)
assert not (R/'prompts'/(s+'.prompt.txt')).exists()
base=R/'native/r10_c04_s03_02_v02.png'
repair=R/'native/r10_c04_postfoot_join_v01.png'
context=R/'guides/r10_c04_s03_02_v02.postfoot-context.png'
assert not context.exists()
canvas=Image.open(base).convert('RGB');part=Image.open(repair).convert('RGB')
canvas.paste(part.crop((0,0,951,1254)),(303,0));canvas.save(context)
save(Path(str(context)+'.derivation.json'),{'operation':'same global coordinate crop/paste for next-generation TOP constraint only; no interpolation/color/shift; original native unchanged','nativeGlobalBox':[13197,38797,14451,40051],'sources':[{'path':base.as_posix(),'sha256':sha(base),'crop':[0,0,1254,1254],'destination':[0,0]},{'path':repair.as_posix(),'sha256':sha(repair),'nativeGlobalBox':[13500,38797,14754,40051],'crop':[0,0,951,1254],'destination':[303,0]}],'sha256':sha(context)})
guide=R/'guides'/(s+'.native-overlap-guide.png');oldsha=sha(guide)
g=Image.open(guide).convert('RGB');g.paste(part.crop((0,1024,951,1254)),(303,0));g.save(guide)
dp=Path(str(guide)+'.derivation.json');d=read(dp)
d['priorGuideSha256']=oldsha;d['postfootCorrection']={'path':repair.as_posix(),'sha256':sha(repair),'globalIntersection':[13500,39821,14451,40051],'sourceCrop':[0,1024,951,1254],'destinationTopLeft':[303,0],'operation':'same-coordinate native crop/paste after neighbors; repair wins TOP corner'};d['sha256']=sha(guide);save(dp,d)
req['references'][0]['sha256']=sha(guide)
req['references'][0]['role']='coordinate edit target; corrected native TOP 230px and RIGHT 230px constrain geometry; blurred remainder layout only'
req['references'][1]={'path':context.as_posix(),'sha256':sha(context),'dimensions':[1254,1254],'role':'above native context with actual whole postfoot AI repair pasted at same global coordinates'}
req['correctedTopSource']='r10_c04_postfoot_join_v01';req['correctedTopDerivation']=str(context)+'.derivation.json';save(reqp,req)
rp=R/'qa/r10_c04_s03_02_v02-rejection.json';hist=read(rp)
hist['historicalDecision']={'status':hist['status'],'reason':hist['reason']};hist['status']='structure_clear_base_pending_whole_repair';hist['reason']='Use v02 as structure-clear base together with r10_c04_postfoot_join_v01 whole-foot repair; narrow-strip v03 remains rejected.';hist['repairHandoff']='qa/r10_c04_postfoot_join_v01-handoff.json';save(rp,hist)
for ref in req['references']:
    assert sha(Path(ref['path']))==ref['sha256']
print(json.dumps({'guide':guide.as_posix(),'context':context.as_posix(),'allFiveReferenceHashesMatch':True}))
