from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
import json,hashlib

OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(OUT/'manifest.json')
findings={
 'r11_c05--r12_c05-segment1':{
  'status':'fail_geometry_and_material','geometry':'The diagonal paving grooves have different phase on the two sides of the exact horizontal cut. Around local tile x410 above the cut the lower groove begins around x359; another above x944 resumes around x986. These are visible clipped/displaced line ends rather than a physical slab edge.',
  'locations':[{'tileLocalXAbove':410,'tileLocalXBelow':359,'worldY':45056,'approxWorldXAbove':16794,'approxWorldXBelow':16743},
               {'tileLocalXAbove':944,'tileLocalXBelow':986,'worldY':45056,'approxWorldXAbove':17328,'approxWorldXBelow':17370}],
  'material':'Dense small cellular/crosshatched marks and broad torn pale/grey wash remain; a unified quiet stone surface is not accepted.'},
 'r11_c05--r12_c05-segment2':{
  'status':'fail_geometry_and_material','geometry':'Two lower paving grooves start at the core boundary with no incoming groove north of the cut and no transverse joint to justify a T-end. One clear pointed start is near local tile x1572; the other is near x1233.',
  'locations':[{'tileLocalX':1572,'worldX':17956,'worldY':45056},{'tileLocalX':1233,'worldX':17617,'worldY':45056}],
  'material':'Fine woven/cellular marks north of the seam change to broader smooth/clouded wash below; the same exposed slab plane remains inconsistent.'},
 'r11_c05--r12_c05-segment3':{
  'status':'fail_geometry_and_material','geometry':'An upper diagonal groove ends at the cut near local tile x2318; its south continuation is absent. A different lower groove starts at the cut around x3020 without a north continuation.',
  'locations':[{'tileLocalX':2318,'worldX':18702,'worldY':45056},{'tileLocalX':3020,'worldX':19404,'worldY':45056}],
  'material':'Dense crosshatch/cellular stone across the north half and pale clouded wash below remain outside the quiet material target.'},
 'r11_c05--r12_c05-segment4':{
  'status':'fail_geometry_and_material','geometry':'Two descending dark paving grooves begin abruptly at the horizontal cut, around local tile x3348 and x3623. Both have unpaired pointed north ends on an otherwise continuous stone face.',
  'locations':[{'tileLocalX':3348,'worldX':19732,'worldY':45056},{'tileLocalX':3623,'worldX':20007,'worldY':45056}],
  'material':'Large irregular grey/pale islands and dense fine weave remain above the join; lower paint finish differs.'},
 'r11_c05--r12_c05-intersection-x1024':{
  'status':'fail_geometry_and_material','geometry':'The 512-square intersection retains the line phase mismatch immediately left of the subpatch junction: the dark groove near tile x944 on the upper source is near x986 on the lower source. The blue-grey slab also has a ragged grey/cream paint frontier below the junction.',
  'locations':[{'tileLocalXRange':[768,1280],'worldBox':[17152,44800,17664,45312],'tileBoundaryWorldY':45056}],
  'material':'Same blue-grey plane changes brush density and broad wash; dense pattern remains.'},
 'r11_c05--r12_c05-intersection-x2048':{
  'status':'fail_material_geometry_not_established','geometry':'No distinct groove crosses the center of the x2048/y45056 junction in this crop. Central seam geometry cannot be certified from the unmarked surface; this crop does not close the adjacent segment2/3 groove failures.',
  'locations':[{'tileLocalXRange':[1792,2304],'worldBox':[18176,44800,18688,45312],'tileBoundaryWorldY':45056}],
  'material':'Dense north-side cellular/crosshatch and ragged cool/pale wash become a broader, smoother paint field below; quiet material is not passed.'},
 'r11_c05--r12_c05-intersection-x3072':{
  'status':'fail_geometry_and_material','geometry':'A lower diagonal groove begins at the seam around tile x3020 within this intersection crop. The upper source contains no matching incoming groove; the pointed cut is unresolved.',
  'locations':[{'tileLocalXRange':[2816,3328],'worldBox':[19200,44800,19712,45312],'tileBoundaryWorldY':45056},
               {'tileLocalX':3020,'worldX':19404,'worldY':45056}],
  'material':'North retains dense cellular islands and fine weave with irregular grey/cream transitions; material remains failed.'}
}
for c in m['newReviewCrops']:
    c.update(findings[c['id']]);c['actualViewedAtNativePixels']=True;c['viewTool']='view_image';c['viewDetail']='original'
    c['cropHashStillMatches']=sha(c['file'])==c['sha256']

focus=[]
for n,x in [(1,380),(1,965),(2,550),(3,270),(3,975),(4,275),(4,550)]:
    x0=max(0,min(x-96,1024-192));p=OUT/f'focus-segment{n}-x{x}.png';source=OUT/f'r11_c05--r12_c05-segment{n}.png'
    with Image.open(p) as im,Image.open(source) as s:
        assert im.size==(192,192) and ImageChops.difference(im,s.crop((x0,64,x0+192,256))).getbbox() is None
    focus.append({'file':str(p),'sha256':sha(p),'pixels':[192,192],'sourceCrop':str(source),'sourceCropBox':[x0,64,x0+192,256],
                  'worldBox':[16384+(n-1)*1024+x0,44960,16384+(n-1)*1024+x0+192,45152],
                  'actualViewedAtNativePixels':True,'viewTool':'view_image','viewDetail':'original','resampling':False,
                  'operation':'further exact crop from a reviewed native boundary strip; no pixel editing'})

changed=[];end=[]
for inp in m['inputs']:
    actual=sha(inp['file']);assembly=sha(inp['assembly']);same=actual==inp['sha256'] and assembly==inp['assemblySha256']
    if not same:changed.append(inp['tile'])
    end.append({'tile':inp['tile'],'file':inp['file'],'beforeSha256':inp['sha256'],'afterSha256':actual,
                'assemblyBeforeSha256':inp['assemblySha256'],'assemblyAfterSha256':assembly,'unchanged':same})
for edge in m['reusedEdges']:
    edge['reportHashStillMatches']=sha(edge['report'])==edge['reportSha256']
    if not edge['reportHashStillMatches']:changed.append(edge['report'])
    for n in edge.get('nativeEvidence',[]):
        n['sourceEvidenceHashStillMatches']=sha(n['file'])==n['sha256']
        if not n['sourceEvidenceHashStillMatches']:changed.append(n['file'])
catalog=read(m['currentCatalogSnapshot']['file'])['tiles']
current_match=all(catalog[x['tile']]['candidate']['file']==x['file'] and catalog[x['tile']]['candidate']['sha256']==x['sha256'] for x in m['inputs'])
if not current_match:changed.append('current catalog adopted entries changed')

report={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/southwest_census',
        'status':'four_tile_chain_failed_existing_and_new_geometry_material_evidence','inputs':m['inputs'],
        'reviewScope':{'newNativeFullBoundarySegmentsActuallyViewed':4,'newNativeIntersectionCropsActuallyViewed':3,
                       'additionalNativeFocusCropsActuallyViewed':7,'newReviewedEdge':['r11_c05','r12_c05'],
                       'nativeScale':True,'viewTool':'view_image','viewDetail':'original','candidateOverviewUsed':False},
        'newReviewedEdgeStatus':'fail_geometry_and_material','newReviewCrops':m['newReviewCrops'],'additionalFocusCrops':focus,
        'reusedEdges':m['reusedEdges'],'sourceEndVerification':end,'currentCatalogFourEntriesStillMatch':current_match,
        'stale':bool(changed),'changedSources':changed,'allSourceHashesUnchanged':not changed,
        'completeMapAccepted':False,'wholeTilesInternalPassed':False,'formalAccepted':False,
        'deliverableMergedImageCreated':False,'previewCreated':False,'newImageGenerationCalls':0,'sourceArtworkModified':False,
        'limits':'Only the bounded r11/r12 edge and three local intersections were newly visually inspected. Existing r10/r11 pass and r12/r13 failure are reused with current source equivalence. Whole tiles, other external sides, and entire map acceptance remain open.'}
m.update({'newReviewCrops':m['newReviewCrops'],'stale':report['stale'],'sourceEndVerification':end,'allSourceHashesUnchanged':not changed,
          'reviewReport':str(OUT/'visual-review.json'),'newReviewedEdgeStatus':'fail_geometry_and_material','completedAtUtc':report['reviewedAtUtc']})
write('manifest.json',m);write('visual-review.json',report)
lines=['# Southwest 第 5 列南北接缝 v001','','范围：r10_c05 → r11_c05 → r12_c05 → r13_c05，4 张均为当前采用的 4096×4096 候选。输入、来源规范、worldbox、SHA-256 与每处检查见 manifest.json / visual-review.json。',
       '','- r10→11：复用 v5 已通过的接缝接续证据，当前两图路径/hash 一致；整体石材仍待验收。',
       '- r11→12：本次实际查看 4 张 1024×320 原像素边界裁片和 3 张 512×512 交点，另查看 7 张 192×192 原像素定位裁片。接缝失败。',
       '- r12→13：复用既有结构/材质失败；原有 4 张边界证据逐像素与当前候选重组的原像素裁片完全相同。',
       '','新发现均位于 world y=45056：',
       '- 第 1 段：沟槽在上侧 tile x≈410、944，下侧分别落在 x≈359、986，相位错位约 51 与 42 像素。',
       '- 第 2 段：下侧 x≈1233、1572 的沟槽在切线处直接起头，上方没有衔接。',
       '- 第 3 段：上侧 x≈2318 沟槽到切线止步；下侧 x≈3020 新起沟槽。',
       '- 第 4 段：下侧 x≈3348、3623 两处沟槽在切线处截断起头。',
       '- x=1024、3072 交点保留相位错接／沟槽断头；x=2048 中心没有可连续追踪的沟槽，不能独立认证几何，石材纹理仍失败。',
       '- 各段石面仍有密集细网／鳞格和大片撕裂状冷暖洗色，未通过自然安静灰石材目标。',
       '',f'最终输入复核：4 图与装配 manifest hash 未变；当前 catalog 的 4 个采用条目仍一致。stale={report["stale"]}。',
       '','本链有现存和新增失败，未生成可交付合图、预览或补图；只交原像素 QA 裁片及报告。未生图、未写原生产目录、未操作 Git。']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'outputDirectory':str(OUT),'newBoundaryStatus':report['newReviewedEdgeStatus'],'nativeCropsActuallyViewed':14,
                  'allSourceHashesUnchanged':not changed,'stale':report['stale'],'deliverableMergedImageCreated':False}))
