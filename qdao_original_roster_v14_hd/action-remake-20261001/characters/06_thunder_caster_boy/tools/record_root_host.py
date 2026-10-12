"""Archive native provenance and optionally export a root-owned candidate."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('source');p.add_argument('--review',default='候选，待逐帧及动态验收');p.add_argument('--export',action='store_true');p.add_argument('--replace',action='store_true');a=p.parse_args()
cmd=[sys.executable,'-B',str(ROOT/'tools/record_frame.py'),a.source,a.stem,(ROOT/'prompts'/f'{a.stem}.txt').read_text(encoding='utf-8-sig'),'--references',str(ROOT/'records'/f'{a.stem}_references.json'),'--review',a.review]
if a.export and not a.replace:
 action,direction,frame=a.stem.split('_')[:3]
 cmd+=['--action',action,'--direction',direction,'--frame',str(int(frame))]
subprocess.run(cmd,check=True)
if a.replace:
 action,direction,frame=a.stem.split('_')[:3]
 subprocess.run([sys.executable,'-B',str(ROOT/'tools/assign_existing_native.py'),a.stem,action,direction,str(int(frame)),a.review],check=True)
