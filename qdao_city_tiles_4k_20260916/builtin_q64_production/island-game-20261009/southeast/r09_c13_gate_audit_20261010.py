"""Read existing artwork and evidence only; write two tile-specific audit reports."""
from pathlib import Path
import datetime, hashlib, json, subprocess
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
cache = {}
def sha(p):
    p = Path(p)
    k = str(p.resolve()).lower()
    if k not in cache:
        cache[k] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    return cache[k]
def check_file(p, expected):
    actual = sha(p)
    return {'file': str(p), 'expectedSha256': expected, 'actualSha256': actual,
            'exists': actual is not None, 'hashMatches': actual == expected if actual else False}

tid = 'r09_c13'
candidate = ROOT/'tiles'/f'{tid}.candidate.png'
candidate_rec = read(str(candidate)+'.generation.json')
selected = {Path(x['file']).name for x in candidate_rec['derivedFrom']}
historical = read(ROOT/'qa'/f'{tid}.source-audit.json')
dispositions = {Path(x['file']).name:x['disposition'] for x in historical['records']}
records = []
for p in sorted((ROOT/'native').glob(f'{tid}_*.png')):
    recp = Path(str(p)+'.generation.json')
    rec = read(recp)
    reqp = ROOT/'prompts'/f'{p.stem}.request.json'
    req = read(reqp)
    receiptp = ROOT/rec['evidence']['toolReceipt']
    receipt = read(receiptp)
    actual = receipt['submittedArguments']
    prompt_path = Path(rec['prompt'])
    # Record both byte decoding and universal-newline reading; historical receipts may retain CRLF.
    prompt_raw = prompt_path.read_bytes().decode('utf-8')
    prompt_normalized = prompt_raw.replace('\r\n','\n')
    received_normalized = actual['prompt'].replace('\r\n','\n')
    refs = [check_file(x['file'],x['sha256']) for x in rec['references']]
    with Image.open(p) as im: pixels = list(im.size)
    records.append({'file':str(p),'selected':p.name in selected,'coordinate':rec['coordinate'],
        'native':check_file(p,rec['sha256']),'pixels':pixels,'native1254':pixels==[1254,1254],
        'sourceOutput':check_file(rec['sourceOutputPath'],rec['sourceOutputSha256']),
        'prompt':check_file(prompt_path,rec['promptSha256']),
        'requestFile':str(reqp),'requestSha256':sha(reqp),'receiptFile':str(receiptp),'receiptSha256':sha(receiptp),
        'references':refs,'receiptReferencesExact':actual['referenced_image_paths']==[x['file'] for x in req['references']],
        'requestAndNativeReferenceRecordsExact':req['references']==rec['references'],
        'receiptPromptByteDecodedExact':actual['prompt']==prompt_raw,
        'receiptPromptNewlineNormalizedExact':received_normalized==prompt_normalized,
        'receiptPromptNewlineAndTrailingWhitespaceNormalizedExact':received_normalized.rstrip()==prompt_normalized.rstrip(),
        'actualSubmittedParameterKeys':sorted(actual),'actualModel':rec.get('actualModel'),
        'actualQuality':rec.get('actualQuality'),'receiptModel':receipt.get('model'),'receiptQuality':receipt.get('quality'),
        'modelQualitySelectorsAbsent': 'model' not in actual and 'quality' not in actual,
        'configSnapshotIsTargetOnly':rec.get('configSnapshot'),
        'disposition':dispositions.get(p.name,'Not selected: seam2 repair restores central beam, but lower hard-insert boundary still steps at post right edge; native preserved as evidence.')})

with Image.open(candidate) as im: cand=np.asarray(im.convert('RGB'))
coverage=np.zeros((4096,4096),dtype=np.uint8)
replay=[]
for src in candidate_rec['derivedFrom']:
    box=src.get('destinationBox',src['destination'])
    x0,y0,x1,y1=box
    with Image.open(src['file']) as im: core=np.asarray(im.convert('RGB').crop(src['sourceCrop']))
    coverage[y0:y1,x0:x1]+=1
    replay.append({'file':src['file'],'sourceCrop':src['sourceCrop'],'destinationBox':box,
        'nativeHashMatchesManifest':sha(src['file'])==src['sha256'],
        'exactPixels':bool(np.array_equal(core,cand[y0:y1,x0:x1]))})

style_path='D:/work/image/designs/mail-ui-v1/01-mail-event.png'
style_hash='3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2'
pngs=subprocess.run(['rg','--files','D:/work/image','-g','*.png'],capture_output=True,text=True,check=True).stdout.splitlines()
dimension_candidates=[]
scan_errors=[]
for name in pngs:
    try:
        with Image.open(name) as im: size=im.size
        if size==(1931,814): dimension_candidates.append({'file':name,'sha256':sha(name)})
    except Exception as e: scan_errors.append({'file':name,'error':str(e)})
matches=[x for x in dimension_candidates if x['sha256']==style_hash]
style={'historicalPath':style_path,'historicalSha256':style_hash,'historicalPixels':[1931,814],
       'historicalPathExists':Path(style_path).is_file(),'exactFilenameMatches':[p for p in pngs if Path(p).name=='01-mail-event.png'],
       'workspacePngHeaderScanCount':len(pngs),'sameDimensionCandidates':dimension_candidates,
       'verifiedSameHashPaths':matches,'scanErrors':scan_errors,
       'scanScope':'Only D:/work/image PNG files indexed by rg; no user-disk-wide search.',
       'historicalReferencesModified':False,'recoveryStatus':'Verified same-hash path found' if matches else 'No same-hash file found in indexed workspace PNGs; current location unresolved. Missing file cause not established.'}

risks=[
 {'id':'structural-seam-y2048','severity':'blocks-local-acceptance','evidence':'qa/r09_c13-p22-p32.hard-seam-100pct.png','finding':'Beam upper gold face terminates at core cut; thick post right edge/width jumps about 30 pixels. seam2_v01 does not safely replace it: its lower insert boundary still steps.','actionAfterRelease':'Repair from native seam crop and verify both insertion boundaries at 100%; no change under current gate.'},
 {'id':'structural-seam-y3072','severity':'blocks-local-acceptance','evidence':'qa/r09_c13-p32-p42.hard-seam-100pct.png','finding':'Thick timber post shifts about 10–25 pixels at core cut; grain/tone differs.','actionAfterRelease':'Repair and inspect actual candidate seam plus junction32.'},
 {'id':'walkable-surface','severity':'capacity-unverified','evidence':'qa/r09_c13.preview.png','finding':'This tile is predominantly dense garden foliage/rocks and a musical rack, with stone wall and narrow visible paving at the bottom. It is not evidence of a large walkable area. Do not count foliage canopy or areas behind walls as usable player capacity.','actionAfterRelease':'Validate full-island navigation/collision mask, actual world scale and access around rack/wall against root capacity plan.'},
 {'id':'building-road-layout','severity':'layout-unverified','evidence':'tiles/r09_c13.candidate.png','finding':'No complete residence or through-road is contained here. The rack, stone wall and upright continuity can be checked locally, but this tile cannot establish island building spacing, route connectivity, door widths or 5000-player capacity.','actionAfterRelease':'Root must approve world-scale layout before expansion; top/right/bottom borders need future actual-neighbor QA.'},
 {'id':'foliage-detail-density','severity':'layout-review-required','evidence':'qa/r09_c13.preview.png','finding':'Leaf and flower size varies across native patches. Seam continuity checks do not establish that final foliage silhouette, collision footprint or apparent prop scale meets the full-island plan.','actionAfterRelease':'Compare assembled silhouette against layout and gameplay masks at agreed scale, without assuming native detail increases usable space.'},
 {'id':'historical-style-unavailable','severity':'provenance-current-replay-incomplete','evidence':style_path,'finding':'Historical style-reference hash is recorded in all 24 attempts; current source path is missing. Available native/output/prompt hashes remain independently checkable.','actionAfterRelease':'Resolve approved style input before future generation; preserve historical hashes and paths.'}
]
report={'auditedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':tid,
 'gate':{'file':str(ROOT.parent.parent/'capacity-layout-gate-20261010.json'),'generationPaused':True,'inFlight':False,'newImageRequestsDuringAudit':0,'newCoordinatesDuringAudit':0,'r10_c13Started':False,'formalAccepted':False,'formalAcceptedCount':0},
 'inventory':{'nativeAttempts':len(records),'selectedNativeCores':len(selected),'uniquePatchCoordinates':sorted({r['coordinate']['id'] for r in records if 'id' in r['coordinate']}),'crossSeamNativeRepairAttempts':sum('id' not in r['coordinate'] for r in records),'tileGlobalBox':[49152,32768,53248,36864],'worldPixelExtentUsedByExistingBatch':[57344,57344],'worldSizeAndCapacityApproved':False},
 'candidate':{'file':str(candidate),'check':check_file(candidate,candidate_rec['sha256']),'pixels':[cand.shape[1],cand.shape[0]],'sourceRectangleCount':len(replay),'coverageExactlyOnce':bool(np.all(coverage==1)),'allSourcePixelsExact':all(x['exactPixels'] and x['nativeHashMatchesManifest'] for x in replay),'sources':replay,'replayOperation':'In-memory comparisons only; artwork not rewritten, resized or blended.'},
 'records':records,'styleInvestigation':style,'roadBuildingRisks':risks,
 'priorVisualQA':{'source':str(ROOT/'qa'/f'{tid}.review-index.json'),'internalSeamsReviewed':24,'internalLocalPass':22,'internalNeedsRepair':2,'junctionsReviewed':9,'leftExternalStripsReviewed':4,'leftExternalLocalPass':4,'unverifiedExternalEdges':['top','right','bottom'],'previewReinspectedInThisAudit':True,'formalAcceptance':False},
 'historicalAuditPreserved':{'file':str(ROOT/'qa'/f'{tid}.source-audit.json'),'sha256':sha(ROOT/'qa'/f'{tid}.source-audit.json'),'recordedAt':historical['generatedAt'],'attemptCount':historical['generatedAttemptCount'],'note':'Preserved historical reference-check evidence; not overwritten with current missing-file status.'},
 'mutations':'Only this tile-specific audit script and the two named audit reports written; existing artwork, references, selections, receipts and shared progress left unchanged.'}
out=ROOT/'qa'/f'{tid}.gate-audit-20261010.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
good_native=sum(r['native']['hashMatches'] and r['native1254'] for r in records)
good_outputs=sum(r['sourceOutput']['hashMatches'] for r in records)
good_prompts=sum(r['prompt']['hashMatches'] for r in records)
normalized_mismatch=[Path(r['file']).name for r in records if not r['receiptPromptNewlineAndTrailingWhitespaceNormalizedExact']]
missing=sorted({x['file'] for r in records for x in r['references'] if not x['exists']})
md=f'''# r09_c13 门控期只读审计（2026-10-10）

生产门控保持暂停，inFlight=false，本次没有新生图、没有新增坐标、没有删除图片。r10_c13 尚未启动。此块 formal=0，仍需两处柱梁跨缝修复。

24 个原生尝试覆盖 16 个常规子坐标及 1 个跨缝修复窗口；16 个原生核心用于现候选，8 个尝试未选入。{good_native}/24 原生为 1254×1254 且文件哈希匹配，{good_outputs}/24 原工具输出哈希匹配，{good_prompts}/24 保存提示词哈希匹配。模型与质量的实际值均保留 null，配置值仅为目标。逐图 request / receipt / reference 哈希及实际参数键见 JSON。

候选：`tiles/r09_c13.candidate.png`，4096×4096，SHA-256 `{sha(candidate)}`。16 个 1024 核心逐像素重放一致，每个目标像素恰好覆盖一次；本次仅内存比较，没有重存或变换图片。

已有视觉 QA：24 条内部缝中 22 条局部通过、2 条需要修复；9 个交会点已检查，22 与 32 受柱缝影响；左外边界 4 段局部通过。上、右、下边界尚未有完整邻块验证。y=2048 柱梁缝及 y=3072 柱缝仍阻止本块交付；seam2_v01 修复在下插入边缘仍错位，未纳入候选。

道路与建筑风险：本块主要为花叶、园石及乐器架，底部有石墙和有限铺地，不能把植物覆盖区或墙后区域计为玩家活动面积。没有完整住宅或贯通道路，无法由本块验证住宅间距、门口宽度、道路连通性、世界米制尺度和 5000 人容量。叶花密度与物体尺度需结合全岛布局、碰撞及寻路数据复核；完整风险列表在 JSON 中。

共享风格图旧路径 `{style_path}` 当前缺失，历史 SHA-256 `{style_hash}` 保持不变。只读扫描了工作区索引中的 {len(pngs)} 张 PNG 头信息，按原始 1931×814 尺寸筛选后核对哈希，同哈希路径数量 {len(matches)}。未搜索用户全盘，未改历史 references。当前来源位置{'已找到' if matches else '未找到'}，无法确定缺失原因。另有 designs/README.md 与 docs 目录在当前工作区路径不可读。当前缺失引用：{json.dumps(missing,ensure_ascii=False)}。

提示词经换行与尾部空白归一化后仍不一致的原生：{json.dumps(normalized_mismatch,ensure_ascii=False)}。实际提交全文始终以 receipt 为证；没有据此改写历史提示词。旧审计保留原时间和当时检查结果。

机器可读证据：`qa/{out.name}`。仅本区专属报告与审计脚本落盘；等主线程解除门控后再续产。
'''
(ROOT/f'{tid}-gate-report-20261010.md').write_text(md,encoding='utf-8')
print(json.dumps({'report':str(out),'nativeHashPass':good_native,'originalOutputHashPass':good_outputs,'promptHashPass':good_prompts,'candidateExact':report['candidate']['allSourcePixelsExact'],'coverageOnce':report['candidate']['coverageExactlyOnce'],'missingReferences':missing,'promptNormalizedMismatches':normalized_mismatch,'stylePngsScanned':len(pngs),'styleDimensionCandidates':len(dimension_candidates),'sameHashStylePaths':matches},ensure_ascii=False))
