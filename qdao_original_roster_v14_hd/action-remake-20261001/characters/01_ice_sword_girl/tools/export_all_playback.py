from pathlib import Path
from PIL import Image
import json,hashlib,sys
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
report=[]
for s in m['sequences']:
 if not s['complete']:continue
 if '--run-only' in sys.argv and s['action']!='run':continue
 if '--axis-only' in sys.argv and (s['action']!='run' or s['direction'] not in ['E','W']):continue
 if '--full-axis-only' in sys.argv:
  revision=json.loads((R/'review/full-axis-revision-selection-20261005.json').read_text(encoding='utf-8'))
  if (s['action'],s['direction']) not in {(v['action'],v['direction']) for v in revision['changes']}:continue
 frames=[Image.open(R/f['path']).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS) for f in s['frames']]
 out=R/f"preview/{s['action']}-{s['direction']}-1x-{s['cycleMs']}ms.webp"
 frames[0].save(out,save_all=True,append_images=frames[1:],duration=[s['frameMs']]*len(frames),loop=0,lossless=True,method=6)
 evidence={'file':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'previewOnly':True,'frameCount':len(frames),'frameDurationsMs':[s['frameMs']]*len(frames),'sourceFrames':[{'path':f['path'],'sha256':f['sha256']} for f in s['frames']],'operation':'full_canvas_downsample_for_preview_no_alignment_no_interpolation'}
 out.with_name(out.name+'.preview.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report.append(evidence['file'])
print(json.dumps({'exportedPreviews':len(report),'files':report},ensure_ascii=False))
