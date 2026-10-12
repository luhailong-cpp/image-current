from native_work import *
name='r05_c14-v2-20261012';q=ZONE/'qa'/f'{name}-final'
files=[q/n for n in ['core-3-1-100pct.png','core-4-1-100pct.png','horizontal-3-segment-1-100pct.png','cross-3-1-100pct.png']]
p=ZONE/'qa'/f'{name}-root-independent-spotreview-20261013.json';assert not p.exists()
write(p,{'tileId':'r05_c14','candidate':read(ZONE/'selection-r05_c14.json')['candidatePath'],'reviewer':'root','reviewedAtUtc':now(),'scope':'independent spot inspection around cabinet foot and repaired paving; supplements worker full49 review','status':'passed','images':[{'file':str(f),'sha256':sha(f),'inspectionScale':1,'resized':False,'status':'passed_visual_100pct'} for f in files],'finding':'Cabinet wood edges, gray paving joints and leaf shadows continue without straight rectangular paint band; repaired lower ground and rock edge remain continuous.','formalAccepted':False})
print(str(p))
