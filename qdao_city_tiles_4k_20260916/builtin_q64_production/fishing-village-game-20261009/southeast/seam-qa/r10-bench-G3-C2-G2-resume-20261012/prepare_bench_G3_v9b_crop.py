from pathlib import Path
import json
D=Path(__file__).resolve().parent
req=json.loads((D/'bench-G3-left-conditioned-v9.request.json').read_text(encoding='utf-8-sig'));req.update({'adoptGuideBox':[585,380,710,470],'adoptWorldBox':[31135,40580,31260,40670],'actualGenerationReuse':'Same v9 builtin output; mechanical native crop reaches actual contour intersection at x710'})
p=D/'bench-G3-left-conditioned-v9b.request.json';assert not p.exists();p.write_text(json.dumps(req,indent=2),encoding='utf-8')
j=json.loads((D/'bench-G3-left-conditioned-v9.job.json').read_text(encoding='utf-8-sig'));j.update({'stem':'bench-G3-left-conditioned-v9b','adoptGuideBox':[585,380,710,470],'adoptWorldBox':[31135,40580,31260,40670],'evidenceGuideBoxes':{'left':[521,348,649,502],'top':[585,316,710,444],'right':[646,348,774,502],'bottom':[585,406,710,534],'center':[451,256,774,924]}})
p=D/'bench-G3-left-conditioned-v9b.job.json';assert not p.exists();p.write_text(json.dumps(j,indent=2),encoding='utf-8')

