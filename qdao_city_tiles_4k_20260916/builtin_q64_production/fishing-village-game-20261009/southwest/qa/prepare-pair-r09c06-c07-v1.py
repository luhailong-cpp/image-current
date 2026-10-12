import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];QA=Z/'qa';ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
a=QA/'pair-r09c05-c06-final-v2-r09_c06-context-native.png';b=QA/'repair-r09_c07-v1-context-native.png';assert ref(a)['sha256']=='c570a6dcde60386581f1cd075a988a07a392f8920c67ffe8b4bed577a26bbebe';assert ref(b)['sha256']=='f28c4ae23202994cac7b450ce2d4a4e7d5b001d7379184c7f4af781fb5697401'
m={'schemaVersion':1,'outputPrefix':'pair-r09c06-c07-v1','inputs':[{'tile':'r09_c06','context':ref(a)},{'tile':'r09_c07','context':ref(b)}],'provenance':[ref(QA/'pair-r09c05-c06-final-v2-trace.json'),ref(QA/'pair-r09c05-c06-final-v2-visual-audit.json'),ref(QA/'repair-r09_c07-v1-trace.json'),ref(QA/'repair-r09_c07-v1-internal-qa.json')],'repairTargets':[]}
p=QA/'pair-r09c06-c07-v1.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(ref(p))
