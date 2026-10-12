from pathlib import Path
import json
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl')
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'source-selection.json';j=json.loads(p.read_text(encoding='utf-8-sig'))
for n in [2,10]:j['slots'][f'run/N/{n:02}']=f'generation/run-N-{n:02}-v2/native.png'
write(p,j)
order=[1,2,3,4,5,6,7,9,8,10,11,12,13,14,15,16]
p=r/'run-playback-proposals.json';j=json.loads(p.read_text(encoding='utf-8-sig'));j['groups']['run/N']=order
j['basis']='Actual selected pose sequence review. S existing trial order retained; N09 initial contact precedes N08 lowered body/settling. No duplicated poses.'
write(p,j)
phases={1:('左脚承重过渡','N01左平底支撑，右靴在后抬起，承接N16初触地。',1.2),2:('左脚压膝缓冲','N02-v2支撑膝明显弯曲，骨盆/头身下降而左靴保持触点；右靴悬空。',1.4),3:('左脚支撑伸展','左支撑腿伸展，右靴仍屈膝后收，背面遮挡中未单独证实前摆通过。',1.1),4:('左脚抬跟','左靴从平底转为可见倾斜鞋底，左腿向后伸，右脚抬起。',.9),5:('左脚蹬离','左腿后伸、鞋跟抬起，前掌朝下；后方脚的投影可低于中支撑地面。',.85),6:('右领先短腾空','N06-v2双膝弯曲，左后靴较大/近、右前靴较小/远，双脚约1000以上明确离地。',.6),7:('右脚下降过渡','N07-v2右前靴比06下降，双脚仍清楚离地。',.65),9:('右脚初接触','原N09右靴平底触地、左靴后收；排在原N08之前避免二次反向起伏。',1.2),8:('右脚承重下降','原N08头身比09降低、右平底支撑，左靴在后抬起。',1.2),10:('右脚压膝缓冲','N10-v2右膝/踝屈曲、骨盆降低，右靴平底支撑；左脚抬离。',1.4),11:('右脚支撑伸展','右支撑腿伸展、左靴屈膝回收；背面遮挡不把通过标签当实证。',1.1),12:('右脚抬跟','右后脚鞋底逐渐倾斜、跟抬起，左脚在前方抬起。',.9),13:('右脚蹬离','右腿后伸、前掌末端朝下，左靴抬起；手肘/枪角相应变化。',.85),14:('左领先短腾空','右后靴较大、左前靴较小，两脚均离地；未镜像。',.6),15:('左脚下降','左前靴向下展开但仍离地，右脚后收；方向沿前进面。',.65),16:('左脚初接触','实图左脚已经平底接触，并非提示词所称悬空；据实记录，接01承重。',1.2)}
frames=[{'sourceFrame':n,'playbackIndex':i+1,'observedPhase':phases[n][0],'evidence':phases[n][1],'trialWeight':phases[n][2]} for i,n in enumerate(order)]
review={'direction':'N','status':'static-full-sequence-reviewed-offline-playback-pending','order':order,'frames':frames,'root':{'target':[512,942],'translation':[73,134],'sourceVirtualGround':1178,'scale':860/1254,'perFrameFootAlignment':False},'hands':'Two original grips maintained across full sequence, high left/low right. Shoulder/elbow positions and straight shaft slope change subtly across push and recovery. Both anatomical hand identities preserved, no detached hand visible.','feet':'Heel view remains aligned away. Compression02/10 redrawn by joints; flight06/07/14/15 actual airborne. Toe-off04/05 and12/13 distinguish heel lift from flat support.','timing':{'frameMs':75,'selectedCycleMs':1200,'phaseWeightsApplied':False},'visualAccepted':False,'dynamicAccepted':False,'clientAccepted':False}
write(r/'run-N-grounding-review.json',review)
print('N reviewed16 selected')

