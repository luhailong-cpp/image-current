import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
now = datetime.now(timezone.utc).isoformat()
ref = '../09_bamboo_archer_girl/runtime/run'
p = ROOT / 'review.json'
reviews = json.loads(p.read_text(encoding='utf-8-sig'))
for key, rec in reviews.items():
    if key.startswith('run/') and rec.get('visualStatus') == 'passed':
        rec['previousOfflineReview'] = {k: rec[k] for k in ('visualStatus','reviewedAt','reviewer','scope','notes') if k in rec}
        rec.update(visualStatus='reopened_user_feedback', reopenedAt=now, reference=ref,
                   notes='用户指出其他方向仍不正确；以09竹弓少女当前实图重新对照手脚、推进轴、落地与连续动作。旧离线通过不再表示当前验收。')
p.write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding='utf-8')
p = ROOT / 'audit/final-visual-review.json'
rec = json.loads(p.read_text(encoding='utf-8-sig'))
if rec.get('status') != 'reopened_user_feedback':
    rec = {'status':'reopened_user_feedback','reopenedAt':now,'reference':ref,
           'userFeedback':'其他方向还是不对，参照弓足少女，那个是对的',
           'remainingKnownArtFixes':['run八方向逐向重新对照09竹弓少女；具体问题和修复记录见audit/bamboo-*-review.json'],
           'previousOfflineReview':rec,'clientValidated':False}
p.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT/'STATUS.md').write_text('# 14 唤雪少女 · 跑步动作重新修正中\n\n用户指出其他方向仍不正确，已撤回128张跑步帧此前的离线通过状态，参照用户认可的09竹弓少女当前实图重新检查及修复。196张正式资源仍在；其余68张动作保留既有审核记录，跑步新审核以成品SHA和实际对照结果为准。\n\n当前入口：[完整动作](index.html)、[八方向并排](all-directions.html)。manifest.json与review.json反映本轮状态。未接入或验收游戏客户端。\n', encoding='utf-8')
p=ROOT/'MERGE_HANDOFF.md'
t=p.read_text(encoding='utf-8-sig')
if '跑步重新修正中' not in t[:200]:
    t=t.replace('# 14 唤雪少女 · 成品交接','# 14 唤雪少女 · 跑步重新修正中\n\n**当前状态：用户拒绝其他跑步方向，128帧已重新打开审核，按09竹弓少女当前实图继续修复。以下是上轮交接历史，不代表本轮已通过；最终以更新后的manifest.json和review.json为准。**',1)
t=t.replace('本机没有游戏客户端，未接入或运行引擎验收。','本轮尚未接入或运行游戏客户端验收。')
p.write_text(t,encoding='utf-8')
print('Reopened 128 run frames; preserved prior review history.')
