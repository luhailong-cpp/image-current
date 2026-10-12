import sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
index=p.read(ROOT/'continuation-20261011/merged-south-v3/output-index.json')
for item in index:
 (ROOT/item['tile']/'receipts').mkdir(exist_ok=True)
 args=[sys.executable,str(ROOT/'select_derivation.py'),item['tile']]+[e['patch']+'='+e['relativePath'] for e in item['exports']]
 subprocess.run(args,check=True)
 subprocess.run([sys.executable,str(ROOT/'publish_integration.py'),item['manifest']],check=True)

