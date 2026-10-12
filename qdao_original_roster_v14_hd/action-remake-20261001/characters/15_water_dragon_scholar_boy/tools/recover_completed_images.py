import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOG=Path(r'C:/Users/luyua/.codex/sessions/2026/10/01/rollout-2026-10-01T10-05-31-01a0f7c8-c88d-7143-b0a2-59c6a573049f.jsonl')
HOST=Path(r'C:/Users/luyua/.codex/generated_images/01a0f7c8-c88d-7143-b0a2-59c6a573049f')
PREFIXES={'8accfa05','7e8fc0f9','e269540f','2022b810','2381f20a','c5b7d3bb','621c98da','6afe8935','487eb6e6','0bad2864','7f84f7f5','82618851','66a9fdf4','06581718','990f691a'}
requests={}
for p in (ROOT/'provenance/requests').glob('*.json'):
    q=json.loads(p.read_text(encoding='utf-8-sig'))
    if 'submittedParameters' in q: requests[q['submittedParameters'].get('prompt')]=p.stem
seen=set()
for lineno,line in enumerate(LOG.open(encoding='utf-8'),1):
    if not any('exec-'+prefix in line for prefix in PREFIXES): continue
    j=json.loads(line); item=j.get('payload',{}).get('item',{})
    if item.get('kind')!='image_gen.generation' or item.get('status')!='completed': continue
    ident=item.get('id','')
    if not any(ident.startswith('exec-'+prefix) for prefix in PREFIXES): continue
    key=requests.get(item.get('revisedPrompt'))
    if not key: raise ValueError('Unmatched actual prompt '+ident)
    host=HOST/(ident+'.png'); assert host.is_file(),host
    receipt={'tool':'image_gen.imagegen','status':'completed','id':ident,'completedAt':j.get('timestamp'),'hostOutput':str(host),'actualModel':None,'actualQuality':None,'revisedPrompt':item['revisedPrompt'],'recoveredEvidence':{'sessionLog':str(LOG),'line':lineno,'event':'event_msg/item_completed','kind':item['kind']},'note':'Recovered exact completed event and exact prompt match after turn interruption. Binary result excluded; PNG preserved by host.'}
    (ROOT/'provenance/receipts'/f'{key}.tool.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    if not (ROOT/'provenance/generation'/f'{key}.json').exists(): subprocess.run([sys.executable,'-B',str(ROOT/'tools/record_image.py'),key,str(host)],check=True)
    seen.add(ident.split('-')[1]);print(key,ident)
assert seen==PREFIXES,('missing',PREFIXES-seen)
