from pathlib import Path
import json
D=Path(__file__).resolve().parent
req=json.loads((D/'bench-G3-left-conditioned-v10.request.json').read_text(encoding='utf-8-sig'));req.update({'adoptGuideBox':[585,480,762,585],'adoptWorldBox':[31135,40680,31312,40785],'actualGenerationReuse':'Same v10 builtin output; mechanical native crop reaches actual bevel intersection at x762'})
p=D/'bench-G3-left-conditioned-v10b.request.json';assert not p.exists();p.write_text(json.dumps(req,indent=2),encoding='utf-8')
j=json.loads((D/'bench-G3-left-conditioned-v10.job.json').read_text(encoding='utf-8-sig'));j.update({'stem':'bench-G3-left-conditioned-v10b','adoptGuideBox':[585,480,762,585],'adoptWorldBox':[31135,40680,31312,40785],'evidenceGuideBoxes':{'left':[521,448,649,617],'top':[585,416,762,544],'right':[698,448,826,617],'bottom':[585,521,762,649],'center':[451,256,826,924]}})
p=D/'bench-G3-left-conditioned-v10b.job.json';assert not p.exists();p.write_text(json.dumps(j,indent=2),encoding='utf-8')

