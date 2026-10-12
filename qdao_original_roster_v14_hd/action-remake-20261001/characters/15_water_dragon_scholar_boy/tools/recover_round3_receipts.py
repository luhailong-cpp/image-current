import json,re
from pathlib import Path
p=Path(r'C:/Users/luyua/.codex/sessions/2026/10/01/rollout-2026-10-01T10-05-31-01a0f7c8-c88d-7143-b0a2-59c6a573049f.jsonl')
need=['8accfa05','7e8fc0f9','e269540f','2022b810','2381f20a','c5b7d3bb','621c98da','6afe8935']
for line in p.open(encoding='utf-8'):
 if any(s in line for s in need):
  j=json.loads(line); pl=j.get('payload',{})
  if pl.get('type') in ('function_call_output','custom_tool_call_output'):
   out=pl.get('output','')
   if isinstance(out,str):
    for match in re.finditer(r'.{0,150}(?:key.{0,60}|exec-(?:8accfa05|7e8fc0f9|e269540f|2022b810|2381f20a|c5b7d3bb|621c98da|6afe8935)).{0,170}',out):
     print(j.get('timestamp'),pl.get('call_id'),match.group(0)[:330])

