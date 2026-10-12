from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
from PIL import Image,ImageChops
name='r06_c11_junction_r2_c2-v1';plan=w.read(w.R/f'{name}.plan.json');gb=plan['nativeGlobalBox'];b=plan['proposedContributionBox'];wg=[gb[0]+b[0],gb[1]+b[1],gb[0]+b[2],gb[1]+b[3]]
src=w.Z/f'native/{name}-west_sol.png';gen=Image.open(src).convert('RGB');qa=w.Z/f'qa/west_sol/{name}-trial'
records=[]
for item in plan['originalQuadrants']:
 e=item['source'];co=e['coordinates'];nb=co['nativeGlobalBox'];t=[max(nb[0],wg[0]),max(nb[1],wg[1]),min(nb[2],wg[2]),min(nb[3],wg[3])]
 if t[0]>=t[2] or t[1]>=t[3]:continue
 sc=[t[0]-gb[0],t[1]-gb[1],t[2]-gb[0],t[3]-gb[1]];at=[t[0]-nb[0],t[1]-nb[1]];tb=[at[0],at[1],at[0]+t[2]-t[0],at[1]+t[3]-t[1]]
 base=Image.open(e['path']).convert('RGB');out=base.copy();out.paste(gen.crop(sc),at)
 mask=Image.new('1',out.size,1);mask.paste(0,tb)
 assert ImageChops.multiply(ImageChops.difference(out,base).convert('L'),mask.convert('L')).getbbox() is None
 assert ImageChops.difference(out.crop(tb),gen.crop(sc)).getbbox() is None
 patch=item['patch'];dst=w.Z/f'native/{patch}-junction-r2c2-v1-west_sol.png';assert not dst.exists();out.save(dst)
 w.write(Path(str(dst)+'.derived.json'),dict(schemaVersion=1,patchId=patch,version='junction-r2c2-v1',nativeGlobalBox=nb,nativeCoreBox=co['nativeCoreBox'],nativeSize=[1254,1254],file=str(dst),sha256=w.sha(dst),base=e,nativeGeneratedSource=w.ref(src),sourceCropBox=sc,targetPasteAt=at,targetContributionBox=tb,worldContributionBox=t,operation='exact integer native crop/paste; no resize/paint/feather',proof=dict(outsideBaseUnchanged=True,insideReturnedNativeExact=True),formalAccepted=False))
 records.append(dict(patch=patch,**w.ref(dst),sourceCropBox=sc,targetPasteAt=at,worldContributionBox=t))
worldbox=[wg[0],wg[3]-128,wg[2],wg[3]+128]
bottom=Image.new('RGB',(wg[2]-wg[0],256))
for item in plan['originalQuadrants']:
 e=item['source'];co=e['coordinates'];cb=co['coreGlobalBox'];nb=co['nativeGlobalBox'];t=[max(cb[0],worldbox[0]),max(cb[1],worldbox[1]),min(cb[2],worldbox[2]),min(cb[3],worldbox[3])]
 if t[0]>=t[2] or t[1]>=t[3]:continue
 bottom.paste(Image.open(e['path']).crop([t[0]-nb[0],t[1]-nb[1],t[2]-nb[0],t[3]-nb[1]]),[t[0]-worldbox[0],t[1]-worldbox[1]])
bottom.paste(gen.crop([b[0],b[3]-128,b[2],b[3]]),(0,0));bp=qa/'bottom.native-1to1.png';bottom.save(bp)
w.write(w.R/f'{name}.derivation-trial.json',dict(source=w.ref(src),generatedSourceWorldBox=gb,sourceContributionBox=b,worldContributionBox=wg,patches=records,bottomQA=w.ref(bp),formalAccepted=False,selected=False))
print(records)

