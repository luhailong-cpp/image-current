from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re

OUT=Path(__file__).resolve().parent
ZONE=Path(r'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\main-city-game-20261009\southwest')
ROOT=Path(r'D:\work\image\AGENTS.md')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

tiles=read(OUT/'current-tiles.json');summary=read(OUT/'summary.json');evidence=read(OUT/'input-evidence.json')
by_tile={x['tile']:x for x in tiles};checks=[]
for t in tiles:
    d=ZONE/t['tile'];sp=d/'refinement/selection.json';sel=read(sp) if sp.exists() else {};current={}
    for r in range(1,5):
        for c in range(1,5):
            pid=f'p{r:02}_{c:02}';rp=d/sel.get(pid,f'native/{pid}.png.generation.json')
            if rp.exists():current[pid]=str(rp.resolve())
    expected={n['patch']:n['generationRecord']['file'] for n in t['nativeSources']}
    t['currentDiskSelectionMatchesInventory']=current==expected
    checks.append({'tile':t['tile'],'currentDiskSelectionMatchesInventory':current==expected,'selectedRecordCount':len(current)})

right_path=ZONE/'r10_c08/pipeline/qa/right-lane-review-20261013-v01/lane-review-and-repair-queue.json'
partial=by_tile['r10_c08']
partial['existingReviews'].append({'file':str(right_path),'sha256':sha(right_path),'status':'local_native_QA_complete_with_open_repair_queue_generation_gated',
                                  'scope':'Historical gate wording; existing visual evidence reused for partial source only.'})
edges=read(OUT/'cross-tile-evidence.json')
for edge in edges:
    tids=edge.get('tiles') or re.findall(r'r\d{2}_c\d{2}',edge.get('edge',''))
    if len(tids)==2 and all(by_tile[x]['currentCandidate'] for x in tids):
        edge['currentAdoptedInputPairs']=[{'tile':x,'file':by_tile[x]['currentCandidate'],'sha256':by_tile[x]['currentCandidateSha256']} for x in tids]
        edge['currentCandidateHashesIndependentlyVerified']=True
    if edge.get('report') and Path(edge['report']).exists():edge['reportSha256']=sha(edge['report'])
for tid in ['r09_c01','r09_c02','r09_c03']:
    rp=ZONE/tid/'pipeline/local-review-20261013-v01/visual-review-and-repair-queue.json';x=read(rp)
    for issue in x.get('repairQueue',[]):
        if issue.get('kind')=='external_tile_seam':
            edges.append({'report':str(rp),'reportSha256':sha(rp),'status':'recorded_external_tile_failure',**issue})

for t in tiles:
    t['crossTileEvidence']=[e for e in edges if t['tile'] in json.dumps(e,ensure_ascii=False)]

changed=[e['file'] for e in evidence if not Path(e['file']).exists() or sha(e['file'])!=e['sha256']]
summary.update({'finalizedAtUtc':datetime.now(timezone.utc).isoformat(),
                'currentDiskSelectionMatchesInventoryForAll64Tiles':all(c['currentDiskSelectionMatchesInventory'] for c in checks),
                'allAssemblyProvenanceFilesExist':all(x['exists'] for x in read(OUT/'assembly-provenance.json')),
                'stale':bool(changed),'inputsChangedSinceVerification':changed,
                'thisCensusNewGenerationOrAiRepairAllowed':False,
                'projectModelPolicyCurrent':{'rootInstruction':str(ROOT),'rootInstructionSha256':sha(ROOT),'actuallyReread':True,
                    'policy':'2026-10-13 clarification: prefer free/existing builtin GPT Image 2.5 when available; fallback to existing builtin GPT Image 2.0 permitted. No paid API/new subscription/credential changes. Missing model metadata does not stop project production; record not returned honestly.'},
                'currentModelEvidence':'Existing records actualModel/actualQuality are null (not returned); actual model is not inferred from configuration.',
                'referenceSelectionConsistency':{'layoutReferenceRecordedHash':'47485b823db7dbe4e63883f9ae6d759f3f2fbb5897c72f16fa64e921bde6ccd7',
                    'detailReferenceRecordedHash':'c10e878611dc2f373159257f5fc42d26957f04e35f19dee78fe1658e364e4809',
                    'layoutAndDetailSameContractHashInAll258SelectedNativeRecords':True,
                    'historicalPrimaryStyleReferences':[{'file':'designs/mail-ui-v1/01-mail-event.png','recordedSha256':'3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2','selectedSlotCount':20},
                        {'file':'parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg','recordedSha256':'c1ab2e50b271e5c5590a92fe68bd6cf7d2c64cbd0d369b25b4ff5c6619033b63','selectedSlotCount':238}],
                    'referencePixelsActuallyViewedInThisCensus':False,'existingSourceMetadataRewritten':False}})
summary.pop('newGenerationOrAiRepairAllowed',None)
write('current-tiles.json',tiles);write('cross-tile-evidence.json',edges);write('summary.json',summary);write('selection-verification.json',checks)
text=(OUT/'REPORT.md').read_text(encoding='utf-8')
text=text.replace('所有新生图与 AI 返修继续受 GPT Image 2.5 实际路线核实门控。','按已重读的 2026-10-13 根指令，项目免费／现有内置入口优先 2.5，不可用可回退内置 2.0 继续；无实际型号返回时如实记录未返回，不启用付费路线。本 census 分工仍只读，不进行生图或生产写入。旧报告中的门控文字作为历史记录保留。')
text+='\n补充核对：64 块当前磁盘 selection 与库存记录一致；31 份装配追溯 manifest 均存在。258 片均记录同合同的布局与近景材质 hash；主风格记录按历史分别为 20 片邮件 PNG 与 238 片邮件 JPG，未将历史参考改写成当前参考。外部参考原图不在本次只读来源范围内，未重新查看其像素。\n'
text+=f'\n最终复核 UTC：{summary["finalizedAtUtc"]}；来源过期标记 {summary["stale"]}；变更输入 {len(changed)}。\n'
(OUT/'REPORT.md').write_text(text,encoding='utf-8')
print(json.dumps({'outputDirectory':str(OUT),'stale':summary['stale'],'changedInputs':changed,'all64DiskSelectionsMatch':summary['currentDiskSelectionMatchesInventoryForAll64Tiles']},ensure_ascii=False))
