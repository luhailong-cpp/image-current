"""One fixed transform per direction; never aligns individual frames."""
from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
if len(m['frames'])!=68:raise ValueError('All68 final frames required before calibration')
for f in m['frames']:
 p=ROOT/f['file'];g=json.loads((ROOT/f['sourceRecord']).read_text(encoding='utf-8'))
 if sha(p)!=f['sha256'] or sha(p)!=g.get('sha256'):
  raise ValueError('Stale manifest/source record; rebuild and audit first: '+f['file'])
 cal=g.get('finalDirectionCalibration')
 if cal and (cal.get('translationPx')!=[0,{'E':-15,'W':-4}[f['direction']]] or cal.get('outputSHA256')!=sha(p)):
  raise ValueError('Existing calibration does not match final pixels: '+f['file'])
updates=[]
for f in m['frames']:
 p=ROOT/f['file']; r=ROOT/f['sourceRecord']; g=json.loads(r.read_text(encoding='utf-8'))
 dy={'E':-15,'W':-4}[f['direction']]
 if g.get('finalDirectionCalibration'):
  if sha(p)!=g['sha256']:raise ValueError('Previously calibrated image changed without refreshed generation record')
  continue
 old=sha(p)
 im=Image.open(p).convert('RGBA'); canvas=Image.new('RGBA',(1024,1024),(0,0,0,0));canvas.paste(im,(0,dy));canvas.save(p)
 cal={'type':'fixed-direction-canvas-translation','translationPx':[0,dy], 'appliesToAllActionsOfDirection':True,'perFrameAlignment':False,'basis':'Design reference visible alpha>16 baseline E957/W946 moved to942; no individual frame registration','inputSHA256':old,'outputSHA256':sha(p),'at':datetime.now(timezone.utc).isoformat()}
 g['preCalibrationExport']={'sha256':old,'operation':g.get('operation'),'imageRetained':False,'reason':'uniform final direction calibration replaces pre-export; source model evidence retained'}
 g['finalDirectionCalibration']=cal;g['sha256']=sha(p);g['operation']={'pipeline':[g.get('operation'),cal]}
 if 'technical' in g:g['technical']['finalSHA256']=sha(p)
 r.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
 updates.append({'file':f['file'],**cal})
all_operations=[{'file':f['file'],**json.loads((ROOT/f['sourceRecord']).read_text(encoding='utf-8'))['finalDirectionCalibration']} for f in m['frames']]
(ROOT/'records/final-direction-calibration.json').write_text(json.dumps({'operations':all_operations,'singleTransformPerDirection':True,'allFramesIndependentlyAIGeneratedBeforeTransform':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'calibrated':len(updates),'directions':{'E':[0,-15],'W':[0,-4]}}))
