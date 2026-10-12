from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
for n in [1,2,3,6,7,8,9,10,11,12]:
 slot=f'attack-E-{n:02d}-v8-arm'
 rec=json.loads((R/'provenance'/f'{slot}.receipt.json').read_text(encoding='utf-8'))
 path=re.search(r'as (C:.*?\.png) by default',rec['output_hint']).group(1)
 subprocess.run([sys.executable,str(R/'tools/register_root.py'),path,slot,'--request',f'provenance/{slot}.request.json'],check=True)

