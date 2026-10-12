from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
from PIL import Image,ImageChops
name='r06_c11_junction_r2_c2-v1'
plan=w.read(w.R/f'{name}.plan.json')
host=Path('C:/Users/luyua/.codex/generated_images/01a13004-3711-7343-a016-7bdb371d0ccc/exec-6eebe363-e3f3-4d98-98d2-6206877d42a8.png')
dst=w.Z/f'native/{name}-west_sol.png'
if dst.exists():assert w.sha(dst)==w.sha(host)
else:shutil.copyfile(host,dst)
im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
args=w.read(w.R/f'{name}.actual-arguments.json');rr=w.read(w.R/f'{name}.receipt.json');assert rr['request']==args
gen=dict(plan);gen.update(file=str(dst),sha256=w.sha(dst),nativeSize=list(im.size),source=w.ref(host),receipt=w.ref(w.R/f'{name}.receipt.json'),tool='image_gen.imagegen',route='builtin',request=args,submittedParameters=dict(model=None,quality=None,transparent_background=False),nativeResizePerformed=False,status='junction_native_candidate_pending_edge_QA');w.write(Path(str(dst)+'.generation.json'),gen)
base=Image.open(plan['base']['path']).convert('RGB');b=plan['proposedContributionBox']
trial=base.copy();trial.paste(im.crop(b),(b[0],b[1]))
qa=w.Z/f'qa/west_sol/{name}-trial';qa.mkdir(parents=True,exist_ok=False)
q=qa/'contribution.native-1to1.png';trial.save(q)
strips=[]
for s,bb in [('left',[b[0]-128,b[1],b[0]+128,b[3]]),('right',[b[2]-128,b[1],b[2]+128,b[3]]),('top',[b[0],b[1]-128,b[2],b[1]+128])]:
 out=trial.crop(bb);p=qa/f'{s}.native-1to1.png';out.save(p);strips.append(dict(side=s,**w.ref(p),sourceBox=bb,operation='exact integer crop/paste, no resample'))
w.write(qa/'construction.json',dict(source=w.ref(dst),base=plan['base'],sourceContributionBox=b,worldContributionBox=[plan['nativeGlobalBox'][0]+b[0],plan['nativeGlobalBox'][1]+b[1],plan['nativeGlobalBox'][0]+b[2],plan['nativeGlobalBox'][1]+b[3]],trial=w.ref(q),strips=strips,bottomBoundary='At source bottom; final patch extends beyond source and must be checked with original native.',formalAccepted=False))
print(w.sha(dst))

