"""Apply the user's 960ms/16=60ms run timing without changing combat or pixels."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, argparse
from build_delivery import render_main_preview
from render_review_board import render_review_board
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reopen',action='store_true');a=parser.parse_args()
    m=read(ROOT/'manifest.json');old_t=read(ROOT/'audit/run-timing.json')
    now=datetime.now(timezone.utc).isoformat();audit=ROOT/'audit/archer-reference';audit.mkdir(parents=True,exist_ok=True)
    if a.reopen:
        for name,path in [('previous-manifest.json',ROOT/'manifest.json'),('previous-run-timing.json',ROOT/'audit/run-timing.json'),('previous-final-review.json',ROOT/'audit/final-review.json')]:
            if not (audit/name).exists(): (audit/name).write_bytes(path.read_bytes())
        feedback={'recordedAt':now,'userFeedback':'其他方向还是不对，参照竹弓少女当前版；正常跑步960ms/圈，每帧60ms，移除更快档。','reference':'../09_bamboo_archer_girl/runtime/','previousOfflineApproval':'superseded_by_user_feedback','clientIntegration':'not_integrated'}
        write(audit/'user-feedback.json',feedback)
        review=read(ROOT/'audit/final-review.json');review['supersededAt']=now;review['status']='superseded_by_user_feedback';write(ROOT/'audit/final-review.json',review)
        m.update(animationApproval='pending_archer_reference_review',userAcceptance='rejected_other_directions',note=feedback['userFeedback'],currentRevision='audit/archer-reference/user-feedback.json')
        m.pop('offlineReview',None)
    t={'schemaVersion':1,'character':ROOT.name,'action':'run','frameCount':16,'defaultProfile':'uniform960','status':'candidate_pending_archer_reference_review','clientIntegration':'not_integrated','clientRuntimeAcceptance':'not_tested','note':'用户指定均匀60ms×16=960ms；旧快速档已移出正式预览。姿态重修中，未入客户端。','profiles':[{'id':'uniform960','label':'960ms 正常跑步 · 每帧60ms','status':'candidate_pending_archer_reference_review','cycleMs':960,'frameDurationsMs':[60]*16}],'requestedAt':now}
    for row in m['frames']:
        if row['action']!='run': continue
        row.update(durationMs=60,timingStatus='user_requested_not_client')
        d=read(ROOT/row['derivedRecord']);d.update(durationMs=60,timingStatus='user_requested_not_client')
        if a.reopen:
            row.update(animationApproval='pending_archer_reference_review',visualApproval='pending_archer_reference_review');row.pop('offlineReview',None)
            d.update(animationApproval='pending_archer_reference_review',userAcceptance='rejected_other_directions');d.pop('offlineReview',None)
        write(ROOT/row['derivedRecord'],d)
    for g in m['groups']:
        if g['action']=='run':
            g.update(durationMs=60,frameDurationsMs=[60]*16,cycleMs=960,timingStatus='user_requested_not_client',trialCyclesMs=[])
            if a.reopen: g.update(animationApproval='pending_archer_reference_review');g.pop('offlineReview',None)
    m['runTiming']={'file':'audit/run-timing.json','defaultProfile':'uniform960','status':'user_requested_not_client','cycleMs':960,'frameDurationMs':60}
    write(ROOT/'manifest.json',m);write(ROOT/'audit/run-timing.json',t)
    (ROOT/'preview/index.html').write_text(render_main_preview(m,t),encoding='utf-8')
    (ROOT/'preview/all-directions.html').write_text(render_review_board(m,t),encoding='utf-8')
    print('Applied run 16 x 60ms = 960ms; combat unchanged; pose review pending.')
if __name__=='__main__': main()
