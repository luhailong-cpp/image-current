import sys
from workflow import ROOT,read,write,now
f=ROOT/'selection-r12_c11.json';s=read(f)
for arg in sys.argv[1:]:
 rc,ver=arg.split('=');assert (ROOT/'native'/f'r12_c11_p{rc}_{ver}.png').exists();s['patchVersions'][rc]=ver
write(f,s)
f=ROOT/'progress-r12_c11.json';p=read(f);p.update({'selectedCoordinateCount':len(s['patchVersions']),'generatedNativeCount':len(list((ROOT/'native').glob('r12_c11_*.png'))),'updatedAt':now(),'pendingFindings':s.get('pendingFindings',[]),'missingPatches':['r12_c11_p'+str(r)+str(c) for r in range(1,5) for c in range(1,5) if str(r)+str(c) not in s['patchVersions']]});write(f,p)
print(s['patchVersions'])
