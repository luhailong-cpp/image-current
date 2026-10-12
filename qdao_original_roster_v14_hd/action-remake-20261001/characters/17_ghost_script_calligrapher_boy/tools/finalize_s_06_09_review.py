from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
BASE=Path(__file__).resolve().parents[1]
p=BASE/'review/review-run-S.json';d=json.loads(p.read_text(encoding='utf-8'));now=datetime.now(timezone.utc).isoformat()
by={f['frame']:f for f in d['frames']}
def select(n,v):
 f=by[n];old=f['file'];new=f'staging/run-S-{n:02d}-v{v}.png'
 if old!=new:
  history=f.setdefault('supersededReviewSelections',[])
  if old not in history:history.append(old)
 f['file']=new;f['sha256']=hashlib.sha256((BASE/new).read_bytes()).hexdigest()
 f['nativeSize']=list(Image.open(BASE/new).size)
select(6,3);select(7,6)
by[6].update(observedPhase='左膝屈收的短腾空候选，左前靴开始伸膝下降前的较高位置',supportCandidate='none_airborne_candidate',
 handConnection='以07v6局部改绘膝踝，右肩-袖-笔手与左肩-袖-卷手保留；06/07/08上半身基本一致，尚需检查连续摆臂是否短暂停滞。',
 groundingObservation='06v3前靴ROI最低1036；07v6=1097、08v4=1159、09v1=1190。实际膝踝由屈收到渐伸，替代06v2前靴1182后再屈回的反向动作；两靴离地形态可辨，不能仅靠像素数字标接地通过。',
 footAxisObservation='左前靴鞋尖/鞋底长轴正向镜头，屈膝后的鞋带、前掌和后跟居中；右后靴仍近正面。',
 issues=['05→06头位/道具姿态转换需完整循环复核','06/07/08上半身接近，持物臂连续运动仍待动态审查','透明边缘彩点'])
by[7].update(observedPhase='左腿开始伸膝下降、右脚继续后收的短腾空候选',supportCandidate='none_airborne_candidate',
 handConnection='沿用08v4上半身与持物肩袖连接，右手笔前、左手卷后；未换持手。',
 groundingObservation='重新按相邻序列判断选07v6。06v3→07v6→08v4→09v1前靴最低1036→1097→1159→1190，前腿逐渐伸膝下降；07v6相对08收高62px并非单独弃用理由。后靴1068→1053→1044→1036渐收。',
 footAxisObservation='v6前靴近对称朝镜头，膝踝前进面保持；不再选前靴过低的v5。',
 issues=['整体接地仍未校准、完整循环待动态验收','06/07/08上半身接近，持物臂连续运动仍待动态审查','透明边缘彩点'])
by[8].update(groundingObservation='保留08v4。与新06v3/07v6配对后，前靴由1036→1097→1159逐步下降再到09的1190，原07v5→08反向收腿问题在当前选择中已消除；前靴未平踏，仍属临接触候选。',
 footAxisObservation='v4保持正面脚轴；不再因前一帧旧v5导致的相对高度判断而单独认定08收得偏高。',
 issues=['09触地轮廓与真实承重仍待动态验收','06/07/08上半身接近，持物臂连续运动仍待动态审查','透明边缘彩点'])
# Remove stale observations describing older selected versions.
by[11]['groundingObservation']='左靴平底、右靴抬高且屈膝；240px下支撑可辨。v2已补长笔头，v3保留；回收靴下缘相对v2变化20px，须与10/12动态复核。'
by[13]['observedPhase']='双脚轴已转正的左前掌推离候选'
by[13]['groundingObservation']='v3纠正v2两脚外撇并改善左膝踝路径；支撑脚前掌与后跟的离地关系仍不清楚，不能标蹬地通过。'
d['reviewedAt']=now
d['normal240pxFindings']='当前脚轴局部纠正后，主要前靴与02/10承重靴、11回收靴更正向镜头。最新06v3/07v6/08v4/09v1构成可辨的屈膝→伸膝下降序列，优于旧06v2/07v5的过早前伸后屈回。05→06转换、05/13推离、09→10尺度、14/15卷轴与16→01仍待完整动态复核，不能标整体通过。'
d['priorityRedrawFrames']=[5,13]
d['otherProblemFrames']=[1,3,6,7,8,9,10,11,12,14,15,16]
d['candidateCount']=len(list((BASE/'staging').glob('run-S-*.png')))
d['notSelectedCandidates'].pop('run-S-07-v6.png',None)
d['notSelectedCandidates']['run-S-06-v2.png']='虽脚轴较直，但前腿过早伸到y1182，接07v6时反向屈回；选择06v3建立渐伸下降。'
d['notSelectedCandidates']['run-S-07-v5.png']='前靴y1194随后08v4回升至1159，反向收腿；选择07v6与06v3/08v4配对。'
d['sequenceReview06to09']='grounding-S/S06-S09-sequence-review.json'
d['latestSequenceChoice']={'reviewedAt':now,'selected':['run-S-06-v3','run-S-07-v6','run-S-08-v4','run-S-09-v1'],'decisionBasis':'actual_anatomical_sequence_not_exact_prompt_pixel_target','furtherRetries':'none','approved':False}
d['timing']['note']='所有16槽齐全；480/640/720/800ms仅试播比较，未采用时长权重掩盖动作问题。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=BASE/'review/grounding-S/S06-S09-sequence-review.json';a=json.loads(q.read_text(encoding='utf-8'))
for r in a['rows']:
 if r['file']=='run-S-05-v3.png':
  r.pop('rearBootRoiMaxY',None);r['rearBootMeasurementNote']='not applicable: support boot extends below recovery-boot ROI'
a.update(decision='selected_as_better_pending_sequence',selected=['run-S-06-v3','run-S-07-v6','run-S-08-v4','run-S-09-v1'],
 reason='实图左膝逐渐伸开、左前靴下降，右后靴渐收；四帧脚轴向镜头，没有旧06/07过早前伸后在08屈回的相位逆转。按动作连续性选图，不以精确命中提示数字为标准。',
 actualLeadingBootRaiseRelativeToS07=61,rearBootChangeRelativeToS07=15,
 limitations=['06v3仍改变后靴约15px，但06→09后靴回收方向连续','05→06转换和09→10头身尺度需完整序列复核','06/07/08上半身接近，不能宣称持物摆臂动态通过','未校准地面，不以ROI自动贴地','05/13推离与全循环尚未通过'],furtherGeneration='stopped_after_one_attempt',approval=False)
q.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=BASE/'review/grounding-S/S07-new-base-attempt.json';a=json.loads(q.read_text(encoding='utf-8'))
a['originalDecisionHistory']={'decision':a['decision'],'reason':a['reason']}
a['decision']='selected_with_new_S06_after_sequence_review'
a['reason']='原先仅因收高超过提示数字而弃选过于机械；主代理复核后要求按06→09实际相位判断。06v3补足屈收过渡后，07v6成为较连续的伸膝下降段；原一次尝试证据保留。'
a['followUpReview']='S06-S09-sequence-review.json';q.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
errors=[];files=list((BASE/'staging').glob('run-S-*.png'))
for f in files:
 im=Image.open(f);record=f.with_name(f.name+'.generation.json')
 if im.size!=(1254,1254) or im.mode!='RGBA':errors.append(f.name+': size/mode')
 if not record.exists():errors.append(f.name+': missing generation record')
print(json.dumps({'count':len(files),'selection':[f['file'] for f in d['frames']],'validationErrors':errors}))

