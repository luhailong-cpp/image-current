from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
from PIL import Image,ImageChops
name='r06_c11_counterwest-rightclosure-v3';plan=w.read(w.R/f'{name}.plan.json');gb=plan['nativeGlobalBox'];b=plan['proposedContributionBox'];wg=[gb[0]+b[0],gb[1]+b[1],gb[0]+b[2],gb[1]+b[3]]
host=Path('C:/Users/luyua/.codex/generated_images/01a13004-3711-7343-a016-7bdb371d0ccc/exec-60fe69d7-6f10-473e-9d58-058ab03466d2.png');src=w.Z/f'native/{name}-west_sol.png';assert not src.exists();shutil.copyfile(host,src);gen=Image.open(src).convert('RGB');assert gen.size==(1254,1254)
rr=w.read(w.R/f'{name}.receipt.json');args=w.read(w.R/f'{name}.actual-arguments.json');assert rr['request']==args
d=dict(plan);d.update(file=str(src),sha256=w.sha(src),nativeSize=list(gen.size),source=w.ref(host),receipt=w.ref(w.R/f'{name}.receipt.json'),tool='image_gen.imagegen',route='builtin',request=args,submittedParameters=dict(model=None,quality=None,transparent_background=False),nativeResizePerformed=False,status='native_candidate_pending_review');w.write(Path(str(src)+'.generation.json'),d)
base=Image.open(plan['base']['path']).convert('RGB');trial=base.copy();trial.paste(gen.crop(b),(b[0],b[1]));qa=w.Z/f'qa/west_sol/{name}-trial';qa.mkdir(parents=True,exist_ok=False);tp=qa/'contribution.native-1to1.png';trial.save(tp);strips=[]
for side,bb in [('left',[b[0]-128,b[1],b[0]+128,b[3]]),('right',[b[2]-128,b[1],b[2]+128,b[3]]),('top',[b[0],b[1]-128,b[2],b[1]+128]),('bottom',[b[0],b[3]-128,b[2],min(1254,b[3]+124)])]:
 qp=qa/f'{side}.native-1to1.png';trial.crop(bb).save(qp);strips.append(dict(side=side,**w.ref(qp),sourceBox=bb,operation='exact integer crop/paste no resize'))
records=[]
for item in plan['originalQuadrants']:
 patch=item['patch']
 if '_p3' not in patch and '_p4' not in patch:continue
 e=item['source'];co=e['coordinates'];nb=co['nativeGlobalBox'];t=[max(nb[0],wg[0]),max(nb[1],wg[1]),min(nb[2],wg[2]),min(nb[3],wg[3])]
 if t[0]>=t[2] or t[1]>=t[3]:continue
 sc=[t[0]-gb[0],t[1]-gb[1],t[2]-gb[0],t[3]-gb[1]];at=[t[0]-nb[0],t[1]-nb[1]];tb=[at[0],at[1],at[0]+t[2]-t[0],at[1]+t[3]-t[1]]
 original=Image.open(e['path']).convert('RGB');out=original.copy();out.paste(gen.crop(sc),at)
 mask=Image.new('1',out.size,1);mask.paste(0,tb)
 assert ImageChops.multiply(ImageChops.difference(out,original).convert('L'),mask.convert('L')).getbbox() is None
 assert ImageChops.difference(out.crop(tb),gen.crop(sc)).getbbox() is None
 dst=w.Z/f'native/{patch}-rightclosure-v3-west_sol.png';assert not dst.exists();out.save(dst)
 w.write(Path(str(dst)+'.derived.json'),dict(schemaVersion=1,patchId=patch,version='rightclosure-v3',nativeGlobalBox=nb,nativeCoreBox=co['nativeCoreBox'],nativeSize=[1254,1254],file=str(dst),sha256=w.sha(dst),base=e,nativeGeneratedSource=w.ref(src),sourceCropBox=sc,targetPasteAt=list(at[:2]),targetContributionBox=tb,worldContributionBox=t,operation='exact integer native crop/paste; no resize/paint/feather',proof=dict(outsideBaseUnchanged=True,insideReturnedNativeExact=True),formalAccepted=False))
 records.append(dict(patch=patch,**w.ref(dst),sourceCropBox=sc,targetPasteAt=list(at[:2]),worldContributionBox=t))
w.write(w.R/f'{name}.derivation-trial.json',dict(source=w.ref(src),generatedSourceWorldBox=gb,sourceContributionBox=b,worldContributionBox=wg,patches=records,formalAccepted=False,selected=False))
w.write(qa/'construction.json',dict(base=plan['base'],source=w.ref(src),trial=w.ref(tp),sourceContributionBox=b,worldContributionBox=wg,strips=strips,formalAccepted=False))
print(records)
