from workflow import ROOT,read,write,sha,now
from pathlib import Path
s=read(ROOT/'selection-r12_c11.json');p=read(ROOT/'progress-r12_c11.json')
files=sorted((ROOT/'native').glob('r12_c11_*.png'))
p.update({'updatedAt':now(),'generatedNativeCount':len(files),'selectedCoordinateCount':len(s['patchVersions']),'inFlightRequests':[],'nativeInventory':[{'file':str(f),'sha256':sha(f),'hasGenerationRecord':Path(str(f)+'.generation.json').exists()} for f in files],'missingPatches':['r12_c11_p'+str(r)+str(c) for r in range(1,5) for c in range(1,5) if str(r)+str(c) not in s['patchVersions']],'pendingFindings':['p13v01 input moderation rejected, no native, no retry; only this coordinate blocked','p21v02 narrow water stripe remains visible near native x1024, pending local repair','p34v01 guide uses withdrawn r12c12p31v01 anchor; preserve but never submit; wait corrected east source'],'formalAcceptedCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'status':'generating_with_coordinate_block_and_quality_findings'})
write(ROOT/'progress-r12_c11.json',p)
j=read(ROOT/'continuation-r12_c11-left-20261011.json');j.update({'updatedAt':now(),'actualNativeCount':len(files),'selectedCoordinateCount':len(s['patchVersions']),'selectedVersions':s['patchVersions'],'pendingFindings':p['pendingFindings'],'currentCoordinate':p['currentPatch'],'lastActualNative':str(files[-1]) if files else None,'formalAcceptedCount':0});write(ROOT/'continuation-r12_c11-left-20261011.json',j)
print({'natives':len(files),'selected':len(s['patchVersions']),'missing':p['missingPatches']})
