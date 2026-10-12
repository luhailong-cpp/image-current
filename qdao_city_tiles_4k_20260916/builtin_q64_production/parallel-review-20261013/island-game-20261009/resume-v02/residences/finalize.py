import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
OUT=BASE/'parallel-review-20261013/island-game-20261009/resume-v02/residences'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):
    p=Path(p);return p if p.is_absolute() else ROOT/p
def now():return datetime.now(timezone.utc).isoformat()
def write(name,j):(OUT/name).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
j=read(OUT/'snapshot.json');corner=read(OUT/'corner.json')
findings={
'r02_c02_s04_01_a01':('failed_layout_and_south_join','南边 y8192 的铺地突然接成海岸岩石与大叶灌木；完整原生片另新增院落、房屋、兔子、家具，不符合本坐标近景。生产已有 rejected_layout，保持未采用。'),
'r02_c10_p04_04_v02':('failed_production_geometry_review_retained','本次查看南边原像素裁片；生产独立检查明确记录南边斜石缝偏移，保持失败，不以本次较大裁片未见显著断层覆盖原未通过结论。'),
'r02_c11_p04_04_v02':('passed_available_south_segment','已采用核心的南边 1024 像素段红梁、米白墙板连续；仅这一段可复用，不涵盖整块、其余三侧或全图。'),
'r02_c12_p04_04_v03':('local_geometry_observed_no_formal_acceptance','南、东各 1024 像素段的红柱、树叶、岩壁和金色构件在本次裁片内连贯；未将候选改为采用，完整核心布局和其他边仍按生产检查处理。')}
for s in j['seams']:
    status,note=findings[s['nativeId']];s.update(visualReviewed=True,reviewedAtUtc=now(),status=status,finding=note,formalAccepted=False)
corner.update(visualReviewed=True,reviewedAtUtc=now(),status='local_geometry_observed_no_formal_acceptance',finding='交汇 (49152,8192) 的金色构件弧线与背景植被在 512 方形裁片内连续；不代表其他边通过。',formalAccepted=False)
write('visual-review.json',{'seams':j['seams'],'corner':corner})
originals={}
for b in j['batches']:
    for n in b['native']:originals[n['file']['path']]=n['file']['sha256']
for n in j['neighborSources'].values(): originals[n['path']]=n['sha256']
for n in corner['sources']: originals[n['file']]=n['sourceSha256']
rehash=[{'path':p,'snapshotSha256':h,'currentSha256':sha(p),'unchanged':h==sha(p)} for p,h in originals.items()]
write('source-recheck.json',{'checkedAtUtc':now(),'images':rehash,'allUnchanged':all(x['unchanged'] for x in rehash)})
late={'checkedAtUtc':now(),'baselineSnapshot':(OUT/'snapshot.json').as_posix(),'batches':[]}
selectedTotal=0;nativeTotal=0
currentTiles=[]
for b in j['batches']:
    folder=Path(b['directory']);baseline={n['id'] for n in b['native']}
    files=sorted(folder.glob('native/*.png'))
    native=[]
    for f in files:
        with Image.open(f) as im:dims=list(im.size)
        native.append({'id':f.stem,'path':f.as_posix(),'sha256':sha(f),'dimensions':dims,'addedAfterSnapshot':f.stem not in baseline,'visualReviewScope':'not_reviewed_in_this_batch' if f.stem not in baseline else 'see visual-review.json or retained production rejection'})
    nativeTotal+=len(native)
    tiles=[]
    for t in b['tiles']:
        sels=[]
        for f in folder.glob('selections/**/*.json'):
            d=read(f)
            if d.get('tileId')==t['tileId']:sels.append((f,d))
        sels.sort(key=lambda z:(z[1].get('createdAtUtc',''),z[0].name))
        matrix=[[None]*4 for _ in range(4)];selection=None
        if sels:
            f,d=sels[-1];selection={'path':f.as_posix(),'sha256':sha(f),'createdAtUtc':d.get('createdAtUtc')}
            for coord,n in d.get('selected',{}).items():
                m=re.search(r'_[ps](\d+)_(\d+)',coord); p=path(n['file']);h=sha(p)
                matrix[int(m[1])-1][int(m[2])-1]={'id':n['id'],'path':p.as_posix(),'sha256':h,'matchesSelection':h==n['sha256']}
        count=sum(x is not None for row in matrix for x in row);selectedTotal+=count
        record={'tileId':t['tileId'],'selection':selection,'selectedCoreMatrix':matrix,'selectedCoreCount':count,'missingCoreCount':16-count,'full4096Candidate':None,'formalAccepted':False,'selectedCountAtVisualSnapshot':t['selectedCoreCount']}
        tiles.append(record);currentTiles.append(record)
    # Only current local review records; skip anchors and historical full-region inventories.
    reviews=[]
    for sub in ['qa','reviews-input']:
        for f in sorted((folder/sub).glob('*.json')):
            if 'review' in f.name:reviews.append({'path':f.as_posix(),'sha256':sha(f),'content':read(f)})
    late['batches'].append({'key':b['key'],'native':native,'tiles':tiles,'currentProductionReviews':reviews})
write('end-delta.json',late)
allnodes={t['tileId'] for t in currentTiles}
edges=[]
for t in currentTiles:
    tid=t['tileId'];r=int(tid[1:3]);c=int(tid[5:7])
    for direction,dr,dc in [('north',-1,0),('south',1,0),('west',0,-1),('east',0,1)]:
        nr,nc=r+dr,c+dc;nid=f'r{nr:02}_c{nc:02}'
        if not 1<=nr<=14 or not 1<=nc<=14: state='map_outer_boundary'
        elif nid in allnodes:state='missing_selected_shared_edge_cores'
        elif nid in j['neighborSources']:state='neighbor_image_exists_target_edge_incomplete'
        else:state='outside_this_delta_scope_no_neighbor_assumed'
        edge={'tileId':tid,'direction':direction,'neighbor':nid,'status':state,'whole4096EdgeAccepted':False}
        seen=[s for s in j['seams'] if s['nativeId'].startswith(tid+'_') and s['direction']==direction]
        if seen:edge['inspectedSegments']=[{'nativeId':s['nativeId'],'worldBox':s['worldBox'],'status':s['status'],'evidence':s['output']['path']} for s in seen]
        edges.append(edge)
write('edge-status.json',{'edges':edges})
summary={'createdAtUtc':now(),'task':'residence incremental read-only audit','visualSnapshotAtUtc':j['createdAtUtc'],'metadataRefreshAtUtc':late['checkedAtUtc'],'tileCount':12,'targetCoreCount':192,'snapshotNativeImageCount':sum(len(b['native']) for b in j['batches']),'currentNativeImageCount':nativeTotal,'snapshotSelectedCoreCount':sum(t['selectedCoreCount'] for b in j['batches'] for t in b['tiles']),'currentSelectedCoreCount':selectedTotal,'currentMissingSelectedCoreCount':192-selectedTotal,'full4096CandidateCount':0,'formalAcceptedCount':0,'selectedCoreMatrixFile':(OUT/'end-delta.json').as_posix(),'currentTiles':currentTiles,'reviewedSeamStripCount':len(j['seams']),'reviewedFourWayCount':1,'unchangedSourceImageCount':len(rehash),'sourceImagesUnchanged':all(x['unchanged'] for x in rehash),'reviewedCoreIds':list(findings),'generationPerformed':False,'productionWrites':False,'gitMutation':False,'modelEvidence':'existing native records actualModel null / not returned; no image generation in audit','unreviewedAfterSnapshotNativeIds':[n['id'] for b in late['batches'] for n in b['native'] if n['addedAfterSnapshot']],'outputs':['snapshot.json','end-delta.json','visual-review.json','source-recheck.json','edge-status.json','review.md']}
write('summary.json',summary)
lines=['# 八仙岛东西民居增量检查','',f'12 个新划拨坐标仍无完整 4096 候选或正式验收。视觉快照有 {summary["snapshotNativeImageCount"]} 张原生图、{summary["snapshotSelectedCoreCount"]} 个已选核心；结束时的元数据更新记录 {nativeTotal} 张原生图、{selectedTotal}/192 个已选核心。快照后新片仅登记来源，不套用旧接缝结论。','',f'视觉输入冻结于 {j["createdAtUtc"]}；元数据更新于 {late["checkedAtUtc"]}，均为 UTC。所有写入限于当前检查目录。','', '| 坐标 | 当前已选核心 | 状态 |','| --- | ---: | --- |']
for t in currentTiles:lines.append(f'| {t["tileId"]} | {t["selectedCoreCount"]}/16 | 整块及缺邻边待查 |')
lines+=['','西侧 r02_c02_s04_01_a01 新增不属于坐标近景的房屋、院落、兔子和家具；南边在世界 y8192 处从铺地直接切换到海岸岩石与植被，失败且未采用。东侧 r02_c12_p04_04_v02 已有构图失败记录，来源 hash 匹配，继续复用未通过状态。','', '东侧 r02_c10_p04_04_v02 的生产记录指出南边斜石缝偏移，本次保留失败。r02_c11_p04_04_v02 已选核心的南边 1024 像素段红梁和墙板连续。r02_c12_p04_04_v03 的南、东各 1024 像素段及东南交汇 (49152,8192) 在本次裁片内连贯；这只说明可见局部几何，没有改变生产选择，也不构成完整核心、整块或全图验收。','',f'5 张接缝裁片和 1 张四交汇裁片均为整数坐标原像素拼接，未缩放、羽化或生成新细节。{len(rehash)} 张所用源图结束复核 hash 均'+('未变。' if summary['sourceImagesUnchanged'] else '记录于 source-recheck.json，存在变化时须重验。'),'','当前所选 4×4 矩阵、每格来源 hash、快照后新增未查图和生产拒收记录见 [end-delta.json](end-delta.json)。全部边界的缺图和局部检查状态见 [edge-status.json](edge-status.json)。缺少目标核心的边界继续保留待查；从未把缺图填成整块。','', '局部证据：','']
for s in j['seams']:lines.append(f'- [{s["nativeId"]} {s["direction"]}]({Path(s["output"]["path"]).name})：{s["status"]}。')
lines.append(f'- [r02 r03 c12 c13 四交汇]({Path(corner["file"]).name})：仅局部几何已查看。')
(OUT/'review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:summary[k] for k in ['currentNativeImageCount','currentSelectedCoreCount','currentMissingSelectedCoreCount','unchangedSourceImageCount','sourceImagesUnchanged','unreviewedAfterSnapshotNativeIds']},ensure_ascii=False,indent=2))
