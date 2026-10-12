from pathlib import Path
from PIL import Image
import json,hashlib,datetime
BASE=Path(__file__).resolve().parents[1]
p=BASE/'review/review-run-S.json';d=json.loads(p.read_text(encoding='utf-8'))
versions={4:4,5:3,6:2,7:5,8:4,11:2,12:2,13:3,14:2,15:5,16:3}
axis_notes={
1:'前靴大致正面，仍有轻微不对称；未在本轮重画，须动态复核。',
2:'支撑靴轻微向画面左侧偏斜；未以站距替代脚轴判定，待复核。',
3:'支撑靴鞋尖/鞋带近居中，膝踝到靴的前进面较直，暂保留。',
4:'v4摆动左靴已由外撇露底改为正向镜头；右支撑靴保留。',
5:'v3摆动左靴正向镜头，鞋尖/鞋跟较居中；支撑右靴仍需推离连续性复核。',
6:'v2左前靴正向镜头，鞋底长轴不再朝画面右侧斜撇；高度较旧稿下移。',
7:'v5左前靴已转为近对称正面；脚轴改善，但轴向重画使靴最低点下移，接地未通过。',
8:'v4保持v3纠正后的正面脚轴；踝膝改画又收得偏高，连续性未通过。',
9:'左前靴近正面且中心鞋带与膝踝同向，暂保留，不宣告全姿势通过。',
10:'承重左靴略向画面右偏斜，待进一步复核；不能因平底接触而自动判脚轴正确。',
11:'承重左靴较直，右回收靴略有外偏；本轮只修毛笔长度，脚轴未宣告通过。',
12:'左支撑靴正面，右抬脚轻微偏斜需动态复核；未动整体像素。',
13:'v3同时纠正两脚向左右撇：两靴鞋尖和鞋底长轴已正向镜头，左膝踝也回到较合理路径；前掌蹬离仍不清楚。',
14:'v2右前靴长轴已正向镜头，鞋跟居中；仍存在前脚高度与相邻帧连续性问题。',
15:'v5右前靴已转正，中心鞋带/鞋尖在同向前进面；脚轴改善但高度随重画下移。',
16:'选择v3：右前靴转正且较接近01高度；v4虽然脚轴仍直，却过度收腿约100px，不选作当前序列。'
}
for f in d['frames']:
 n=f['frame'];path=BASE/'staging'/f'run-S-{n:02d}-v{versions.get(n,1)}.png';old=f['file'];f.update(file=str(path.relative_to(BASE)).replace('\\','/'),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),nativeSize=list(Image.open(path).size),footAxisObservation=axis_notes[n],footAxisApproval=False,approval=False,status='needs_review')
 if old!=f['file']:f.setdefault('supersededReviewSelections',[]).append(old)
 if n in [4,5,6,7,8,13,14,15,16]:f['issues']=['脚轴已局部改善，整段仍需动态复核','接地/腾空高度与邻帧尚未连续','透明边缘彩点']
 if n==11:f['handConnection']='v2笔头已补长，右肩-袖-手-笔连接保留，短笔突变减轻；其他手臂动作仍需动态复核。';f['issues']=['毛笔长度已局部改善，待邻帧动态复核','回收脚略外偏','透明边缘彩点']
 if n==7:f['groundingObservation']='v2靴ROI最低y1215；高度两轮修正v3=1114/v4=1182；随后脚轴转正v5使最低点再下移。禁止用整图位移补偿，未通过。'
 if n==8:f['groundingObservation']='v3脚轴转正但仍低；高度最后一轮v4靴收得偏高，07→08仍可能出现反向收腿。两轮已到，不继续盲重试。'
 if n==15:f['groundingObservation']='v2靴ROI最低y1208；高度两轮修正v3=1092/v4=1166；脚轴转正后v5最低点轻度下移。未通过。'
 if n==16:f['groundingObservation']='v3脚轴转正且高度接近01；v4高度修正过度，约100px收腿，不选。仍需解决16→01微小高度跳变。'
d.update(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),approved=0,priorityRedrawFrames=[7,8,16],otherProblemFrames=[1,2,5,6,10,11,12,13,14,15],footAxisReviewPolicy='最新用户更正：核心是鞋尖/鞋底长轴外撇，不能用两腿间距或平底接触代替方向判定；没有完整已通过角色参照。',normal240pxFindings='局部脚轴纠正后，04/05/06/07/08/13/14/15/16主要摆动脚或双脚已更直朝镜头；13不是仅缩窄站距。完整接地序列仍未通过：07→08回收高度不连续、16v4过收需弃用、部分脚轴细微偏斜与头身/道具尺度跳变仍在。11笔头长度已改善。',retryBounds={'07_descentHeight':2,'15_descentHeight':2,'08_precontactHeight':2,'16_precontactHeight':2,'sameDefectFurtherRetry':'stopped; report remaining problems'},notSelectedCandidates={'run-S-16-v4.png':'高度过度回收，尽管脚轴保持较直；继续选16v3。'})
d['root']['status']='uncalibrated_manual_contact_band_for_diagnosis_only'
d['root']['additionalFinding']='高度诊断见grounding-S/boot-height-diagnostic.json。该ROI最低点只用于核实局部修改，绝不用于逐帧贴地；S01/S09接触轮廓仍不能单独定义全局地面。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('selected',len(d['frames']),'frames;0approved')
