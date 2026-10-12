from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parents[1]
choices={1:'run-E-01-v2',2:'run-E-02-v2',3:'run-E-03-v2',4:'run-E-04-v3',5:'run-E-04-v1',6:'run-E-06-v2',7:'run-E-07-v2',8:'run-E-08-v2',9:'reused/run-E-09-from-prior-E07',10:'run-E-10-v4',11:'run-E-11-v3',12:'run-E-12-v2',13:'run-E-13-v1',14:'run-E-14-v2',15:'run-E-15-v5',16:'run-E-16-v2'}
notes={1:'沿用旧01落地相位，近右手持扇归属已修。',2:'沿用旧02受力压缩，近右肩臂持扇深度已修。',3:'左支撑与右膝通过，右扇肘回弯减少前后极值跳变。',4:'左后脚尖蹬地，右前膝折起，右扇后摆。',5:'原04v1实际双脚腾空，按图重选为05早腾空，保留原来源名。',6:'双脚腾空峰值，右腿领先与右扇后摆。',7:'针对性曲膝抬右靴，保留离地间距。',8:'按实图改记右足跟初触，已达到接触高度，不能继续算腾空。',9:'旧07真实右落地，重选09，不重复生成。',10:'v3修复握轴，v4回收右扇至腰边过渡，避免前后摆跳变；保留右支撑。',11:'原11跨步修为髋下支撑与左膝通过，v3纠正支撑鞋尖朝东。',12:'原12落地腿误绘，v2修为右后脚尖推蹬与左前膝屈折。',13:'第二次早腾空，近右扇前摆。',14:'第二腾空峰值，修正近右臂连接持扇手。',15:'v5前靴高度1140，介于14峰值1124与16预触地1171；修复悬停，右扇前摆连续。',16:'原16v1手臂过早反向，v2保留前摆并拉开前腿至预触地。'}
frames=[]
for n,key in choices.items():
    rel=('sources/'+key if key.startswith('reused/') else 'sources/new/'+key)+'.png'
    rec='provenance/reused/run-E-09-original-record.json' if n==9 else 'provenance/generation/'+key+'.json'
    with Image.open(B/rel) as im: bbox=im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
    print(n,bbox)
    frames.append(dict(action='run',direction='E',frame=n,source=rel,sha256=hashlib.sha256((B/rel).read_bytes()).hexdigest(),accepted=True,nativeSingleFrame=True,generationRecord=rec,review=dict(reviewer='root',reviewedAt=datetime.now(timezone.utc).isoformat(),notes=notes[n]+' 静态候选；全组时间线、衣摆变化与首尾尚待动态审核。'),event={1:'left_contact',4:'left_toeoff',6:'flight_peak',8:'right_heel_initial_contact',9:'right_contact',12:'right_toeoff',14:'flight_peak'}.get(n)))
(B/'audit/run-E-selection.json').write_text(json.dumps(dict(frames=frames),ensure_ascii=False,indent=2),encoding='utf-8')


