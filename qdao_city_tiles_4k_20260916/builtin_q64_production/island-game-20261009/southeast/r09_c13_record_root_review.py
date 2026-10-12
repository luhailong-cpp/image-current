from pathlib import Path
from workflow import ROOT,read,write,sha,now
files=['qa/r09p42-p43-shifted.png','qa/r09_c12.junction_32-v02.png','qa/r10_c12_h12-repair_v01.hard-insert.png','qa/r10_c12-v02/h12.png']+[f'qa/r09_c12-v02-r10_c12-v02.south-border-{i}.png' for i in range(1,5)]
tiles=[ROOT/'tiles/r09_c12.candidate-v02.png',ROOT/'tiles/r10_c12.candidate-v02.png']
report={'reviewedAt':now(),'reviewer':'tile_right independent reviewer for root-produced changes','scope':'delta review of listed eight native QA images only; not re-review of all unmodified internal seams','files':[{'file':str(ROOT/f),'sha256':sha(ROOT/f),'status':'independent_candidate_pass'} for f in files],'candidates':[{'file':str(p),'sha256':sha(p)} for p in tiles],'findings':[],'notes':['r09c12 shifted cut: wall/base contour and paving flow continuously, no conspicuous hard boundary. Junction32 has continuous plaster shading.','r10c12 h12 repaired paving: stone joints, grain, shadows and cylinder contour remain continuous through local insert borders.','Four assembled r09/r10 cross-border segments: stair, column base, paving joints and rack feet align with no visible major split.'],'formalAccepted':False}
write(ROOT/'qa/r09_c13-agent-root-delta-review.json',report)
print(report['candidates'])

