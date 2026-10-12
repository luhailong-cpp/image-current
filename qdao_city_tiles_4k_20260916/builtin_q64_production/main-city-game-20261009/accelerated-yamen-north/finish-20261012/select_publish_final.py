import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pipeline as p
import subprocess
ROOT=p.ROOT;py=sys.executable
for tile in ['r03_c04','r03_c05','r04_c04','r04_c05']:
 mfile=ROOT/tile/'finish-20261012-integrated/integration-manifest.json';m=p.read(mfile)
 command=[py,str(ROOT/'select_derivation.py'),tile]+[e['patch']+'='+e['relativePath'] for e in m['exports']]
 r=subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True);print(tile,'selection',r.stdout.strip())
 r=subprocess.run([py,str(ROOT/'publish_integration.py'),str(mfile)],cwd=ROOT,check=True,capture_output=True,text=True)
 print(r.stdout.strip())

