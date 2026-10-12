"""Scoped repair evidence using the preserved configuration snapshot only."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v2', HERE.parent / 'production_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
LOCAL = HERE / 'qa/native-repair-20261012'
CONFIG = LOCAL / 'config/image-generation.json'
SOURCE = HERE / 'receipts/s04_04_resume01.request.json'
snapshot = v2.read(SOURCE)['configurationSnapshot']
if not CONFIG.exists():
    v2.write_json(CONFIG,snapshot)
    v2.write_json(LOCAL / 'configuration-snapshot-provenance.json',
                  dict(source=str(SOURCE),sourceSha256=v2.sha(SOURCE),configuration=str(CONFIG),
                       configurationSha256=v2.sha(CONFIG),createdAt=v2.now(),
                       meaning='Historical requested settings copied only for evidence bookkeeping. '
                               'No backend model or quality selector is submitted to the built-in tool.',
                       actualModel=None,actualQuality=None,globalConfigurationWritten=False))
elif v2.read(CONFIG) != snapshot:
    raise RuntimeError('Scoped historical configuration changed')
v2.REPO = LOCAL
parser = argparse.ArgumentParser()
parser.add_argument('command',choices=['request','ingest'])
parser.add_argument('--id',required=True)
parser.add_argument('--args-file')
parser.add_argument('--roles-file')
parser.add_argument('--source')
parser.add_argument('--receipt')
args = parser.parse_args()
if args.command == 'request':
    result = v2.record_request(HERE.name,args.id,args.args_file,args.roles_file)
else:
    result = v2.ingest(HERE.name,args.id,args.source,args.receipt)
print(json.dumps(result,ensure_ascii=False))
