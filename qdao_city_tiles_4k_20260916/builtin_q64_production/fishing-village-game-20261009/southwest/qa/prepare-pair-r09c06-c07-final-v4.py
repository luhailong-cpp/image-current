import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
Q=Path(__file__).resolve().parent;m=json.loads((Q/'pair-r09c06-c07-final-v3.manifest.json').read_text());m['outputPrefix']='pair-r09c06-c07-final-v4';m['repairs'][3]['clipPolygon']=[[466,429],[724,594],[724,654],[714,656],[466,501]]
(Q/(m['outputPrefix']+'.manifest.json')).write_text(json.dumps(m,indent=2)+'\n')

