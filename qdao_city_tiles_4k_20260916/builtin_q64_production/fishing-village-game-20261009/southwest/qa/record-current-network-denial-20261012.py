import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
p=json.loads((z/'progress.json').read_text(encoding='utf-8-sig'))
e={'observedAtUtc':prod.now(),'operation':'normal resumption of art_qa, stair_rebuild, finish_r10c05 agents','error':'Fatal error: application network permission was revoked','status':'current_network_permission_denied','response':'No network bypass or repeated retries. Continue local QA and save all successful outputs.'}
p.setdefault('errors',[]).append(e);p['status']='local_qa_continues_network_permission_denied';p['nextStep']='Review all saved r11c05 native joins and complete available local assembly; new network generation blocked.';prod.write(z/'progress.json',p)
prod.write(z/'network-permission-denial-20261012.json',e)

