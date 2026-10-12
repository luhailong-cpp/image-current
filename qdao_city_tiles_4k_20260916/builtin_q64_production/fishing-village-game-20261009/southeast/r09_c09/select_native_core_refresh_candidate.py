from pathlib import Path
import json
R=Path(__file__).resolve().parent
s=json.loads((R/'selected-patches.json').read_text())
s['patches']['p23']='native/p23-v2.png';s['patches']['p34']='native/p34-v2.png'
s.update(status='native_core_refresh_candidate_pending_QA',internalReady=False,formalAccepted=False)
(R/'selected-patches-core-refresh-v1.json').write_text(json.dumps(s,indent=2),encoding='utf-8')

