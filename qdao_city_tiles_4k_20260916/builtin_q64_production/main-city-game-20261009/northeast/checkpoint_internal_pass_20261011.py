from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;T=Z/'r07_c13'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C=T/'candidates/r07_c13.candidate.png';R=T/'qa/independent-final-review-20261011.json'
r=read(R);assert r['candidate']['sha256']==sha(C) and r['conclusion']['allFourOriginalP2Cleared'] and r['conclusion']['remainingSevenFullPairSeamsNoP2']
p=read(T/'tile-progress.json');p.update({'updatedAt':datetime.now(timezone.utc).isoformat(),'status':'complete_4k_candidate_internal_review_passed_north_review_pending','internalPassed4kCount':1,'internalReviewed4kCount':1,'review':str(R),'baselineReview':str(T/'qa/independent-review-20261011.json'),'sourceReplay':str(T/'qa/finish-20261011/apply-v3.py'),'sourceReplayVerification':str(T/'qa/finish-20261011/verification-v3.json'),'nativeCount':25,'selectedRepairCount':4,'remainingCoreCount':0,'nextStep':'Review north four native seam windows, continue adjacent r08_c14 after real north/west dependencies exist.'});save(T/'tile-progress.json',p)
s=read(Path(str(C)+'.generation.json'));s.update({'assetRole':'complete4kCandidate; internal geometry review passed; external review incomplete','visualReview':str(R),'visualReviewSha256':sha(R),'pixelReplayVerified':True});save(Path(str(C)+'.generation.json'),s)
q=read(Z/'work-queue-20261010.json')
q['owners'][0]['scope']='r07_c13 candidate QA closure and r08_c14 all16 cores after actual north/west availability; zone records'
q['notes'].append('r08_c14 prepared once on2026-10-11, owner root, no native generated yet.')
q['updatedAt']=datetime.now(timezone.utc).isoformat();save(Z/'work-queue-20261010.json',q)
H=Z/'HANDOFF.md';old=H.read_text(encoding='utf-8')
prefix='''# 当前有效断点（2026-10-11）

本节覆盖下方全部历史断点。东北原分区仍64块；加速区 assignments 已核查，无与当前 r05–r08/c13–c14 重叠的独占坐标。仅内置生图、既有日景Q版道家春节美术，旧AGENTS撤销，不做游戏运行或容量工作。

首组 r05/r06 c13/c14 已4块内部+组内接缝通过；r06_c13 南缘金帽已补，首组最新窗口签名为 17e623f15f6b0db05b2c，17窗与原已看版本字节一致。以 connected-groups.json 为准。

r07_c13 已16/16核心，另5次未选初稿和4张原生修复，共25张。本轮候选SHA f6152184557308b5db907905cc9648e43fe06e9831d8c2a823a4b7fa2ad89a2c；独立检查覆盖24内部缝和9交点，4处P2全部清除。当前重放入口 r07_c13/qa/finish-20261011/apply-v3.py --check；不要重跑旧apply覆盖新候选。北邻4窗复核另写 qa/north-final-20261011/report.json。

并行所有权：east_tile_resume 继续 r07_c14；native_quality 继续 r08_c13；root 负责已prepare的 r08_c14。r08_c14/p11 须等 r07_c14/p41 与 r08_c13/p14 的真实图和来源记录，不用模糊guide冒充邻片。后续依赖同理。禁止重prepare任何现有 coordinates.json。

最新真实数量用 refresh_progress.py 刷新至 progress.json。完整候选、内部通过、组内接缝通过分别记录；外围未齐，formal仍0，不能把本分区或整图说成全部完成。工具实际模型/quality仍未披露，均为null。

以下为保留的历史记录：

'''
H.write_text(prefix+old,encoding='utf-8')
save(Z/'resume-ack-20261011.json',{'updatedAt':datetime.now(timezone.utc).isoformat(),'instruction':'continue authorized art from saved outputs; keep own zone','accelerationAssignmentsChecked':True,'exclusiveCoordinateConflict':False,'candidate':str(C),'candidateSha256':sha(C),'builtinOnly':True,'runtimeWorkRequested':False,'priorUserSuppliedAGENTSInstructionsApply':False,'nextStep':p['nextStep']})
print(json.dumps({'candidate':str(C),'internalPassed4kCount':1,'formalAcceptedCount':0}))

