import json,pathlib
p=pathlib.Path('C:/Users/luyua/.codex/sessions/2026/10/13/rollout-2026-10-13T04-29-14-01a13461-4bfa-7ea2-ba83-e14e8aa09f34.jsonl')
with p.open('rb') as f:
 f.seek(max(0,p.stat().st_size-5000000)); raw=f.read().decode('utf-8',errors='replace').splitlines()
print('bytes',p.stat().st_size)
for line in raw[-30:]:
 try: o=json.loads(line)
 except: continue
 payload=o.get('payload',{})
 if payload.get('type')=='custom_tool_call_output':
  print('CALL OUTPUT',o.get('timestamp'),payload.get('call_id'))
  for item in payload.get('output',[]) if isinstance(payload.get('output'),list) else []:
   if item.get('type')=='input_text': print(item.get('text','')[:8000])
 elif o.get('type')=='event_msg' and payload.get('type') in ['task_complete','error','agent_message']:
  print(str(payload)[:4000])
b=pathlib.Path(__file__).resolve().parents[2]
for t in ['r15_c05','r16_c05']:
 print('RECENT',t)
 for p in (b/t).rglob('*restart*json'):
  if 'request' not in p.name and 'derivation' not in p.name: print(str(p.relative_to(b)),p.stat().st_size)
print('HELPER')
print((b/'pipeline-tools/col5-record-step-20261013.py').read_text(encoding='utf-8'))
