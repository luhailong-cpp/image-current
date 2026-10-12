import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];QA=Z/'qa';ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
a=QA/'joint-r09c05-r10c05-v1-r09_c05-context-native.png';b=QA/'repair-r09_c06-final-v4-context-native.png';assert ref(a)['sha256']=='87316f19ec4b457d4a201d090c888a0745266d42da4b6ef736bebd563799cd19';assert ref(b)['sha256']=='fecb07cada0b889066e07a0b5f7805a45807c424f7bd4ee61a6bc334cd9c51a6'
m={'schemaVersion':1,'outputPrefix':'pair-r09c05-c06-v1','inputs':[{'tile':'r09_c05','context':ref(a)},{'tile':'r09_c06','context':ref(b)}],'provenance':[ref(QA/'joint-r09c05-r10c05-v1-trace.json'),ref(QA/'repair-r09_c06-final-v4-trace.json'),ref(QA/'repair-r09_c06-final-v4-internal-qa.json')],'repairTargets':[]}
p=QA/'pair-r09c05-c06-v1.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(ref(p))
