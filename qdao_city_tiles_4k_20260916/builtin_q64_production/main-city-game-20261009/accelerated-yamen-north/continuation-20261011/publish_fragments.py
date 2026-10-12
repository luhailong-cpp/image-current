import sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
mf=ROOT/'r03_c05/continuation-20261011/fragments-v1/integration-manifest.json';d=p.read(mf)
subprocess.run([sys.executable,str(ROOT/'select_derivation.py'),'r03_c05']+[e['patch']+'='+e['relativePath'] for e in d['exports']],check=True)
subprocess.run([sys.executable,str(ROOT/'publish_integration.py'),str(mf)],check=True)

