from pathlib import Path
import argparse, importlib.util, json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v2',HERE.parent/'production_v2.py')
v2=importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
p=argparse.ArgumentParser(); p.add_argument('command',choices=['request','ingest']); p.add_argument('--id',required=True); p.add_argument('--args-file'); p.add_argument('--source'); p.add_argument('--receipt'); a=p.parse_args()
if a.command=='request': result=v2.record_request(HERE.name,a.id,a.args_file)
else: result=v2.ingest(HERE.name,a.id,a.source,a.receipt)
print(json.dumps(result,ensure_ascii=False))
