from pathlib import Path
import ast,json,importlib.util
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;R=W.parent
spec=importlib.util.spec_from_file_location('assembly',R/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
wm=m.read(W/'tiles/r03_c02.candidate.assembly.json');sources=wm['sources'];patches={s['sourceId']:np.array(Image.open(R/s['file']).convert('RGB')) for s in sources}
bridges=[(17,0,'r03_c02_s01_c03_c04_bridge_v01'),(18,2,'r03_c02_s03_c02_c03_bridge_v01'),(19,0,'r03_c02_c03_roof_bridge_v01')]
tree=ast.parse((W/'assemble.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compose');fn.body[-1]=ast.parse('return canvas[115:4211,115:].copy(),ids[115:4211,115:].copy(),seams').body[0];ast.fix_missing_locations(fn);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<read-only-compose-extract>','exec'))
west,wi,ws=compose(False)
plan=m.read(R/'assembly-plan.json');col=[s for s in plan['sources'] if s['column']==1]
for j,s in enumerate(col):
 a=np.array(Image.open(R/s['file']).convert('RGB'));ai=np.full((1254,1254),50+s['sourceId'],np.uint8)
 if j==0:halo,hi=a,ai
 else:
  p,i,d=m.append_hard(halo.transpose(1,0,2),hi.T,a.transpose(1,0,2),ai.T,'east-original-west-halo');halo,hi=p.transpose(1,0,2),i.T
eastpath=R/'tiles/r03_c03.candidate-repair-v5.png';eid=R/'tiles/r03_c03.source-id-repair-v5.png';em=m.read(R/'tiles/r03_c03.repair-v5.assembly.json')
assert m.sha(eastpath)==em['candidate']['sha256'];ep=np.array(Image.open(eastpath).convert('RGB'));ei=np.array(Image.open(eid))+50
east=np.concatenate([halo[115:4211,:115],ep],axis=1);ei=np.concatenate([hi[115:4211,:115],ei],axis=1)
pair,ids,cut=m.append_hard(west,wi,east,ei,'r03c02-r03c03-full-height-native230')
bridge=patches[19][115:];x=7565-4096;y=0;old=pair[:1139,x:x+1254].copy();L,lc=m.minimum_vertical_seam(old[:,:115],bridge[:,:115]);RR,rc=m.minimum_vertical_seam(bridge[:,1139:],old[:,1139:]);RR+=1139;B,bc=m.minimum_vertical_seam(bridge[1024:].transpose(1,0,2),old[1024:].transpose(1,0,2));B+=1024
mask=(np.arange(1254)[None,:]>=L[:,None])&(np.arange(1254)[None,:]<RR[:,None])&(np.arange(1139)[:,None]<B[None,:]);pair[:1139,x:x+1254]=np.where(mask[...,None],bridge,old);ids[:1139,x:x+1254]=np.where(mask,19,ids[:1139,x:x+1254])
allsource={s['sourceId']:{'file':str(R/s['file']),'box':s['globalNativeBox'],'sha256':s['sha256']} for s in sources}
for s in em['sources']:allsource[50+s['sourceId']]={'file':s['file'],'box':[8192+s['nativeBox'][0],8192+s['nativeBox'][1],8192+s['nativeBox'][2],8192+s['nativeBox'][3]],'sha256':s['sha256']}
counts=[]
for sid in np.unique(ids):
 s=allsource[int(sid)];p=Path(s['file']);assert m.sha(p)==s['sha256'];a=np.array(Image.open(p).convert('RGB'));ys,xs=np.nonzero(ids==sid);sx=xs+4096-s['box'][0];sy=ys+8192-s['box'][1];assert np.array_equal(pair[ys,xs],a[sy,sx]);counts.append({'sourceId':int(sid),'pixels':len(xs)})
prefix=W/'qa/east-full-height-gate';belt=pair[:,3696:4496];bid=ids[:,3696:4496];Image.fromarray(belt).save(str(prefix)+'.png');Image.fromarray(bid).save(str(prefix)+'.source-id.png')
crops=[]
for j in range(4):
 p=str(prefix)+f'.segment{j+1}.100pct.png';Image.fromarray(belt[j*1024:(j+1)*1024]).save(p);crops.append({'file':p,'globalBox':[7792,8192+j*1024,8592,9216+j*1024]})
for j in range(1,4):
 p=str(prefix)+f'.intersection{j}.100pct.png';Image.fromarray(belt[j*1024-300:j*1024+300]).save(p);crops.append({'file':p,'globalBox':[7792,8192+j*1024-300,8592,8192+j*1024+300]})
out={'role':'diagnostic only, no shared final pixels updated','formalAccepted':False,'westManifest':str(W/'tiles/r03_c02.candidate.assembly.json'),'eastManifest':str(R/'tiles/r03_c03.repair-v5.assembly.json'),'eastCandidateSHA256':m.sha(eastpath),'method':'true230px full-height min-squared-error DP using west native east halo and east native west halo/current repaired core; root approved roof bridge forced core with115side/bottom DP','fullPairGlobalBox':[4096,8192,12288,12288],'beltGlobalBox':[7792,8192,8592,12288],'nativePixelsVerified':int(pair.shape[0]*pair.shape[1]),'mismatchedPixels':0,'sources':allsource,'contributions':counts,'eastCut':cut,'roofBridgeCut':{'leftXByY':L.tolist(),'rightXByY':RR.tolist(),'bottomYByX':B.tolist(),'globalOrigin':[7565,8192]},'crops':crops,'file':str(prefix)+'.png','sha256':m.sha(str(prefix)+'.png')};m.write_json(Path(str(prefix)+'.json'),out);print(json.dumps({'belt':str(prefix)+'.png','sha256':out['sha256'],'nativePixelsVerified':out['nativePixelsVerified']}))
