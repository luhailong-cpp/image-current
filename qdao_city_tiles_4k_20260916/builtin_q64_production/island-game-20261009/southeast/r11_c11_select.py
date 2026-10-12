import sys
from workflow import ROOT,read,write,now
f=ROOT/'selection-r11_c11.json';s=read(f)
for arg in sys.argv[1:]:
 rc,ver=arg.split('=');assert (ROOT/'native'/f'r11_c11_p{rc}_{ver}.png').exists();s['patchVersions'][rc]=ver
write(f,s)
f=ROOT/'progress-r11_c11.json';p=read(f);p.update({'selectedCoordinateCount':len(s['patchVersions']),'generatedNativeCount':len(list((ROOT/'native').glob('r11_c11_*.png'))),'updatedAt':now(),'pendingFindings':s.get('pendingFindings',[])});write(f,p)
print(s['patchVersions'])
