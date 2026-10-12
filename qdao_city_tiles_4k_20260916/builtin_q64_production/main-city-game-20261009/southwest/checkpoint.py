"""Record the actual candidate and remove superseded local process images only."""
from production import *
assembly=json.loads((T/'output/assembly.json').read_text(encoding='utf-8-sig'))
candidate=T/'output'/f'{TILE}.candidate.png'
with Image.open(candidate) as im:
    im.load();assert im.size==(4096,4096)
assert len(assembly['nativeSources'])==16
assert sha(candidate)==assembly['output']['sha256']
issues=[
 {'id':'wood-local-tone','severity':'P2','status':'open','candidatePixelBox':[2985,825,3105,970],
  'description':'Subtle polygonal wood-tone transition near p01_03/p01_04 boundary. Board lines and cream arc are continuous; fix local tone without moving geometry.',
  'qaImage':'r10_c05/qa/candidate/intersection_x3072_y1024.png'},
 {'id':'stone-material-density','severity':'P2','status':'open','candidatePixelBox':[0,2460,4096,4096],
  'description':'Stair and side-wall stone has denser fragment-like brush marks than the approved temple close-view. Repaint cleaner natural grey stone while locking treads, risers, curb and light.',
  'reference':CONTRACT['detailStyleReference']},
 {'id':'external-borders','severity':'acceptance-gate','status':'pending_neighbor_generation',
  'description':'All four outer tile edges and cross-tile intersections still need adjacent native art and root review.'}
]
qa={'reviewedAtUtc':now(),'candidate':str(candidate),'sha256':sha(candidate),
    'scope':'All 6 full-length internal seams and 9 internal intersections visually reviewed using original-pixel QA crops; overview reviewed separately.',
    'reviewers':['primary generation worker','independent coordinate/seam audit subagent'],
    'internalGeometry':'No obvious broken boards, cream arcs, stair level discontinuities, railing or curb fractures found.',
    'visualStatus':'needs_material_and_local_tone_refinement','issues':issues,
    'formalAccepted':False,'externalSeamsReviewed':False,'clientMappingValidated':False,'capacity5000Validated':False}
write(T/'qa/visual-review.json',qa)
assembly['visualQa']=qa;write(T/'output/assembly.json',assembly)
deleted=[]
for p in list((T/'output').glob('*.partial-*.png'))+list((T/'qa').glob('partial-*/*.png'))+[T/'rejected/p01_01.attempt02/p01_01.png']:
    p=p.resolve()
    assert p.is_relative_to(ROOT.resolve())
    assert p.suffix=='.png'
    if p.exists():
        deleted.append({'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
        p.unlink()
for d in (T/'qa').glob('partial-*'):
    assert d.resolve().is_relative_to(ROOT.resolve())
    if not any(d.iterdir()):d.rmdir()
rp=T/'rejected/p01_01.attempt02/p01_01.png.generation.json'
rr=json.loads(rp.read_text(encoding='utf-8-sig'));rr['imageRetained']=False;rr['deletedAtUtc']=now();rr['deletionReason']='Rejected framing; corrected first patch and complete current candidate exist. Provenance text preserved.';write(rp,rr)
write(ROOT/'cleanup.json',{'recordedAtUtc':now(),'scope':'southwest only','candidateVerifiedBeforeDeletion':{'file':str(candidate),'sha256':sha(candidate)},'deletedImages':deleted,'retained':'16 active native patches, current candidate, current QA crops, layout/continuity guides and all prompt/model/source records are needed for remaining refinement and neighbor extension. Shared references and other zones untouched.'})
for rp in (T/'native').glob('*.generation.json'):
    rec=json.loads(rp.read_text(encoding='utf-8-sig'))
    rec['generatedAtEvidence']='Local record timestamp shortly after tool returned; the tool did not disclose a separate generation timestamp.'
    rec['visualStatus']='used_in_candidate_with_open_refinement_issues'
    write(rp,rec)
# Generation records changed only by adding explicit timestamp/QA evidence. Refresh their hashes.
for entry in assembly['nativeSources']:
    entry['recordSha256']=sha(ROOT/entry['recordFile'])
write(T/'output/assembly.json',assembly)
write(ROOT/'progress.json',{'zone':'southwest','updatedAtUtc':now(),'status':'first_4k_candidate_needs_refinement',
    'tileRows':[9,16],'tileColumns':[1,8],'assignedTileCount':64,'firstTile':TILE,
    'generatedNativeCount':17,'usableNativeCount':16,'rejectedNativeCount':1,'failedBuiltinCallCount':2,
    'complete4kCandidateCount':1,'formalAcceptedCount':0,'activeTile':TILE,'remainingTilesWithoutCandidates':63,
    'candidate':str(candidate),'candidateSha256':sha(candidate),'preview':str(T/'qa/candidate/preview.png'),
    'nativeDimensionsVerified':[1254,1254],'nativePatchGrid':[4,4],'corePixels':1024,'haloPixels':115,
    'internalSeamReview':str(T/'qa/visual-review.json'),'nextStep':'Refine r10_c05 wood tone at candidate box [2985,825,3105,970] and clean overly dense stone texture below y2460 using built-in native edits. Preserve 16-patch geometry and recheck all changed overlaps. Then extend south to r11_c05, first patch p01_01 with top230 native overlap from r10_c05/p04_01. No full southwest completion claim.',
    'nextTileAfterRefinement':'r11_c05','nextTileFirstCoreWorldBox':[16384,40960,17408,41984],
    'nextTileFirstContextWorldBox':[16269,40845,17523,42099],
    'actualModel':None,'actualQuality':None,'modelEvidence':'Host-managed image_gen; model and quality arguments/return values not disclosed. Each generation record retains config target separately.',
    'clientMappingValidated':False,'capacity5000Validated':False,'finalCityComplete':False})
rows=[]
for r in range(1,5):
    for c in range(1,5):
        n=pid(r,c);rows.append(f'| {n} | [原生图](r10_c05/native/{n}.png) | [生成记录](r10_c05/native/{n}.png.generation.json) | [提示词](r10_c05/prompts/{n}.prompt.txt) | 未确认 / 未确认 |')
readme='''# 西南分区实际制作进度

2026-10-09：首块 r10_c05 已形成 **4096×4096 候选**，未正式验收。由16张实测1254×1254的内置生图原生片连续扩展、230像素重叠拼接，最后裁去四边115像素。原生像素没有放大；layout-only引导像素没有拼入成品。

- [当前候选](r10_c05/output/r10_c05.candidate.png) · [预览](r10_c05/qa/candidate/preview.png)
- [真实进度和下一步](progress.json) · [拼接及多源记录](r10_c05/output/assembly.json) · [视觉复核及待修问题](r10_c05/qa/visual-review.json)
- [坐标](r10_c05/coordinates.json) · [批次设置和官方核对](batch-evidence.json) · [清理记录](cleanup.json)

累计17张真实原生返回，其中1张因视野错误拒用，16张进入当前候选；另有2次网络失败没有返回图片。64块分区中当前只有1个4K候选，正式验收0块。候选覆盖 `[16384,36864,20480,40960)`，只是擂台局部，锁妖塔与其他63块尚未制作。

六条内部完整接缝和九个交点均已实际查看，未见明显断板、断弧、错阶或石栏断裂。仍需修订木面局部色差 `[2985,825,3105,970]`，并把下部石阶/侧墙过密碎片状石纹收敛到道馆样板的干净灰石。外部块接缝未验收；世界范围、5000人容量和客户端接入未验证。

继续断点：先完成上述两项原生编辑与重叠复核，再向南推进 r11_c05。该块首片核心 `[16384,40960,17408,41984)`，上下文 `[16269,40845,17523,42099)`；将本块 p04_01 的底部230像素原样作为新片顶部上下文。不能仅复制或放大这张候选当作下一块。

全部使用宿主内置 image_gen，无付费API。配置目标与实际证据分开：官方核对保持本批目标，但工具不提供 model/quality 选择器或返回值，所以实际型号、质量均未确认。逐图记录保存目标快照、实际提示词、参考用途/哈希、原生尺寸、原始返回路径和回执；不把公告或提示词当作实际型号证据。

| 子片 | 当前图 | 来源 | 实际提交提示词 | 实际型号 / 质量 |
|---|---|---|---|---|
'''+ '\n'.join(rows)+'''\n
当前原生片、引导和QA仍用于修订与邻块扩展，按唯一在制稿保留。拒稿图片和被当前候选取代的局部拼接预览已在核实当前文件后删除，文字来源记录保留。未修改中央工程文件、其他分区、共享参考、客户端或Git。
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps({'generatedNativeCount':17,'usableNativeCount':16,'complete4kCandidateCount':1,'formalAcceptedCount':0,'candidateSha256':sha(candidate),'deletedSupersededImages':len(deleted),'next':'native material/tone refinement, then r11_c05'},ensure_ascii=False))
