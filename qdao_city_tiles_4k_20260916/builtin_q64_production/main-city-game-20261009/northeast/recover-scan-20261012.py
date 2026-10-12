from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent
sources=set();mirrors={}
for f in Z.rglob('*.generation.json'):
 try:
  j=json.loads(f.read_text(encoding='utf-8-sig'))
  if j.get('route','').startswith('builtin'):
   if j.get('sourceOutputPath'):sources.add(str(Path(j['sourceOutputPath']).resolve()).lower())
   if j.get('sha256'):mirrors[j['sha256']]=j.get('file')
 except (OSError,ValueError):pass
root=Path('C:/Users/luyua/.codex/generated_images')
orphans=[];verified=0
for tid in ['01a12075-ff24-76d0-ac68-97861111ddb0','01a12555-5d16-7b23-9669-fa5ccc375294','01a12556-0e70-7380-96c1-1af9b358adf7']:
 p=root/tid
 if not p.exists():continue
 for f in p.glob('*.png'):
  if f.stat().st_mtime<1791763200:continue
  h=hashlib.sha256(f.read_bytes()).hexdigest()
  if h in mirrors:verified+=1
  elif str(f.resolve()).lower() not in sources:orphans.append({'file':str(f),'sha256':h})
r={'checkedPriorThreadOutputs':verified,'unmirroredSuccessfulOutputFiles':orphans}
print(json.dumps(r))
(Z/'resume-recovery-20261012-current.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
