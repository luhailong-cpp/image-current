import json,datetime
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'provenance/run/grounding-NW-20261003.json'
d=json.loads(p.read_text(encoding='utf-8-sig'))
trace=[
('near_LEFT','近LEFT前景裤腿低位承重，远RIGHT裤腿在后方高折，低鞋朝NW/画面左。','keep'),
('near_LEFT','近LEFT膝压缩、低靴平掌，远RIGHT后跟仍高；鞋轴随胫骨没有独立外旋。','keep'),
('near_LEFT','近LEFT低靴承重恢复，远RIGHT脚跟回收到身后；高折露底是俯仰，不判外八。','keep'),
('near_LEFT','低位大裤腿/大靴为近LEFT；左前小摆腿被袖与裙摆遮住为远RIGHT，鞋尖左向。与12区别主要在前后遮挡及远摆腿更小。','keep_with_independent_readability_review'),
('near_LEFT_forefoot','近LEFT后大靴抬跟、趾端低，远RIGHT较小前鞋上提；两足沿同一NW矢状平面。','keep_with_independent_readability_review'),
('near_LEFT_toeoff','近LEFT后大腿伸踝最后蹬地，远RIGHT前小腿前摆；后脚尖向下是蹬地俯仰，无横向外八。','keep_with_independent_readability_review'),
('none','双脚腾空；近LEFT后鞋大且露底，远RIGHT前鞋较小。','keep'),
('far_RIGHT_pending','远RIGHT前小鞋下降转薄底侧面；近LEFT后大靴高折，近侧大裤腿在前景。','keep'),
('far_RIGHT','远RIGHT低腿部分被前景近LEFT大腿遮挡、前小鞋近水平；近LEFT高折靴大且露底。不是01近腿承重的重复。','keep'),
('far_RIGHT','低位远RIGHT小腿从近LEFT大回收裤腿后露出，近LEFT高折靴遮在低腿前；支撑靴在身体下。','keep'),
('far_RIGHT','近LEFT大腿已前提，位于画面左前；远RIGHT低支撑裤腿在其后。支撑靴因相对身体后移而落在中右，未见无故换腿。','keep'),
('far_RIGHT','近LEFT左前裤腿大且在前景，远RIGHT裤腿低位在后；与04的小远摆腿/大近支撑腿深度顺序相反。','keep'),
('far_RIGHT_forefoot','近LEFT前膝上抬、前鞋头朝画面左；远RIGHT后靴跟高趾低。鞋轴与膝踝一致，左下位置不是外撇。','keep'),
('far_RIGHT_toeoff','远RIGHT后腿继续伸踝蹬离；近LEFT前鞋头左向，膝踝同向，未见鞋掌横拧。','keep'),
('none','近LEFT前伸、远RIGHT后折，双脚短暂腾空；前鞋头左向/底边可见属于翘尖，不是横向外八。','keep'),
('near_LEFT_pending','近LEFT前腿下降，鞋头左向且与膝踝前伸方向一致；远RIGHT后靴高折，衔接01近左接触。','keep')]
for row,(support,obs,decision) in zip(d['frames'],trace):
 row['observedSupport']=support
 row['anatomicalTrace']=obs
 row['footDirectionReview']={'decision':decision,'toeOutObserved':False,'evidence':obs}
 row['phaseNote']='静态近远腿追踪已完成；相邻帧时间分配、根配准和地面速度需整圈动态。'
d['reviewedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
d['staticAnatomicalConclusion']='以裤腿遮挡、大小和髋膝连接判定：01–06近LEFT支撑；08/09–14远RIGHT支撑；07/15腾空；16近LEFT下降。支撑靴从屏左移动中右可由足相对身体后移解释，不自动视为换腿。04/12轮廓近似，但近远深度不同；独立代理审读性增强。'
d['staticFootDirectionConclusion']='当前NW16帧均未发现独立于膝踝的明确鞋掌外旋；13–16前鞋朝NW画面左，保留。'
d['redrawRequiredNow']=[]
d['independentReadabilityReview']={'frames':[4,5,6],'owner':'finish_ew','selection':'provenance/run/selection-NW04-06.json','reason':'强化两半周期深度差异；先判断必要性，当前静态不是仅靠屏幕位置认定错腿。'}
d['unresolved']=['04–06独立近远腿可读性审查结果需根代理合并。','01/02的静态压低差较小，需连播评价承重感。','固定尺度根配准、全周期速度、逐帧时长与客户端滑步仍未验收；正式通过仍0。']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p)

