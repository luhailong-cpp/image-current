from build_summary import *

def f_record(p):
    p=Path(p)
    return {'file':str(p),'sha256':sha(p)}

def finalize():
    coverage=read(OUT/'coverage-summary.json')
    index=read(OUT/'current-256-coordinate-index.json')['coordinates']
    byid={t['coordinate']:t for t in index}
    swnew=BASE/'southwest-col5-boundary/v001/visual-review.json'
    senew=BASE/'southeast-new-boundaries/v001/review.json'
    issues=[]
    issues.append({'id':'NW-stale-r07c06','kind':'REASSEMBLY_AND_CURRENT_INTERNAL_QA_REQUIRED','coordinate':'r07_c06','observation':'All16 selected source slots exist, but old4K candidate does not include current s02_02_orphanfix03.png. Old candidate excluded from current coverage.','evidence':f_record(NW/'r07_c06-stale-candidate.json'),'sourceStatus':'selected sources complete; old candidate stale','requiresAIRepairEstablished':False})
    issues.append({'id':'SW-new-r11c05-r12c05','kind':'AI_REPAIR_REQUIRED_GEOMETRY_AND_MATERIAL','pair':['r11_c05','r12_c05'],'worldBoundaryY':45056,'worldReviewBox':[16384,44896,20480,45216],'observation':'Gutter lines offset ~51/42px in segment1 (tile x410→359 and944→986); segment2 lower lines x1233/1572 start at cut; segment3 upper x2318 stops and lower x3020 starts; segment4 lower x3348/3623 starts at cut. Surface texture/value differs.','evidence':f_record(swnew),'newActualNativeReview':True})
    issues.append({'id':'SE-parasol-fold','kind':'AI_REPAIR_REQUIRED_GEOMETRY','pair':['r13_c13','r13_c14'],'worldBox':[53213,50516,53283,50650],'observation':'Red and ivory parasol stripe edges make a sharp simultaneous angular discontinuity at the actual core boundary x53248.','evidence':f_record(senew),'newActualNativeReview':True})
    issues.extend([
      {'id':'SW-v5-north-vertical','kind':'AI_REPAIR_REQUIRED_GEOMETRY','pair':['r10_c05','r10_c06'],'worldBoundaryX':20480,'worldYApprox':40734,'observation':'Short diagonal rim remains unclosed. Current candidate paths and hashes match v5 inspected sources.','evidence':f_record(ROOT/'southwest/integrated-20261011/v5/qa-review.json'),'reuseProof':f_record(SW/'cross-tile-evidence.json')},
      {'id':'SW-v5-south-vertical','kind':'AI_REPAIR_REQUIRED_MATERIAL','pair':['r11_c05','r11_c06'],'worldBoundaryX':20480,'worldYRange':[40960,45056],'observation':'Shared edge finish/brightness remains inconsistent; geometry-local observations do not clear material acceptance.','evidence':f_record(ROOT/'southwest/integrated-20261011/v5/qa-review.json'),'reuseProof':f_record(SW/'cross-tile-evidence.json')},
      {'id':'SW-left-c01-c02','kind':'RECORDED_EXTERNAL_FAILURE','pair':['r09_c01','r09_c02'],'worldBoundaryX':4096,'worldYRange':[33792,36864],'observation':'Rows2–4 gold/wood value changes; gold timber inset terminates against dark panel and beam tone steps.','evidence':f_record(SW/'cross-tile-evidence.json')},
      {'id':'SW-left-c02-c03-partial','kind':'RECORDED_PARTIAL_SOURCE_BOUNDARY_FAILURE','pair':['r09_c02','r09_c03'],'worldBoundaryX':8192,'worldYRange':[32768,36864],'observation':'Masonry bevel/grout discontinuity, gold/wood finish steps, red cloth and lantern finish cuts. Child has only14 selected cores; no complete current4K child is claimed.','evidence':f_record(SW/'cross-tile-evidence.json')},
      {'id':'SW-right-c07-c08','kind':'RECORDED_EXTERNAL_FAILURE_GEOMETRY_AND_MATERIAL','pair':['r09_c07','r09_c08'],'worldBoundaryX':28672,'worldYRange':[32768,36864],'observation':'Upper rim polygonal jog; ledge/truncation in segment3 and small rim/bevel gap in segment4; cellular stone texture variation.','evidence':f_record(SW/'cross-tile-evidence.json')},
      {'id':'SW-col5-r12-r13','kind':'RECORDED_EXTERNAL_FAILURE_GEOMETRY_AND_MATERIAL','pair':['r12_c05','r13_c05'],'worldBoundaryY':49152,'worldXRange':[16384,20480],'observation':'Existing four segment failure retained. This review independently proved all4 prior crops pixel-identical to current recomposed source strips.','evidence':f_record(swnew)}
    ])
    for e in read(EAST/'prior-finding-pixel-validation.json'):
        if not e.get('currentEvidenceValid') or 'inherited' not in e.get('status',''): continue
        child=e['pair'][1]; t=byid[child]; box=e.get('boxInChildRelativeCoordinates')
        issue={'id':'SE-inherited-'+child+'-'+e['id'],'kind':e['status'],'pair':e['pair'],'observation':e.get('description'),'evidence':f_record(EAST/'prior-finding-pixel-validation.json'),'priorVisualVerdict':e.get('priorVisualVerdict'),'currentPixelIdentityProved':True}
        if box: issue['worldBox']=[box[0]+t['worldBox'][0],box[1]+t['worldBox'][1],box[2]+t['worldBox'][0],box[3]+t['worldBox'][1]]
        issues.append(issue)
    se=read(senew)
    ep=BASE/'southeast-new-boundaries/v001/endpoint-review.json'
    if se.get('priorIssuesNotClosed'):
        remaining=[e for e in se['priorIssuesNotClosed'] if not (ep.exists() and e.get('tile')=='r14_c14' and '2842/2874' in e.get('location',''))]
        if remaining: issues.append({'id':'SE-additional-open-scope','kind':'PENDING_EXISTING_REVIEW_SCOPE','observation':remaining,'evidence':f_record(senew)})
    if ep.exists():
        issues.append({'id':'SE-r14c14-endpoints-current','kind':'SEE_CURRENT_NATIVE_ENDPOINT_REVIEW','evidence':f_record(ep),'details':read(ep)})
    save(OUT/'seam-repair-and-review-queue.json',{'createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Specific failed or pending breakpoints in captured existing sources; not a new image-generation job','issues':issues,'formalAcceptedCount':0})
    guardfiles=sorted(OUT.glob('source-guard-*.json'))
    guard=read(guardfiles[-1])
    grid=[]
    for r in range(1,17):
        chars=[]
        for c in range(1,17):
            t=byid[f'r{r:02}_c{c:02}']
            chars.append('C' if t['fullCurrent4KCandidate'] else 'F' if t['selectedCoreCount']==16 else 'p' if t['selectedCoreCount'] else '.')
        grid.append(f'r{r:02}  '+' '.join(chars[:8])+' | '+' '.join(chars[8:]))
    g=read(GROUP/'manifest.json')
    now=datetime.datetime.now(datetime.timezone.utc)
    lines=[
      '主城既有素材独立收尾检查 — v1',
      f'报告完成时点：{now.astimezone(ZoneInfo("America/New_York")).isoformat()} (America/New_York)',
      '本报告对应固定输入快照；生产窗口后续新候选不自动继承本次结论。',
      '',
      '结果：完成本批清点、可用局部拼接、缺块清单与断点核验。全地图尚未完成，正式验收0。',
      '256坐标去重后：48个当前完整4K候选；208坐标尚无当前完整候选。',
      '49坐标具备全部16片位（其中r07_c06旧4K过期）；9坐标部分覆盖；198坐标无选定核心。',
      '选定核心855/4096，缺3241片位。该数字为逻辑坐标覆盖，不是原始工具输出张数。',
      '',
      '分工                   目标  当前4K  全16片位  部分  无核心  已选核心',
    ]
    for name,z in coverage['perOwner'].items():
        lines.append(f'{name:24} {z["assignedCoordinates"]:3} {z["current4KCandidates"]:6} {z["fullSelectedCoreCoordinates"]:8} {z["partialCoordinates"]:4} {z["zeroSelectedCoreCoordinates"]:6} {z["selectedCoreSlots"]:8}')
    lines += [
      '',
      '覆盖图：C=当前完整4K候选，F=16片位齐但旧4K未计入，p=部分，.=无选定核心；均不代表正式验收。',
      '列   01 02 03 04 05 06 07 08 | 09 10 11 12 13 14 15 16',
      *grid,
      '',
      '局部可交付图：官府r03–r05/c04–c05共6块，世界像素框[12288,8192,20480,20480]。',
      '新看8段南界、6个子片交点和1个四块交点，15处均主要轮廓局部通过。',
      '旧南界证据8段中6段像素已变，已用当前整块南邻替换检查；2段相同也重看。',
      '既有内部/其他共享边QA沿当前候选哈希复用。未验北西东外邻，不扩张为全图验收。',
      '新合图为6张既有复合候选的原像素整数坐标拼接，无缩放/混合/补绘；不是新生图或单次原生4K。',
      '8192×12288 PNG逐行独立解码，与输入拼接像素SHA256一致：'+g['assembly']['pixelIdentityVerification']['actualRasterSHA256'],
      '原像素合图：'+g['assembly']['file'],
      '明确标注的缩小预览：'+g['labeledPreview']['file'],
      '源坐标、SHA256、100%裁片、逐处结论：'+str(GROUP/'manifest.json'),
      '',
      '新增待修：',
      '1. 西南r11_c05→r12_c05，world y45056：沟槽错位约51/42px及多处切线断头，石面材质不同。4段、3交点及7定位细图实际100%查看。',
      '2. 东南r13_c13→r13_c14，约world[53213,50516,53283,50650]：伞面红/米白条带在真核心边同时折角。',
      '东南指定12段边界：9段新看、3段像素一致复用，11段主要轮廓局部通过、1段失败；2个640交点局部过。',
      '东南r14_c15旧N01局部修复已过；未将旧失败再列为当前失败。r14_c14更深x2842/2874端点已补看1200×1280宽窗，局部主要轮廓通过，关闭该端点待验项。',
      '',
      '复用待修及待验：',
      '西南v5中央竖界短斜边未闭、材质亮度差；左路木梁/布料边界断层；右路弧边折角；r12_c05→r13_c05几何/材质失败。',
      '东南r14_c14→r14_c15的W01/W02/W03与材质watch、r14_c14→r15_c14的N01/N02、r15_c13→r15_c14的W01/W02，双侧当前像素继承已证实。',
      '东北r06_c13→r07_c13虽然整图hash变更，四个原尺寸边窗双侧像素完全相同，原局部通过/材质watch结论可复用。',
      '具体当前source、worldbox与证据索引：'+str(OUT/'seam-repair-and-review-queue.json'),
      '',
      '跨四大区：32条分区边界中，当前两侧完整候选齐全的边为0；中心四块也未齐。不得把邻区缺源写成接缝通过。',
      '官府外北/西/东六个邻块仍缺源：r02_c04/r02_c05/r03_c03/r03_c06/r04_c03/r04_c06。',
      '分区边界逐段可用片位：'+str(OUT/'four-zone-boundary-availability.json'),
      '',
      '来源与规则：',
      '布局/材质参考的所记hash延续同一批准合同。邮件风格历史PNG/JPG所记版本有差异，保留原记录；本只读范围未重开外部参考像素，不声称它们字节相同。',
      '选定片位中含已披露的同坐标返修衍生复合片，不把其数量当全新原生工具输出。实际型号未返回的历史源仍写未返回。',
      '已重读2026-10-13模型更正：现有免费入口2.5优先，不可用可用内置2.0；本检查分工没有生图/AI返修。',
      '原图、progress、索引、AGENTS均未写入；未安装模型/技能、未改凭据、未删除、未恢复已删目录、未做Git操作。',
      '',
      '过期检查：',
      '末尾guard先后捕获northwest/southwest progress变更，旧guard均标stale并保留；分别重新核对当前选片数量、采用manifest、catalog/inventory及partial数量一致，另存v2/v3基线。',
      f'最终guard：{guard["checkedAtUTC"]}；输入{guard["inputCount"]}个，缺失选片路径{guard["absentSelectedFileCount"]}个；stale={guard["stale"]}。',
      '最新guard：'+str(guardfiles[-1]),
      '原生产恢复后继续变更是下一批输入。任一已记录source/selection/adoption/review hash变化，依赖检查须标过期并重验。',
      '',
      '交付索引：',
      str(OUT/'current-256-coordinate-index.json'),
      str(OUT/'missing-current-4k-coordinates.json'),
      str(OUT/'missing-native-core-slots.json'),
      str(OUT/'coverage-summary.json'),
    ]
    (OUT/'REPORT.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    deliverables=[OUT/'REPORT.txt',OUT/'coverage-summary.json',OUT/'current-256-coordinate-index.json',OUT/'missing-current-4k-coordinates.json',OUT/'missing-native-core-slots.json',OUT/'four-zone-boundary-availability.json',OUT/'seam-repair-and-review-queue.json',GROUP/'manifest.json',Path(g['assembly']['file']),Path(g['labeledPreview']['file']),swnew,senew,guardfiles[-1]]
    if ep.exists(): deliverables.append(ep)
    save(OUT/'delivery-index.json',{'finalizedAtUTC':now.isoformat(),'scope':'Independent source-batch review; no production directory mutation','existingSourceBatchWorkComplete':True,'mapComplete':False,'formalAcceptedCount':0,'artifacts':[f_record(p) for p in deliverables],'currentGuardStale':guard['stale'],'nativeGroupPixelProofPassed':True})
    print(json.dumps({'report':str(OUT/'REPORT.txt'),'deliveryIndex':str(OUT/'delivery-index.json'),'issueRecords':len(issues),'stale':guard['stale'],'counts':coverage['counts']},ensure_ascii=False))

if __name__=='__main__': finalize()
