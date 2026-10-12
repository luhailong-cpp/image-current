from native_work import *
# Register recovered native and its inspected right join without touching neighboring source status.
p=ZONE/'native/r03_c11_p01_01.png.generation.json';q=read(p);q.update(status='usable_native_candidate',internalSeams='root1:1 right join passed; other edges pending');write(p,q)
p=ZONE/'qa/r03_c11_p01_01__r03_c11_p01_02.json';q=read(p);q.update(status='passed_internal_only',reviewer='root',reviewedAtUtc=now(),geometryChecks={'lantern':'continuous','leaves':'continuous','color':'pass'});write(p,q)
s={'tileId':'r03_c11','cores':[
['r03_c11_p01_01','r03_c11_p01_02','r03_c11_p01_03','r03_c11_p01_04'],
[None,'r03_c11_p02_02','r03_c11_p02_03','r03_c11_p02_04'],
[None,'r03_c11_p03_02','r03_c11_p03_03_v3','r03_c11_p03_04'],
[None,'r03_c11_p04_02','r03_c11_p04_03_v2','r03_c11_p04_04']],
'overlays':[],'selectionIsPartialCandidate':True,'pendingIssues':[{'id':'r03_c11-stair-riser','status':'requires_native_generation','affectedCores':['r03_c11_p03_03_v3','r03_c11_p03_04'],'finding':'lowest stair height tapers into ground at right join; geometry not passed'},{'id':'r03_c11-paving-junction','status':'requires_native_generation','affectedCores':['r03_c11_p03_03_v3','r03_c11_p03_04','r03_c11_p04_03_v2','r03_c11_p04_04'],'finding':'paving joins and tone mismatch at 4core corner'}],'formalAccepted':False,'updatedAtUtc':now()}
assert not (ZONE/'selection-r03_c11.json').exists();write(ZONE/'selection-r03_c11.json',s)
for ident in ['r03_c11_p03_03_v3','r03_c11_p04_03_v2']:
 p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='candidate_with_unresolved_geometry',requiredRepair='r03_c11 stair or adjacent paving junction');write(p,q)
for ident in ['r05_c13_p02_03_v3','r05_c13_p02_04_v2']:
 p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='candidate_with_unresolved_geometry',requiredRepair='two gold roof edge bars step at shared join, native joint repaint required');write(p,q)
p=ZONE/'selection-r05_c13.json';s=read(p);s['pendingIssues']=[{'id':'r05_c13-roof-gold-join','status':'requires_native_generation','affectedCoordinates':['p02_03','p02_04'],'candidateIds':['r05_c13_p02_03_v3','r05_c13_p02_04_v2'],'finding':'gold edging height discontinuity between two cores; p02_03_v2 selected earlier but not final accepted'}];write(p,s)
# Generic sparse work-in-progress PNGs preserve missing regions as transparent, never filled.
for tid in ['r03_c11','r05_c12','r05_c13']:
 s=read(ZONE/f'selection-{tid}.json');im=Image.new('RGBA',(4096,4096),(0,0,0,0));sources=[];missing=[]
 for r,line in enumerate(s['cores']):
  for c,ident in enumerate(line):
   if ident is None:missing.append(f'p{r+1:02}_{c+1:02}');continue
   p=ZONE/'native'/f'{ident}.png';rec=read(p.with_suffix('.png.generation.json'));assert sha(p)==rec['sha256'];im.paste(Image.open(p).convert('RGBA').crop((115,115,1139,1139)),(c*1024,r*1024));sources.append({'id':ident,'sha256':sha(p),'file':p.as_posix(),'crop':[115,115,1139,1139],'paste':[c*1024,r*1024]})
 dest=ZONE/'qa'/f'{tid}-sparse-wip-20261011.png';assert not dest.exists();im.save(dest)
 write(dest.with_suffix('.png.derivation.json'),{'status':'incomplete_work_in_progress_not_complete_tile','tileId':tid,'size':[4096,4096],'file':dest.as_posix(),'sha256':sha(dest),'coreCoverage':len(sources),'missingCoreCoordinates':missing,'missingRegionTransparent':True,'sources':sources,'pendingIssues':s.get('pendingIssues',[]),'finalArtUpscaled':False,'resampling':'none'})
print('recovered13core r03_c11 candidate; sparse WIP exports3, unresolved geometry explicitly recorded')

