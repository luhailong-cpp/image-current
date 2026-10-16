from native_work import *
name='r06_c14-native-v1-20261013';q=ZONE/'qa'/f'{name}-final';p=ZONE/'qa'/f'{name}-root-independent-spotreview-20261013.json';assert not p.exists()
files=[q/n for n in ['cross-3-1-100pct.png','vertical-2-segment-4-100pct.png','cross-3-3-100pct.png']]
candidate=Path(read(ZONE/'selection-r06_c14.json')['candidatePath'])
write(p,{'tileId':'r06_c14','candidate':str(candidate),'candidateSha256':sha(candidate),'reviewer':'root','reviewedAtUtc':now(),'scope':'Preview and exact 1:1 spot inspection of repaired blossom boundary and rock crossings; complements worker full49 review','status':'passed_spot_only','images':[{'file':str(f),'sha256':sha(f),'inspectionScale':1,'resized':False,'status':'passed_visual_100pct'} for f in files],'finding':'Blossom petals, branches and rounded rocks continue across inspected seams; no straight rectangular cutoff in these spots. Full49 and external boundary state remains per worker review.','formalAccepted':False})
print(str(p))

