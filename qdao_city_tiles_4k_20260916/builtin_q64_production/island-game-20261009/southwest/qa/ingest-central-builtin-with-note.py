from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
stem,source,note=sys.argv[1:4]
for script,args in [('expansion_central_worker.py',['ingest',stem,source]),('qa/finalize-central-native-evidence.py',[stem]),('expansion_central_worker.py',['select',stem,note])]:
 subprocess.run([sys.executable,str(root/script),*args],cwd=root,check=True)
