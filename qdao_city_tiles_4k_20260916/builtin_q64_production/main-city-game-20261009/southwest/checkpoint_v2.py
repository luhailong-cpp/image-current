
from production import *
U=ROOT/'r11_c05'
final=T/'repairs'/'output'/'r10_c05.repaired.candidate.png'
partial=U/'output'/'r11_c05.partial-p01_01-p01_04.png'
assert sha(final)=='f228d0e07c4ed329bdcce87a46abb0ddeb48c9688dab1d86b33456051797ecad'
assert sha(partial)=='84d85d52733a221d2bf1e33f67f377f6014d89e72f484a9fbaeb1a1660f11e7c'
verification=json.loads((ROOT/'verification.json').read_text(encoding='utf-8-sig'));assert verification['passed']
qa=T/'qa'/'current';qa.mkdir(exist_ok=True)
with Image.open(final) as im:
    assert im.size==(4096,4096)
    crops=[]
    for x in [1024,2048,3072]:
        for axis in ['vertical','horizontal']:
            box=(x-128,0,x+128,4096) if axis=='vertical' else (0,x-128,4096,x+128)
            name=f'seam_{axis}_{x}.png';dest=qa/name;im.crop(box).save(dest)
            crops.append({'file':str(dest),'sha256':sha(dest),'box':list(box),'resampled':False})
    for y in [1024,2048,3072]:
        for x in [1024,2048,3072]:
            box=[x-256,y-256,x+256,y+256];dest=qa/f'intersection_{x}_{y}.png';im.crop(box).save(dest)
            crops.append({'file':str(dest),'sha256':sha(dest),'box':box,'resampled':False})
write(qa/'derivation.json',{'source':str(final),'sourceSha256':sha(final),'operation':'exact native QA crops; not new artwork','crops':crops})
review={'reviewedAtUtc':now(),'candidate':str(final),'sha256':sha(final),'reviewers':['primary production worker','independent coordinate/seam audit subagent'],'scope':'Original full internal seams and intersections; all stone-affected seams after 8 refinements; both local-repair regions and all four perimeters after assembly. Unchanged areas carry their preceding review. Current crops are regenerated from exact selected final candidate.','visualStatus':'internal_QA_passed_external_seams_pending','internalGeometry':'No remaining obvious broken plank lines, ivory arc breaks, stair-edge kinks or curb fractures observed.','material':'Dense stone pattern reduced with 8 native edits; polygonal wood-tone seam and 2 tiny stair edge kinks repaired with 2 native localized edits.','resolvedIssues':['wood-local-tone','stone-material-density','two-small-stair-edge-kinks'],'externalSeamsReviewed':False,'formalAccepted':False,'clientMappingValidated':False,'capacity5000Validated':False,'remainingIssues':[{'id':'external-borders','status':'pending_adjacent_tile_QA','description':'r11_c05 partial upper boundary shows slight leaf-tone variation; other adjacent tiles do not yet exist.'}],'qaDirectory':str(qa),'localRepairEvidence':[str(T/'qa'/'local-wood'),str(T/'qa'/'local-stone')]}
write(T/'qa'/'visual-review.json',review)
r11review={'reviewedAtUtc':now(),'candidate':str(partial),'sha256':sha(partial),'pixels':[4096,1024],'reviewers':['primary production worker','independent next-tile QA subagent'],'scope':'All3 full-height internal vertical seams, partial preview and4 upper boundary segments.','internalGeometry':'reviewed_no_obvious_discontinuity','visualStatus':'material_and_external_boundary_refinement_needed','issues':[{'id':'native-tone-seams','severity':'P2','description':'Local warm/cool polygonal stone-tone boundaries near x1024 and especially x3072; x2048 mild.','candidateRegions':[[896,0,1152,1024],[2944,125,3200,235],[2944,333,3200,445],[2944,560,3200,670]]},{'id':'upper-leaf-tone','severity':'P2','description':'First upper boundary section has slight horizontal leaf-tone difference; stair and curb geometry broadly aligned. Preserve r10 selected output when fixing new tile edge.'}],'formalAccepted':False,'crossTileUpperBoundaryAccepted':False,'unproducedNativePatches':12}
write(U/'qa'/'visual-review.json',r11review)
records=list(ROOT.rglob('*.generation.json'));rejected=[p for p in records if 'rejected' in p.parts]
selected=json.loads((T/'refinement'/'selection.json').read_text(encoding='utf-8-sig'))
p={'zone':'southwest','updatedAtUtc':now(),'status':'in_progress_checkpoint','tileRows':[9,16],'tileColumns':[1,8],'assignedTileCount':64,'firstTile':'r10_c05','activeTile':'r11_c05','generatedNativeCount':len(records),'rejectedNativeCount':len(rejected),'failedBuiltinCallCount':2,'selectedNativePatchCount':20,'usableNativeCount':20,'selectedLocalRepairCount':2,'selectedNativeSourceCount':22,'refinedNativeCount':len(selected),'complete4kCandidateCount':1,'partialTileCount':1,'formalAcceptedCount':0,'untouchedTileCount':62,'remainingTilesWithout4kCandidates':63,'candidate':str(final),'candidateSha256':sha(final),'preview':str(T/'qa'/'refined-preview.png'),'partial':str(partial),'partialSha256':sha(partial),'partialPixels':[4096,1024],'partialCoreWorldBox':[16384,40960,20480,41984],'firstCandidateCoreWorldBox':[16384,36864,20480,40960],'nativeDimensionsVerified':[1254,1254],'corePixels':1024,'haloPixels':115,'adjacentOverlapPixels':230,'internalSeamReview':str(T/'qa'/'visual-review.json'),'partialReview':str(U/'qa'/'visual-review.json'),'nextStep':'修订r11_c05首排局部石材色缝及跨r10上边叶片色阶，保留r10候选不变；继续从r11_c05/p02_01真实原生生成剩余12片，完整后再导出4096候选。','nextPreparedRequest':str(U/'prompts'/'p02_01.request.json'),'nextPreparedSeed':str(U/'guides'/'p02_01.continuity-seed.png'),'nextPreparedRequestNeedsMacroCropReview':True,'actualModel':None,'actualQuality':None,'modelEvidence':'Host-managed image_gen exposes no actual model/quality fields. Config target is recorded separately for every generation.','apiUsed':False,'clientMappingValidated':False,'capacity5000Validated':False,'finalCityComplete':False,'artifactsVerification':str(ROOT/'verification.json')}
write(ROOT/'progress.json',p)
cp=json.loads((U/'checkpoint.json').read_text(encoding='utf-8-sig'));cp.update({'updatedAtUtc':now(),'status':'first_row_partial_exported_QA_needs_refinement','nativePatchCount':4,'generationReturnCount':7,'rejectedReturnCount':3,'partial':str(partial),'partialPixels':[4096,1024],'review':str(U/'qa'/'visual-review.json'),'nextStep':p['nextStep'],'preparedPatch':'p02_01','formalAccepted':False});write(U/'checkpoint.json',cp)
manifest={'updatedAtUtc':now(),'currentCandidate':{'file':str(final),'sha256':sha(final),'pixels':[4096,4096],'internalQa':'passed','externalQa':'pending','formalAccepted':False},'currentPartial':{'file':str(partial),'sha256':sha(partial),'pixels':[4096,1024],'internalGeometry':'reviewed','materialQa':'needs_refinement','formalAccepted':False},'records':str(ROOT/'verification.json'),'assemblyChain':[str(T/'output'/'assembly.json'),str(T/'repairs'/'output'/'wood-repaired.candidate.repair-assembly.json'),str(T/'repairs'/'output'/'r10_c05.repaired.candidate.repair-assembly.json')],'reconstruction':'assemble.py then local_repairs.py wood then local_repairs.py stone. Native source patches remain current in-process edge/repair inputs. Intermediate assembly PNGs retired after verifying final source references.'}
write(ROOT/'delivery.json',manifest)
readme='''# 西南分区实际制作进度

2026-10-09：已形成1块4096×4096候选，并向南扩展了下一块的4096×1024首排。正式验收仍为0，西南64块尚未全部完成。

- [r10_c05当前候选](r10_c05/repairs/output/r10_c05.repaired.candidate.png) · [预览](r10_c05/qa/refined-preview.png) · [内部复核](r10_c05/qa/visual-review.json)
- [r11_c05首排局部](r11_c05/output/r11_c05.partial-p01_01-p01_04.png) · [预览](r11_c05/qa/partial-p01_01-p01_04/preview.png) · [待修问题](r11_c05/qa/visual-review.json)
- [准确进度与续产断点](progress.json) · [当前文件索引](delivery.json) · [来源与引用验证](verification.json) · [批次设置](batch-evidence.json)

累计36张真实生图返回：6张拒稿，20张当前空间分片、8张被材质修订替代的源片、2张当前局部修补。另有2次未返回图片的网络失败。当前直接参与作品的来源共22张，实测均为1254×1254，参考文件与提示词哈希已核验。整块和首排均由原生像素拼接并裁除外侧115像素，没有放大总览图或用引导像素充作游戏成品。

r10_c05覆盖[16384,36864,20480,40960)，是擂台近景局部。已完成8张石材编辑及2张局部接缝修补；内部几何与材质复核通过。四边及跨块交点仍未正式验收。

r11_c05目前覆盖[16384,40960,20480,41984)，首排4张已生成，剩12张未生成。内部台阶边线连续；x≈1024、3072附近石面冷暖色块和上边叶片轻微色阶仍需修订。先处理这些问题，保持r10候选不变，再继续p02_01。其真实输入已准备在prompts/p02_01.request.json，生图前必须实际查看guides/p02_01.continuity-seed.png并补充准确近距离裁切描述。不要把首排局部计作第二块完整4K成品。

全部通过内置image_gen生成。实际model和quality没有工具参数或返回值，均标记未确认；每图仍保存配置目标、实际提交提示词、参考路径与哈希、原始返回尺寸与回执。未使用付费API。世界范围映射、5000人容量和客户端接入均未验证。

当前原生片和参考输入仍支撑未完成图块的边缘扩展、修补和装配重建，按用途保留。被当前候选替代的完整拼接中间图与旧QA裁图在核验后清理，拒稿图片不复制到本分区，文字记录保留；清理明细见cleanup-v2.json。只修改southwest目录，未修改中央工程、其他分区、共享参考、客户端或Git。
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
old=[T/'output'/'r10_c05.candidate.png',T/'repairs'/'output'/'wood-repaired.candidate.png']+list((T/'qa'/'candidate').glob('*.png'))
cleanup=[]
for f in old:
    assert f.resolve().is_relative_to(ROOT.resolve())
    if f.exists():cleanup.append({'file':str(f),'sha256':sha(f),'reason':'Superseded assembly or QA pixels; current candidate, current QA and all selected source references verified.'})
write(ROOT/'cleanup-v2.json',{'createdAtUtc':now(),'status':'planned_after_verification','currentCandidate':str(final),'currentCandidateSha256':sha(final),'items':cleanup,'deletionScope':'Only named files under southwest; never shared sources or host generated-image directory.'})
print(json.dumps({'generatedNativeCount':len(records),'rejectedNativeCount':len(rejected),'selectedNativeSourceCount':22,'cleanupFileCount':len(cleanup),'candidateSha256':sha(final),'partialSha256':sha(partial)},ensure_ascii=False))

