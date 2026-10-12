import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
q=Path(__file__).resolve().parent;ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
w=q/'block2x2-r09r10c05c06-v1-r09_c05-context-native.png';e=q/'pair-r09c06-c07-northupdate-v1-r09_c06-context-native.png'
assert ref(w)['sha256']=='71e7daf16654c7b70da51e1fd1f29a42df1c409575e88af3e2e396675f99aba2'
m={'outputPrefix':'pair-r09c05-c06-northupdate-v1','inputs':[{'tile':'r09_c05','context':ref(w)},{'tile':'r09_c06','context':ref(e)}],'provenance':[ref(q/'block2x2-r09r10c05c06-v1-trace.json'),ref(q/'pair-r09c06-c07-northupdate-v1-trace.json')]}
p=q/(m['outputPrefix']+'.manifest.json');assert not p.exists();p.write_text(json.dumps(m,indent=2),encoding='utf-8')

