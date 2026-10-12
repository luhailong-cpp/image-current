from pathlib import Path
import json
b=Path(__file__).resolve().parents[1]
template=(b/'audit/run-E-grounding.html').read_text(encoding='utf8')
for direction in ['NE','W']:
 if direction=='NE':
  data=json.loads((b/'audit/run-NE-review.json').read_text(encoding='utf8'))
  data['snapshotAt']=data['reviewedAt']
 else:
  data=json.loads((b/'audit/run-W-selection.json').read_text(encoding='utf8'))
  data['snapshotAt']='2026-10-03 current W16 selection'
  data['customDurationsMs']=[55,65,60,45,30,25,35,45]*2
  for r in data['frames']:
   r['phaseObserved']=r['event'];r['shoeRegionBottomNative']='见W专项复核';r['shoeRegionBottomExport']='见W专项复核'
  data['clientStatus']='not_integrated';data['status']='offline_review_pending'
 for r in data['frames']:
  r['soleNativeY']=r['shoeRegionBottomNative'];r['soleOutputY']=r['shoeRegionBottomExport']
 (b/'audit'/f'run-{direction}-grounding-review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 html=template.replace(' E ',f' {direction} ').replace(' E',f' {direction}').replace("'E'","'"+direction+"'").replace('run-E-grounding',f'run-{direction}-grounding')
 html=html.replace('50,70,60,40,30,30,35,45,50,70,60,40,30,25,35,50','55,65,60,45,30,25,35,45,55,65,60,45,30,25,35,45')
 html=html.replace('02/03及10/11为承重，飞行峰值缩短；08已达足跟接触高度。','01–04和09–12分配较多接触/承重时间；腾空较短；相位以实图为准。')
 html=html.replace("+'；E02/03后续v3高度未改，未采用。其余新修图未自动混入本比较。'","+'；独立16候选实图，客户端未接入。'")
 html=html.replace("+'；"+direction+"02/03后续v3高度未改，未采用。其余新修图未自动混入本比较。'","+'；独立16候选实图，客户端未接入。'")
 if direction=='NE':
  html=html.replace("x.strokeStyle='#bf5546';x.beginPath();x.moveTo(0,942*s);x.lineTo(size,942*s);x.stroke()","for(const [gy,col]of [[948.5,'#bf5546'],[911,'#568ea0']]){x.strokeStyle=col;x.beginPath();x.moveTo(0,gy*s);x.lineTo(size,gy*s);x.stroke()}")
  html=html.replace('红线为既有942px根点诊断线','红线为近左脚约949px、蓝线远右脚约911px透视诊断线')
 (b/'audit'/f'run-{direction}-grounding.html').write_text(html,encoding='utf8')
print('NE/W comparison pages written')

