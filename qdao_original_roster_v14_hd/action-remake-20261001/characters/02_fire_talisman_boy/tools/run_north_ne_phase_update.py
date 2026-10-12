"""Record the reviewed NE phase repair without touching other owners."""
from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(ZoneInfo('America/New_York')).isoformat()
notes={
4:('03','右后蹬/离地过渡候选','viewer右低腿沿03右髋保持连续；右鞋跟抬、露底，左腿仍高折。脚尖是否仍触地待统一地面实播。'),
5:('03','右蹬后早腾空','右鞋比04抬高，右膝开始回收，左鞋高折；无提前左长腿后伸。'),
6:('06','错位腾空交换候选','已附09竹弓NE15作关节与鞋轴参考；右鞋高折、左腿下前过，无并腿跳；左伸距较07未明显缩短，需root实播05→06→07。')}
rows=[]
for n,(attempt,phase,note) in notes.items():
 p=ROOT/f'records/run-NE-{n:02}-attempt-{attempt}.json';v=read(p)
 v['visualQA']={'reviewedAt':now,'status':'single_frame_axes_cards_shoulders_pass_sequence_pending','reviewMethod':'actual original native output, exported whole canvas and new NE16 contact sheet inspected','cardsVisible':5,'anatomicalHands':'right talisman, left bell; shoulder-to-sleeve-to-wrist visibly traced','shoeAxes':'NE longitudinal heel/sole perspective, no confirmed outturn','observedPhase':phase,'observation':note,'normalSpeedPlayback':'not performed by this subagent; root review pending'}
 save(p,v)
 if 'replaces' in v:
  old=ROOT/v['replaces']['generationRecord'];o=read(old)
  o['status']='superseded_after_observed_phase_defect'
  o['supersededBy']=p.relative_to(ROOT).as_posix()
  o['supersessionReason']=('NE06 attempt04 was rejected in root playback: both knees tuck together and both shoes are nearly level, reading as a two-leg hop.' if n==6 else 'Original NE04-05 showed left low trailing leg immediately after NE03 right support; independent redraw fixes actual leg-chain sequence.')
  save(old,o)
 rows.append({'frame':n,'file':v['export']['file'],'sha256':v['export']['sha256'],'sourceRecord':p.relative_to(ROOT).as_posix(),'phase':phase,'observation':note})
for n,attempt,reason in [(4,2,'仍为左低长腿、右高折，未修复提前换腿'),(6,3,'右鞋仍明显低于左鞋，未形成衔接07所需空中交换'),(6,4,'root动态拒稿：双膝并蜷、两鞋并排同高，像并腿跳'),(6,5,'左腿伸距较07更长，未形成所需短前过过渡')]:
 p=ROOT/f'records/run-NE-{n:02}-attempt-{attempt:02}.json';v=read(p);v['visualQA']={'status':'rejected','reviewedAt':now,'reason':reason}
 native=(ROOT/v['native']['file']).resolve()
 allowed=(ROOT/'work/run-NE').resolve()
 if not native.is_relative_to(allowed):raise ValueError('bad delete target')
 if native.exists():
  v['removedRejectedNative']={'file':native.relative_to(ROOT).as_posix(),'sha256':sha(native),'reason':'User materials-retention instruction: rejected image removed after accepted replacement exported; textual provenance retained.'}
  native.unlink()
 save(p,v)
inv=read(ROOT/'inventory-run-north.json')
for f in inv['frames']:
 if f['direction']=='NE' and f['frame'] in notes:
  f['visual_status']='single_frame_axes_cards_shoulders_pass_sequence_pending'
  f['observed_phase']=notes[f['frame']][1]
save(ROOT/'inventory-run-north.json',inv)
doc={'reviewedAt':now,'slotsReplaced':[4,5,6],'newFrames':rows,'actualModel':None,'actualQuality':None,'modelTarget':'GPT Image2.5 Sunburst/max','nativeSize':[1254,1254],'exportMethod':'whole square canvas downsample to1024, no per-frame positioning','rootPlaybackRequired':['03→04→05 support-side continuity','06 staggered flight; inspect05→06→07 at user-requested uniform1200ms','06→07→08→09 left landing','01/02→03 and16→01 arm amplitude'],'technicalSummary':'55/55 own host-to-native SHA matched; current previews16/16; four-direction64 phase rows regenerated','combatIndependentReview':'reviews/combat-independent-review-20261003.json','status':'candidate_sequence_pending_root_playback'}
save(ROOT/'work/run-NE/phase-repair-20261003.json',doc)
print(json.dumps({'repaired':rows,'inventorySha256':sha(ROOT/'inventory-run-north.json')},ensure_ascii=True))

