from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
xs=[630,630,630,640,638,635,635,640,635,630,630,670,620,635,635,665]
rows=[]
for i,x in enumerate(xs,1):
    p=R/'run'/'E'/f'{i:02d}.png'
    rows.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'srcRoot':[x,980],'basis':'人工全帧带坐标图查看髋中心与腿根投影，虚拟地面980由支撑帧01/02/03/09/10/11共同判定，全组保持。未逐帧最低脚贴地、未独立bbox缩放。','confidence':'manual approx +/-12px; final dynamics pending'})
r={'schemaVersion':1,'coordinateSpace':'whole-canvas1024 before global normalization','globalScale':.8,'targetRoot':[512,942],'applyTransform':False,'method':'manual anatomical hip-root projection; common y980 for complete E run cycle','frames':rows}
(R/'run'/'E'/'registration.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
