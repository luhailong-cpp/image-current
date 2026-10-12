from pathlib import Path
from datetime import datetime,timezone
import json
b=Path(__file__).resolve().parents[1]
p=b/'audit/cast-foot-review.json';d=json.loads(p.read_text(encoding='utf-8'))
d['completedAt']=datetime.now(timezone.utc).isoformat()
d['finalStaticReview']={'performed':True,'method':'32张内置返回的完整原图逐张目检；再次查看E/W足部16格连图及完整16格连图。','passes':['E16张：后靴屏左的鞋跟在左、鞋头向右，与身体和原前靴方向一致。','W16张：后靴屏右的鞋跟在右、鞋头向左，与身体和原前靴方向一致。','靴子仍是蓝金圆头；两腿独立，踝接腿连续；前靴方向保留，未把两腿向中间挤。','逐张保持原有右手扇、左手诀/松掌/垂手的阶段；32帧并未复用同一张编辑图。','扇持手未翻转；身份、衣服、相机和整体画幅保留。'],'limitations':['E方向原序列在聚势到释放间的站距/重心变化仍存在，尤其06—09；本次鞋向局部编辑没有伪造全组固定脚位。','两方向的鞋底都画有平直承重段；统一1191源参考线附近仍有少量帧高差，不能仅凭鞋底形状宣布完整动态无滑步。','正常速度和慢速完整实播本代理未完成：CUA不可用（apps/browsers均空）。'] }
d['artifacts']={'feetContacts':['audit/cast-foot-contact-E.png','audit/cast-foot-contact-W.png'],'fullContacts':['audit/cast-final-review/E-contact.png','audit/cast-final-review/W-contact.png'],'normal':['audit/cast-final-review/E-normal.apng','audit/cast-final-review/W-normal.apng'],'slow':['audit/cast-final-review/E-slow.apng','audit/cast-final-review/W-slow.apng'],'integrity':'audit/cast-foot-integrity.json'}
d['timing']={'frameMs':45,'cycleMs':720,'changedByFootCorrection':False,'slowPreviewFrameMs':180}
d['model']={'target':'GPT Image 2.5 Sunburst / max','submittedSelector':None,'actualModel':None,'actualQuality':None,'note':'内置宿主管理入口，回执未披露实际型号/质量；逐图已保留目标、提交提示词/引用及实际回执。'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('cast foot32 final static review saved')

