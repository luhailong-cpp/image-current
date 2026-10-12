"""Record the new user-video review scope before replacing selected frames."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'audit/video-direction-20261004'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/'manifest.json')
slots=['run-N-'+x for x in ['01','02','07','08','09','10','11','15']]+['run-NE-'+x for x in ['08','09','12','13','15']]+['run-SE-04','run-SE-05','run-NW-10','run-SW-10']
p=OUT/'before-repair.json'
if p.exists():raise RuntimeError('Keep existing before record intact')
record={'recordedAt':datetime.now(timezone.utc).isoformat(),'trigger':'用户提供其他游戏视频，指出动作方向笔直、我方腿脚掌歪外翻；本次实际查看并定向修正。','scope':'17 identified foot-axis edits; other179 delivered frames retained','manifestSha256':sha(ROOT/'manifest.json'),'targetSlots':slots,'frames':[{'slot':r['slot'],'source':r['source'],'sourceSha256':r['derivedFrom']['sha256'],'output':r['output'],'outputSha256':r['sha256']} for r in m['frames']], 'reviewMethod':'root读原视频四段连续抽样、截图、身份风格；分方向审核者查看128跑步单图；root复看全部战斗连图和可疑原生帧。视频角色小和遮挡不支持每帧鞋掌细节断言。','reviewFindings':{'N':'左支撑N01/02/15向左外露，右支撑N07–11向右外露；踝以下收正北。','NE':'08/09/12/13/15右支撑靴从背3/4转侧鞋形，收回右上前向。','SE':'04/05左支撑靴横向长鞋面，收回右下前向。','NW':'10左悬空靴突然翻成侧面朝左下，与09/11脱节。','SW':'10左支撑靴偏正下，恢复左下斜向。','retained':'S/E/W全部跑步、其余跑步、全部战斗保留；SW13/14前足背屈改变鞋尖投影，不能据此断言外翻。'},'existingStaticReview':'current-static-review-before-video-feedback.json','dynamicReview':'not performed; previous browser file policy restriction remains','modelRoute':'builtin image_gen, target GPT Image2.5 Sunburst/max; actual version/quality not disclosed'}
p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'current-static-review-before-video-feedback.json').write_bytes((ROOT/'audit/current-static-review.json').read_bytes())
print('Recorded 196 previous hashes and17 correction slots; no runtime changes.')
