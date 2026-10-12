"""Character-only timing comparison; never edits production poses or assumes contact approval."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from current_run_pairs import current_run_pairs
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'preview'/'timing-grounding-20261003';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs=current_run_pairs()
data={'character':'06 雷法少年','status':'正常1×960ms已采用；手脚接地继续复核','normalCycleMs':960,'slowCycleMs':3840,'selectedNormalCycleMs':960,'defaultCycleMs':960,'durationsMs':[60]*16,'client':'未接入、未验证位移速度与滑步','viewSizePx':240,'viewSizeNote':'离线240像素对照，实际客户端显示尺寸待接入确认','referenceGround':{'y':942,'verified':False,'note':'仅原清单诊断参考，不是已标定脚底'},'sequences':{}}
for d in ['N','NE','E','SE','S','SW','W','NW']:
 paths=[ROOT/f'runtime/run/{d}/{i:02d}.png' for i in range(16)]
 if not all(p.exists() for p in paths):continue
 refs=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in paths]
 data['sequences'][d]={'frames':refs,'phaseStatus':'需按实图确认；不沿用其他角色相位权重','sourceCount':16,'uniformTrials':{str(c):[c//16]*16 for c in [960,3840]}}
 phase_file=ROOT/'review'/f'run_{d}_grounding_phase_20261003.json'
 if phase_file.exists():
  phase=json.loads(phase_file.read_text(encoding='utf-8-sig'))
  indexed={f['index']:f for f in phase.get('frames',[])}
  data['sequences'][d]['observedPhases']=[{'index':i,'phase':indexed.get(i,{}).get('observedPhase','未审'),'evidence':indexed.get(i,{}).get('pixelEvidence',''),'note':indexed.get(i,{}).get('note',''),'matchesCurrentFrame':indexed.get(i,{}).get('sha256')==refs[i]['sha256']} for i in range(16)]
  data['sequences'][d]['phaseRecord']=phase_file.relative_to(ROOT).as_posix()
 current=[pairs.get(f['file']) for f in refs]
 if all(current):
  data['sequences'][d]['observedPhases']=[{'index':i,'phase':c['supportLeg']+' · '+c['positionPhase'],'evidence':'配对帧 '+('/'.join(f'{n:02d}' for n in c['pairFrames']))+'，两张独立姿态共120ms','note':'脚位沿运动方向与透视推进；客户端未标定','matchesCurrentFrame':True} for i,c in enumerate(current)]
  data['sequences'][d]['phaseStatus']='已按当前实图列出每两帧位置与支撑脚，待用户最终动态观感确认'
  data['sequences'][d]['phaseRecord']=sorted({c['sourceReview'] for c in current})
 for cycle in [960,3840]:
  frames=[]
  for i,p in enumerate(paths):
   canvas=Image.new('RGB',(240,270),'#eeeade');im=Image.open(p).convert('RGBA').resize((240,240),Image.Resampling.LANCZOS);canvas.paste(im,(0,0),im)
   draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',12);draw.text((8,247),f'{d} · {i:02d} · {cycle}ms/圈 · 待验',fill='#254b41',font=font);frames.append(canvas)
  dest=OUT/f'run_{d}_{cycle}ms.webp';frames[0].save(dest,save_all=True,append_images=frames[1:],duration=cycle//16,loop=0,lossless=True,method=4)
  record={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'operation':'Fixed full-canvas 240px presentation, identical source frames, uniform timing trial only; no pose edits','derivedFrom':refs,'durationMs':[cycle//16]*16,'cycleMs':cycle,'visualApproval':False,'clientVerified':False}
  dest.with_name(dest.name+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'review-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
template=(ROOT/'tools'/'timing_grounding_template.html').read_text(encoding='utf-8')
(OUT/'index.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False)),encoding='utf-8')
print(json.dumps({'directions':list(data['sequences']),'index':str(OUT/'index.html'),'normalTiming':960},ensure_ascii=False))
