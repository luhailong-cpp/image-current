from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
P=Path(__file__).parent
ROOT=Path('D:/work/image')
PROD=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southeast'
REVIEW=P.parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
snapshot=read(P/'metadata-snapshot.json'); docs=snapshot['documents']; checks=read(P/'source-checks.json'); now=datetime.now(timezone.utc).isoformat()
base=read(REVIEW/'southeast-audit-v01/inventory.json'); tilemap={t['tileId']:t for t in base['tiles']}
# A fixed capture is retained even when unrelated active workers advance.
after=[]
for c in snapshot['checks']:
    actual=sha(c['file']);
    if actual!=c['sha256']: after.append({'file':c['file'],'frozenSha256':c['sha256'],'currentSha256':actual,'includedInFrozenCounts':False})
extra=[]
def src(p,expected=None):
    p=Path(p); im=Image.open(p); d={'file':str(p),'sha256':sha(p),'dimensions':list(im.size),'expectedSha256':expected,'hashMatches':sha(p)==expected if expected else None};extra.append(d);return d
r13=read(P/'r13_c11-selection-review.json'); old={x['coordinate']:x['sha256'] for x in tilemap['r13_c11']['selectedNativeCores']}
r13all=[]
for key,v in r13['versions'].items():
    d=src(PROD/'native'/f'r13_c11_p{key}_{v}.png',old.get(key)); d['coordinate']=key;r13all.append(d)
r13['selectedNativeCores']=r13all;r13['all12BaselineCoresUnchanged']=all(x['hashMatches'] for x in r13all if x['coordinate'] in old)
r13['visualReview']={'newSeamsPassed':3,'newJunctionsPassed':1,'evidence':'r13-new-seam-board.png and r13_c11/j31-32-41-42.png viewed at original pixels','finding':'海沫、岩体轮廓和岩纹在新三条共享线及交点连续；不扩展为整块通过。','reviewedAtUtc':now}
write('r13_c11-selection-review.json',r13)
r14=read(P/'r14_c12-source-review.json'); im=Image.open(r14['candidate']);north=Image.open(r14['actualNorthChecksPrior'][0]['file']);partial=read(PROD/'qa/r14_c12-partial-local-20261013/partial-proof-and-review-queue.json');n=Image.open(partial['northCandidate']); northchecks=[]
for idx,x in enumerate(partial['actualNorthCuts']):
    oldcut=Image.open(x['file']); w,h=oldcut.size; strip=Image.new('RGB',(1024,h)); a=h//2
    strip.paste(n.crop((idx*1024,4096-a,(idx+1)*1024,4096)),(0,0));strip.paste(im.crop((idx*1024,0,(idx+1)*1024,h-a)),(0,a))
    northchecks.append({'file':x['file'],'sha256':sha(x['file']),'expectedSha256':x['sha256'],'hashMatches':sha(x['file'])==x['sha256'],'dimensions':list(oldcut.size),'pixelsMatchCurrent':oldcut.size==strip.size and oldcut.tobytes()==strip.tobytes(),'priorStatus':x['status']})
assert all(x['hashMatches'] and x['pixelsMatchCurrent'] for x in northchecks)
r14['actualNorthReuseVerification']=northchecks
r14['independentInternalReview']={'status':'passed_for_frozen_candidate','reusedSeams':18,'reusedJunctions':5,'newSeamsViewedAndPassed':6,'newJunctionsViewedAndPassed':4,'actualNorthSeamsReused':4,'geometry':'水波纹跨线连续，无沿核心边的直线材质带或跳色。','evidence':['r14-new-vertical-board.png','r14-new-horizontal-board.png','r14-new-junction-board.png'],'reviewedAtUtc':now}
r14['externalStatus']={'north':'reused_pass_same_pixels','west':'missing_r14_c11','east':'missing_r14_c13','south':'outer_map_boundary','formalAccepted':False}
write('r14_c12-source-review.json',r14)
# Validate only v03 changed ownership. Unchanged v02 areas inherit prior pixel proof.
r12=read(P/'r12_c13-proposal-delta.json');meta=read(str(r12['unadoptedProposal'])+'.generation.json');s=meta['sources'][-1];native=src(s['file'],s['sha256']);maskp=Path(s['binaryOwnershipMask']);mask=np.array(Image.open(maskp))
if mask.ndim==3:mask=mask[:,:,0]
mask=mask>0;source=np.array(Image.open(s['file']));a=np.array(Image.open(r12['currentCandidate']));b=np.array(Image.open(r12['unadoptedProposal']));x,y=s['tileRelativeOrigin'];trial=a.copy();region=trial[y:y+source.shape[0],x:x+source.shape[1]];region[mask]=source[mask]
r12['proposalDeltaSourceProof']={'repairSource':native,'mask':str(maskp),'maskSha256':sha(maskp),'maskHashMatches':sha(maskp)==s['maskSha256'],'ownedPixels':int(mask.sum()),'mismatchedPixels':int(np.any(trial!=b,axis=2).sum()),'sourcePixelsPreserved':bool(np.array_equal(trial,b))}
assert r12['proposalDeltaSourceProof']['mismatchedPixels']==0
r12['visualReview']={'status':'not_passed_not_adopted','viewed':['r12-current-proposal-breakpoints.png','r12_c13/v03-whole-floor-proposal.png'],'currentV02Unclosed':['tile-local (1024,2167) floor groove mismatch','tile-local (3072,3730) low sail batten mismatch'],'v03Findings':'局部采用整木板端头，但实际显示图仍有 x≈1024 木纹/色阶竖直硬边；低位帆横杆断点区域与 v02 相同。没有足够依据关闭整块返修；不把局部替换像素证明当作视觉通过。','caution':'x≈1024 的可见竖边包含继承区域，不将整条硬边归因于 v03 新增像素。','reviewedAtUtc':now}
write('r12_c13-proposal-delta.json',r12)
crops=read(P/'crop-manifest.json')
for x in crops['cuts']:
    if 'r14_c12' in x['file'] or 'r13_c11' in x['file']:x['visualReview']='viewed_original_pixels_pass_local_only'
    else:x['visualReview']='viewed_original_pixels_open_issue_or_unadopted_proposal'
write('crop-manifest.json',crops)
groups=[]
for key,ids in [('g01-r09-r10-c12-c13',['r09_c12','r09_c13','r10_c12','r10_c13']),('g02-r11-r12-c11-c12',['r11_c11','r11_c12','r12_c11','r12_c12'])]:
    records=[{'tile':t,'file':tilemap[t]['file'],'sha256':tilemap[t]['sha256'],'hashMatches':sha(tilemap[t]['file'])==tilemap[t]['sha256']} for t in ids]
    groups.append({'group':key,'sourceStale':not all(x['hashMatches'] for x in records),'rebuilt':False,'priorVisualStatus':'local_seams_passed' if key.startswith('g01') else 'geometry_pass_material_issue_open','sources':records})
summary={'schemaVersion':2,'zone':'southeast','status':'incremental_audit_complete_for_frozen_capture','snapshotStartedAtUtc':checks['snapshotStartedAtUtc'],'snapshotCompletedAtUtc':checks['snapshotCompletedAtUtc'],'completedAtUtc':now,'sourceStability':{'allStableDuringInitialRead':checks['allStableDuringRead'],'changesAfterMetadataCapture':after,'laterChangesExcluded':True},'baselineCounts':{'fullCoverage':15,'adoptedFullCoverage':14,'partialTiles':3,'emptyTiles':31,'selectedNativeCores':267,'formalAccepted':0},'frozenCurrentCounts':{'fullCoverage':16,'adoptedFullCoverage':14,'unadoptedFullCandidates':2,'partialTiles':2,'emptyTiles':31,'selectedNativeCores':271,'missingNativeCores':513,'missingFullTiles':33,'internalPassedAsRecorded':14,'independentlyVerifiedAdditionalInternalPass':1,'formalAccepted':0},'countInterpretation':'271 includes native sources of complete pending candidates and declared partial selections; not 271 formally accepted cores. r14_c12 is counted as a full pending candidate because its selected-source manifest and exact candidate exist despite stale progress=14.','coordinateDelta':{'r13_c11':{'baselineCoreCount':12,'previousDeltaCoreCount':14,'currentSelectedCoreCount':14,'missing':['43','44'],'fullCandidate':False,'newLocalSeamsPassed':3,'newLocalJunctionsPassed':1},'r14_c12':{'baselineCoreCount':14,'previousDeltaSelectedCount':14,'currentCandidateNativeCoreCount':16,'candidate':r14['candidate'],'sha256':r14['candidateSha256'],'adopted':False,'independentInternalPassed':True,'formalAccepted':False},'r12_c13':{'currentCandidate':r12['currentCandidate'],'sha256':r12['currentCandidateSha256'],'adopted':False,'internalPassed':False,'proposal':r12['unadoptedProposal'],'proposalAdopted':False},'r13_c13':{'selectedCoreCount':1,'selectedVersions':docs['progress-r13_c13.json']['selectedVersions'],'status':docs['progress-r13_c13.json']['status']},'r14_c14':{'workingCoreCount':0,'status':docs['progress-r14_c14.json']['status'],'countedAsEmpty':True}},'reuse':{'baselineCandidateCount':15,'allBaselineCandidateHashesUnchanged':True,'groups':groups,'r14Seams':18,'r14Junctions':5,'r14ActualNorthSeams':4},'visualReview':{'newR14InternalSeams':6,'newR14InternalJunctions':4,'newR13LocalSeams':3,'newR13LocalJunctions':1,'r12CurrentAndProposalCrops':5,'actualPixelCropsViewed':19,'allAtOriginalResolution':True},'modelEvidence':'No new generation or AI editing. Historical image entry actual model undisclosed; no relabeling as 2.5. Root AGENTS preferred builtin/free 2.5 with builtin 2.0 fallback applies.','generationPerformed':False,'aiEditPerformed':False,'productionModified':False,'sharedGitTouched':False,'historicalNativeArchiveRescanned':False,'wholeMapAcceptance':False,'reports':{n:str(P/n) for n in ['review.md','metadata-snapshot.json','source-checks.json','r13_c11-selection-review.json','r14_c12-source-review.json','r12_c13-proposal-delta.json','crop-manifest.json','baseline-candidate-reuse.json']}}
write('summary.json',summary)
write('supplemental-source-checks.json',{'checkedAtUtc':now,'sources':extra,'north':northchecks,'changesAfterFrozenMetadata':after})
report=f'''# 八仙岛东南区增量检查 v02

本批检查已完成。冻结读取时间为 {checks['snapshotStartedAtUtc']} 至 {checks['snapshotCompletedAtUtc']}。检查当前采用/候选来源及变化，未扫描历史 native 档案；两个既有 8192 组图的输入哈希未变，直接复用，没有重建。原始素材、生产记录及 Git 均未修改，零生图、零 AI 修图。

本截点东南区 49 块中，完整覆盖候选 **16**（生产已采用 14、未采用 2），部分覆盖 **2**，空块 **31**。纳入候选及已声明部分选择的核心为 **271/784**，较原基线 267 增加 4；缺 513 核心，缺完整块 33。正式验收仍为 **0**。采用、完整覆盖、内部检查和正式验收分别记录。

| 坐标 | 当前证据及结论 |
|---|---|
| r14_c12 | 已有 16 源的 selected-native manifest 和 4096 候选，SHA `{r14['candidateSha256']}`。16 个 1024 核心与候选逐像素比较，差异 0。旧 18 内缝、5 交点、4 段北邻边与当前像素相同，复用通过；新增 6 内缝、4 交点按原比例实际查看通过。该版本局部内部检查通过，但生产采用列表仍未收录，东西邻块缺失，正式未通过。旧 progress 的 14 核心字段已滞后。 |
| r13_c11 | 当前 selection 为 14 核心，原 12 核心哈希未变，新选 p41/p42 的 3 条共享边及 1 交点原比例查看连续。仍缺 p43/p44，无完整候选。进度中的在途请求不算落盘。 |
| r12_c13 | 当前待修候选仍是 v02，SHA `{r12['currentCandidateSha256']}` 未变。地槽 `(1024,2167)`、低位帆横杆 `(3072,3730)` 两处旧问题不关闭。v03-local-ownership 为未采用提案；143215 所属像素机械复核一致，但显示仍见木纹/色阶竖边，且帆横杆区域未改变，不升级为通过。竖边包含原来继承部分，未将整条边归因于提案。 |
| r13_c13 / r14_c14 | r13_c13 仍仅 p14-v01 一片被选中；r14_c14 有生成状态但工作版本为空。均按冻结元数据计数，未追逐在途新文件。 |

实际查看了 19 张原像素裁片，通过 5 张无缩放接触板及 2 张单独原图展示。r14_c12 水面纹理跨线连续；r13_c11 的岩体轮廓、岩纹与海沫在新增边和交点连续。只作局部结果，不扩展为全图验收。原两组组图中 g01 既有局部通过结论保留，g02 木柱材质待核继续保留。

当前元数据在固定读取后有 {len(after)} 个文件再次变化，已写入 `supplemental-source-checks.json`；后续生产不并入本批冻结计数。旧 JSON 中的严格 2.5 停工文句已被根 AGENTS 撤销，不构成本区停工理由。当前并行划拨的八仙岛坐标均在北部，与本次东南只读检查无抢占。

交付路径均在本目录：`summary.json` 供总协调汇总，`r14_c12-source-review.json` 记录新增完整候选及旧检查复用，`r13_c11-selection-review.json` 记录新边与缺片，`r12_c13-proposal-delta.json` 记录未过问题和提案身份。`crop-manifest.json`、`boards.json` 保留所有实际原像素展示的来源、哈希及坐标。没有覆盖现有图片，没有提交或 push。
'''
(P/'review.md').write_text(report,encoding='utf-8')
print(json.dumps({'summary':str(P/'summary.json'),'counts':summary['frozenCurrentCounts'],'northReused':all(x['pixelsMatchCurrent'] for x in northchecks),'v03DeltaMismatch':r12['proposalDeltaSourceProof']['mismatchedPixels'],'postCaptureChangedMetadata':len(after)},ensure_ascii=False))
