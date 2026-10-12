from pathlib import Path
import json
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
p=B/'review/axis-revision-decisions-20261004.json'; d=read(p)
specs=[
('N',6,'06-axis-v2',720,'右脚全掌持续支撑，支撑踝鞋向本腿髋下收正，左脚抬起。','支撑鞋中心由原749.5收至720，减小05到07间的向外凸出；未达到提示目标700。'),
('NW',12,'12-axis-v2',750,'近左脚持续承重，右摆腿从后方经身体下方前摆，保持西北鞋轴。','右摆鞋由原约475移至550，使11约760到13约455的路径更连贯；未达到目标600，不能称逐帧等距。'),
('SW',14,'14-axis-v1',None,'右脚后段持续支撑，左摆腿向西南前伸，避免在13与15之间重新缩回膝下。','原明显摆脚回缩已消除；新摆鞋比13与15稍前，仍有约45至55px原生画布的推进不均，不能称匀速轨迹。')]
for direction,frame,stem,x,phase,finding in specs:
    src=f'generation/{direction}/{stem}.png'; meta=read(B/(src+'.generation.json'))
    assert (B/src).is_file()
    old=read(B/f'review/run-{direction}-sequence-input.json')['frames'][frame-1]['source']
    assert not any(i['direction']==direction and i['frame']==frame for i in d['decisions'])
    item=dict(direction=direction,frame=frame,source=src,replaces=old,observedPhase=phase,finding=finding,issues=[finding,'保留原生画布，手和法器未换；未采用整图移动或逐帧贴底。'],review=f'generation/{direction}/{stem}.review.json')
    if x is not None: item['contactPointNative']=[x,meta['alphaGt8Bounds'][3]-1]
    d['decisions'].append(item)
    if direction in ('N','NW'):
        oldstem=stem.replace('v2','v1')
        d['rejectedAttempts'].append(dict(source=f'generation/{direction}/{oldstem}.png',reason='第一版仅部分改变，第二版继续改善，采用v2。'))
assert len(d['decisions'])==7
d['status']='ready_for_selection'
d['independentNEReview']='NE08/15/16新图与旧稿及07/09/14/01邻帧已独立复核，无新增反向脚尖、明确悬空或持物换手；原生底部高度差分别-3、-17、-14px已记录。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ready':len(d['decisions'])}))
