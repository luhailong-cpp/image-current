from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import hashlib
import json
import re
import sys
from PIL import Image, ImageChops

sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(r'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\main-city-game-20261009')
ZONE = BASE / 'southwest'
OUT = Path(__file__).resolve().parent
evidence = {}

def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def tracked(p):
    p = Path(p).resolve()
    if not p.is_relative_to(BASE.resolve()):
        raise ValueError(f'Outside permitted production read scope: {p}')
    if not p.is_file():
        return {'file': str(p), 'exists': False}
    before = p.stat()
    result = {'file': str(p), 'exists': True, 'sha256': sha(p), 'bytes': before.st_size,
              'mtimeNs': before.st_mtime_ns}
    evidence[str(p)] = result
    return result.copy()

def read(p):
    tracked(p)
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

catalog_path = ZONE / 'current-candidates.json'
inventory_path = ZONE / 'pipeline-tools/local-delivery-inventory-20261013/inventory.json'
counts_path = ZONE / 'pipeline-tools/live-counts-20261010.json'
progress_path = ZONE / 'progress.json'
catalog = read(catalog_path)
inventory = read(inventory_path)
counts = read(counts_path)
progress = read(progress_path)
contract = read(BASE / 'production-contract.json')
by_inventory = {t['tile']: t for t in inventory['tiles']}
by_catalog = catalog['tiles']
counts_tiles = {t['tile']: t for t in counts['tiles']}
issues = []

# Read-only assembly provenance traversal; no production module is imported.
assembly_cache = {}
def assembly_chain(p):
    p = Path(p).resolve()
    if str(p) in assembly_cache:
        return assembly_cache[str(p)]
    entry = tracked(p)
    entry.update({'parents': [], 'nativeSourceCount': 0, 'repairContributorCount': 0})
    assembly_cache[str(p)] = entry
    if not p.exists():
        return entry
    x = read(p)
    entry['nativeSourceCount'] = len(x.get('nativeSources', []))
    entry['repairContributorCount'] = len(x.get('localNativeRepairs', x.get('patches', x.get('appliedProposals', []))))
    entry['composition'] = x.get('repairComposition', x.get('composition'))
    parents = []
    for key in ['sourceAssembly', 'baseNativeAssembly']:
        v = x.get(key)
        if isinstance(v, str): parents.append(v)
        elif isinstance(v, dict) and v.get('file'): parents.append(v['file'])
    for source in (x.get('sources', {}) or {}).values():
        if isinstance(source, dict):
            cp = source.get('candidate', {}).get('file')
            if cp:
                ap = Path(cp).parent / 'assembly.json'
                if ap.exists(): parents.append(str(ap))
    # Integration v1 records a separate inputs document with base assemblies.
    for key in ['inputsFile']:
        if x.get(key):
            inp = read(x[key])
            entry[key] = tracked(x[key])
            def find_assemblies(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if 'assembly' in k.lower() and isinstance(v, str) and v.endswith('.json'):
                            parents.append(v)
                        else: find_assemblies(v)
                elif isinstance(obj, list):
                    for v in obj: find_assemblies(v)
            find_assemblies(inp)
    for parent in dict.fromkeys(parents):
        if Path(parent).resolve() != p:
            entry['parents'].append(str(Path(parent).resolve()))
            assembly_chain(parent)
    return entry

reports = {}
report_paths = [ZONE / 'integrated-20261011/v5/qa-review.json',
               ZONE / 'pipeline-tools/col5-local-audit-20261013-v01/lane-state.json',
               ZONE / 'pipeline-tools/col5-local-audit-20261013-v01/lane-repair-queue.json',
               ZONE / 'pipeline-tools/col5-local-audit-20261013-v01/actual-views-and-findings.json',
               ZONE / 'r10_c08/pipeline/qa/right-lane-review-20261013-v01/lane-review-and-repair-queue.json',
               ZONE / 'r09_c03/pipeline/local-review-20261013-v01/left-lane-local-review-handoff.json',
               Path(progress['currentPartialReview'])]
report_paths += [Path(e['review']) for e in by_catalog.values() if e.get('review')]
report_paths += [ZONE / tid / 'pipeline/local-review-20261013-v01/visual-review-and-repair-queue.json'
                 for tid in ['r09_c01', 'r09_c02', 'r09_c03']]
for p in dict.fromkeys(report_paths):
    if p.is_file(): reports[str(p)] = read(p)

right_path = ZONE / 'r10_c08/pipeline/qa/right-lane-review-20261013-v01/lane-review-and-repair-queue.json'
right = reports[str(right_path)]
cross_edges = []
for edge in right['edges']:
    cross_edges.append({'report': str(right_path), 'reportSha256': evidence[str(right_path.resolve())]['sha256'], **edge})
shared = reports[str(ZONE / 'integrated-20261011/v5/qa-review.json')]
edge_map = {'west_horizontal': ['r10_c05','r11_c05'], 'east_horizontal': ['r10_c06','r11_c06'],
            'north_vertical': ['r10_c05','r10_c06'], 'south_vertical': ['r11_c05','r11_c06']}
for e in shared['sharedEdges']:
    cross_edges.append({'report': str(ZONE / 'integrated-20261011/v5/qa-review.json'),
                        'tiles': edge_map[e['id']], 'wholeTileAcceptance': False, **e})
col5_path = ZONE / 'pipeline-tools/col5-local-audit-20261013-v01/lane-repair-queue.json'
col5 = reports[str(col5_path)]
for edge, status in col5['priorChainStatus'].items():
    cross_edges.append({'report': str(col5_path), 'edge': edge, 'status': status, 'wholeTileAcceptance': False})

global_reference_counts = Counter()
tiles = []
native_total = 0
for row in range(9,17):
    for col in range(1,9):
        tid = f'r{row:02}_c{col:02}'
        t = by_inventory[tid]
        cat = by_catalog.get(tid)
        tile_out = {'tile': tid, 'coordinate': [row,col],
                    'coreWorldBox': [(col-1)*4096,(row-1)*4096,col*4096,row*4096],
                    'coverageState': t['coverageState'],
                    'currentCandidate': cat['candidate']['file'] if cat else None,
                    'currentCandidateSha256': cat['candidate']['sha256'] if cat else None,
                    'nativeManifest': None,
                    'selectedNativePatchCount': t['selectedNativePatchCount'],
                    'selectedIds': t['selectedIds'], 'missingPatchIds': t['missingPatchIds'],
                    'formalStatus': 'not_accepted', 'internalStatus': 'open_QA' if cat else 'incomplete_native_coverage',
                    'internalPassed': False, 'formalAccepted': False,
                    'references': [], 'nativeSources': [], 'existingReviews': [], 'crossTileEvidence': []}
        sel_path = ZONE / tid / 'refinement/selection.json'
        selection = {}
        if sel_path.exists():
            tile_out['selectionManifest'] = tracked(sel_path)
            selection = read(sel_path)
        else: tile_out['selectionManifest'] = None
        resolved = {}
        for rr in range(1,5):
            for cc in range(1,5):
                pid = f'p{rr:02}_{cc:02}'
                rp = ZONE / tid / selection.get(pid, f'native/{pid}.png.generation.json')
                if rp.exists(): resolved[pid] = str(rp.resolve())
        expected_records = {n['patch']:str(Path(n['record']).resolve()) for n in t['selectedNativeRecords']}
        tile_out['currentDiskSelectionMatchesInventory'] = resolved == expected_records
        if resolved != expected_records:
            issues.append({'tile':tid,'kind':'selection_manifest_changed','currentDisk':resolved,'inventory':expected_records})
        refs = {}
        for n in t['selectedNativeRecords']:
            native = tracked(n['file'])
            record = tracked(n['record'])
            with Image.open(n['file']) as im:
                native['actualPixels'] = list(im.size)
                native['mode'] = im.mode
            native['declaredHashMatches'] = native['sha256'] == n['sha256']
            record['declaredHashMatches'] = record['sha256'] == n['recordSha256']
            if not native['declaredHashMatches'] or not record['declaredHashMatches'] or native['actualPixels'] != [1254,1254]:
                issues.append({'tile': tid, 'kind': 'native_integrity', 'patch': n['patch']})
            x = read(n['record'])
            native.update({'patch': n['patch'], 'generationRecord': record,
                           'actualModel': x.get('actualModel'), 'actualQuality': x.get('actualQuality'),
                           'coordinates': x.get('coordinates'), 'neighborSources': x.get('neighborSources', [])})
            for rr in x.get('references', []):
                key = (rr.get('file'), rr.get('sha256'))
                if key not in refs: refs[key] = {**rr, 'selectedSlotUseCount': 0,
                                               'scope': 'recorded_reference_metadata_only'}
                refs[key]['selectedSlotUseCount'] += 1
                if any(s in str(rr.get('role','')).lower() for s in ['approved','primary','geometry','style','material']):
                    global_reference_counts[key] += 1
            tile_out['nativeSources'].append(native)
        tile_out['references'] = list(refs.values())
        native_total += len(tile_out['nativeSources'])
        tile_out['nativeDimensionsVerified'] = bool(t['selectedNativeRecords']) and all(n['actualPixels']==[1254,1254] for n in tile_out['nativeSources'])
        if cat:
            c = tracked(cat['candidate']['file']); ctx = tracked(cat['context']['file'])
            with Image.open(c['file']) as cim, Image.open(ctx['file']) as xim:
                c['actualPixels'] = list(cim.size); ctx['actualPixels'] = list(xim.size)
                core_crop_equal = ImageChops.difference(cim.convert('RGB'), xim.crop((115,115,4211,4211)).convert('RGB')).getbbox() is None
            c['declaredHashMatches'] = c['sha256']==cat['candidate']['sha256']
            ctx['declaredHashMatches'] = ctx['sha256']==cat['context']['sha256']
            tile_out.update({'candidateVerification': c, 'contextVerification': ctx,
                             'coreEqualsContextCrop': core_crop_equal})
            if c['actualPixels'] != [4096,4096] or ctx['actualPixels'] != [4326,4326] or not c['declaredHashMatches'] or not ctx['declaredHashMatches'] or not core_crop_equal:
                issues.append({'tile':tid, 'kind':'candidate_integrity'})
            ap = Path(cat.get('assembly') or ZONE / 'integrated-20261011/v5/assembly.json')
            tile_out['nativeManifest'] = str(ap)
            tile_out['assemblyEvidence'] = assembly_chain(ap)
        # Current generation-slot records are a distinct manifest from integrated repair provenance.
        tile_out['selectedSourceManifest'] = str(inventory_path)
        for rp, rx in reports.items():
            relevant = rx.get('tile') == tid or any(q.get('tile')==tid for q in rx.get('tileChecks', []))
            if rp == str(right_path) and tid in right['scope']: relevant = True
            if tid in ['r13_c05','r14_c05'] and 'col5-local-audit' in rp: relevant = True
            if relevant:
                tile_out['existingReviews'].append({'file':rp, 'sha256':evidence[str(Path(rp).resolve())]['sha256'],
                                                   'status':rx.get('status',rx.get('visualReviewStatus')),
                                                   'scope':'existing_recorded_review_reused_not_new_visual_acceptance'})
        for edge in cross_edges:
            if tid in json.dumps(edge, ensure_ascii=False): tile_out['crossTileEvidence'].append(edge)
        # Preserve all current partial rectangles, excluding retired versions.
        if not cat and t['selectedNativePatchCount']:
            outputs=[]
            for ap in (ZONE/tid/'pipeline/output').glob('*/assembly.json'):
                x=read(ap)
                used=x.get('usedPatchIds',[])
                if not used or not set(used).issubset(t['selectedIds']): continue
                src={n['id']:n['nativeSha256'] for n in x.get('nativeSources',[])}
                wanted={n['patch']:n['sha256'] for n in t['selectedNativeRecords']}
                if not all(src.get(k)==wanted[k] for k in used): continue
                out=x.get('output',{})
                if out.get('file') and Path(out['file']).is_file():
                    outputs.append({'assembly':str(ap), 'createdAtUtc':x.get('createdAtUtc'),
                                    'selectedRectangleInclusive':x.get('selectedRectangleInclusive'),
                                    'usedPatchIds':used, 'output':out})
            latest={}
            for output in outputs:
                key=str(output['selectedRectangleInclusive'])
                if key not in latest or str(output['createdAtUtc'])>str(latest[key]['createdAtUtc']): latest[key]=output
            tile_out['currentPartialRectangles']=list(latest.values())
            for part in tile_out['currentPartialRectangles']:
                assembly_chain(part['assembly']); part['outputVerification']=tracked(part['output']['file'])
                with Image.open(part['output']['file']) as pim: part['outputVerification']['actualPixels']=list(pim.size)
                part['outputVerification']['declaredHashMatches']=part['outputVerification']['sha256']==part['output']['sha256']
        tiles.append(tile_out)

# Compact copied findings retain report pointers and exact issue coordinates.
repair_items=[]
for rp,x in reports.items():
    for key in ['repairQueue','issues','openFindings','findings','remainingIssues']:
        if isinstance(x.get(key),list):
            for item in x[key]: repair_items.append({'report':rp,'reportSha256':evidence[str(Path(rp).resolve())]['sha256'],
                                                      'tile':x.get('tile'),'recordedFinding':item})

# Recheck tracked sources at completion and mark any changed inputs stale.
changed=[]
for p,e in list(evidence.items()):
    pp=Path(p)
    if not pp.exists() or sha(pp)!=e['sha256']: changed.append(p)
summary={'recordedAtUtc':datetime.now(timezone.utc).isoformat(), 'zone':'southwest',
         'scope':'Read-only current adopted source census; no new image generation, no artwork changes, no new visual acceptance.',
         'catalog':str(catalog_path),'catalogUpdatedAtUtc':catalog.get('updatedAtUtc'),
         'inventory':str(inventory_path),'countsSnapshotUtc':counts.get('snapshotCompletedAtUtc'),
         'targetDeduplicatedTileCount':64,'fullCurrentCandidateCount':len(by_catalog),
         'selectedNativePatchCount':native_total,'missingNativePatchCount':1024-native_total,
         'partialTiles':[{ 'tile':t['tile'], 'selectedNativePatchCount':t['selectedNativePatchCount'],
                          'missingPatchIds':t['missingPatchIds']} for t in tiles if 0<t['selectedNativePatchCount']<16],
         'untouchedTileCount':sum(t['selectedNativePatchCount']==0 for t in tiles),
         'tilesWithoutComplete4kCandidate':[t['tile'] for t in tiles if not t['currentCandidate']],
         'currentInternalPassed':0,'formalAccepted':0,'historicalApprovalNotAppliedToModifiedCandidates':True,
         'allSourceNativeSizes1254Square':all(t['nativeDimensionsVerified'] for t in tiles if t['selectedNativePatchCount']),
         'integrityIssueCount':len(issues),'integrityIssues':issues,
         'stale':bool(changed),'inputsChangedDuringCensus':changed,
         'currentModelEvidence':'Existing generation records actualModel and actualQuality are unconfirmed; requested config is not used as actual model evidence.',
         'crossZoneEvidence':'No current top or east zone-boundary acceptance found in inspected Southwest review reports; neighbor availability must be joined with the other zones by root.',
         'assemblyContract':{'tile':[4096,4096],'native':[1254,1254],'patchGrid':[4,4],'core':1024,'halo':115,'adjacentOverlap':230,
                             'coordinateConvention':'artwork pixel grid, half-open; not client world units',
                             'resizingFinalArtAllowed':False,'existingQuilt':'minimum-error rows then row joins; recorded feather up to 2px; mechanical validation does not establish geometry or visual acceptance'},
         'importantEvidence':[str(ZONE/'integrated-20261011/v5/qa-review.json'),str(right_path),str(col5_path),
                              str(ZONE/'r09_c03/pipeline/local-review-20261013-v01/left-lane-local-review-handoff.json')],
         'productionFrontiers':{'left':'r09_c03:p04_03,p04_04','right':'r10_c08:p01_03','central':'r13_c06:p01_03','col5':'r15_c05:p01_01'},
         'newGenerationOrAiRepairAllowed':False}
write('current-tiles.json',tiles)
write('summary.json',summary)
write('assembly-provenance.json',list(assembly_cache.values()))
write('cross-tile-evidence.json',cross_edges)
write('recorded-repair-findings.json',repair_items)
write('input-evidence.json',list(evidence.values()))
write('recorded-reference-use.json',[{'file':k[0],'recordedSha256':k[1],'selectedSlotUseCount':v,'actualReferencePixelsViewed':False} for k,v in global_reference_counts.items()])
with (OUT/'missing-patches.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['tile','missingPatchId'])
    for t in tiles:
        for pid in t['missingPatchIds']: w.writerow([t['tile'],pid])
text='''# Southwest 独立来源核验 v01\n\n本报告只读复用当前采用源与已有视觉检查，未生成或修改图像，也不新增视觉验收结论。\n\n- 去重目标 64 块；当前完整候选 15 块，部分覆盖 3 块，未覆盖 46 块。\n- 已采用空间原生槽 258/1024；缺 766 片，49 块尚无完整 4K 候选。\n- 当前内部通过 0，正式验收 0。旧 r10_c05 内部通过不迁移到修改后的当前候选。\n- 完整候选均核对 SHA-256、4096×4096，context 4326×4326 与中心裁切一致；原生片逐一核对 SHA-256、1254×1254 与 generation record。\n- 已有修补链另列 assembly-provenance.json，258 是空间槽位数，不能当作全部修补贡献源数量。\n\n采用路径、原生片源、缺片、记录参考与验收状态见 current-tiles.json；全部输入 hash 见 input-evidence.json。参考图只检查记录的选择与 hash 口径，本只读范围未延伸到外部参考图片实际像素。\n\n可靠复用 integrated v5：r10_c05/r11_c05 和 r10_c06/r11_c06 水平缝曾通过接续检查；整体石面材质仍待修。r10_c05/r10_c06 的 y≈40734 短斜边和 r11_c05/r11_c06 的材质亮度仍待修。\n\n10 月 13 日新增左侧、右侧、第 5 列检查报告已纳入。右侧报告的窄边观察没有关闭先前整段红栏杆/台阶结构问题；未查看面板、邻区缺失与未验收跨区边界保持待检。第 5 列 r12_c05/r13_c05 的顶边结构失败，r13_c05/r14_c05 仍有材质与叶片变化。具体位置与证据文件见 cross-tile-evidence.json 和 recorded-repair-findings.json。\n\n断点：r09_c03 缺 p04_03,p04_04；r10_c08 与 r13_c06 各只有 p01_01,p01_02；第 5 列下一未覆盖为 r15_c05:p01_01。所有新生图与 AI 返修继续受 GPT Image 2.5 实际路线核实门控。\n\n当前完整候选可以作为局部机械装配输入；其来源完整不表示视觉合格或地图完成。\n'''
text += f'\n核验完成时间 UTC：{summary["recordedAtUtc"]}；完整性问题 {len(issues)}；核验期间输入变更 {len(changed)}。\n'
(OUT/'REPORT.md').write_text(text,encoding='utf-8')
print(json.dumps({'outputDirectory':str(OUT),**{k:summary[k] for k in ['fullCurrentCandidateCount','selectedNativePatchCount','missingNativePatchCount','untouchedTileCount','integrityIssueCount','stale']}},ensure_ascii=False))
