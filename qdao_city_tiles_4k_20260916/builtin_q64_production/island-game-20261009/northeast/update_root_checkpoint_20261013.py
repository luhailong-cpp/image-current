from native_work import *
p=ZONE/'resume_20261012.py';s=p.read_text(encoding='utf-8');s=s.replace("activeCoordinates=['r03_c09','r04_c10','r05_c11','r06_c12','r06_c14']", "activeCoordinates=['r03_c09','r04_c09','r06_c12','r06_c14']").replace("'west':'r04_c10'", "'west':'r04_c09'");p.write_text(s,encoding='utf-8')
name='r05_c11-continued-v2-20261013'
p=ZONE/'qa'/f'{name}-root-independent-spotreview-20261013.json';assert not p.exists()
f=ZONE/'qa'/f'{name}-final/vertical-3-segment-1-100pct.png'
candidate=Path(read(ZONE/'selection-r05_c11.json')['candidatePath'])
write(p,{'tileId':'r05_c11','candidate':str(candidate),'candidateSha256':sha(candidate),'reviewer':'root','reviewedAtUtc':now(),'scope':'Previously viewed preview and exact vertical3-segment1 at 1:1; confirms worker pending issue','status':'requires_native_background_detail_repair','images':[{'file':str(f),'sha256':sha(f),'inspectionScale':1,'resized':False,'status':'failed_sharpness_continuity'}],'finding':'Sharp stone on left meets visibly blurred paving on right at x3072. Keep best v2 selected and defer concentrated repair after two unsuccessful local attempts. This is not a pass.','formalAccepted':False})
print('Updated worker queue and recorded r05_c11 unresolved spot finding')

