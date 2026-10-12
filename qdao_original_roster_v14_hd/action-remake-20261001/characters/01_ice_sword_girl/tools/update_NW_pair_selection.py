from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]; p=R/'review/run-NW-selection.json';s=json.loads(p.read_text(encoding='utf-8'))
for i in [7,8]:
 f=s['frames'][i-1];src=R/f'drafts/run/NW/{i:02}-v5.png'
 f.update(path=src.relative_to(R).as_posix(),sourcePath=src.relative_to(R).as_posix(),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),generationRecord=src.relative_to(R).as_posix()+'.generation.json')
s['frames'][6]['notes']='近左腿连续支撑，踝向后移进入后蹬；右足仍离地。'
s['frames'][7]['notes']='近左前掌连续支撑，后跟微升；远右腿下摆准备09落地，未提前换为右支撑。'
for f in s['frames']:f['actualContact']['evidence']=f['notes']
s.update(eightConsecutiveSupportVerified=True,positionPairsVerified=True,artStatus='paired_support_static_verified_playback_pending',remainingIssues=['1x播放检查，左支撑后移幅度小于右支撑，尚未游戏内验证'])
s['supportFrameRanges']={'left':list(range(1,9)),'right':list(range(9,17))}
s['staticInspection']={'allNativeViewed':True,'contactSheetViewed':True,'footAxis':'NW，鞋尖沿行进方向，无明确外八','handedness':'近左符，远右剑；肩袖肘手链保持','pairObservations':['01/02左足全掌落地','03/04左支撑接近体下','05/06左膝与足向后','07/08左后足蹬地，08右腿下摆','09/10右足全掌落地','11/12右支撑接近体下','13/14右足后移','15/16右前掌后蹬，左腿下摆']}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NW new support selection recorded')

