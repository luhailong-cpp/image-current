from pathlib import Path
import json,hashlib,datetime,re
from PIL import Image
OUT=Path(__file__).resolve().parent
I=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
M=json.loads((OUT/'assembly-review-manifest.json').read_text(encoding='utf-8'))
T={t['tileId']:t for t in I['tiles']}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
pair_notes={
 ('r08_c03','r08_c04'):('geometry_pass','Four current native strips viewed; paving, low stone beam and blue/gold roof contours continuous; mild material variation retained.'),
 ('r08_c03','r09_c03'):('geometry_pass','Four current native strips viewed; bamboo outlines, gold trim and roof courses continuous; painterly value variation remains.'),
 ('r08_c04','r09_c04'):('needs_paired_material_review_or_repair','Four current native strips viewed; no newly identified large geometry gap. Earlier hash-bound south-edge material/highlight exceptions remain open; no prior rejection overridden.'),
 ('r09_c05','r10_c05'):('needs_paired_material_repair','Four current native strips viewed; wall cap retains a large soft patch around tile-local x2900..3400 near north boundary; adjacent paving/wall is sharp. Major geometry generally continuous.'),
 ('r09_c04','r09_c05'):('needs_paired_source_repair','Four current native strips viewed; preserved 115px border strip retains abrupt leaf/material transition and a bright rectangular gold-frame patch at the guide boundary.'),
 ('r10_c04','r10_c05'):('needs_paired_geometry_repair','Four current native strips viewed; western low wall cap and inset bevel retain height/line mismatch in c05 local y1000..1650.'),
}
for x in M['seams']:
 status,note=pair_notes[tuple(x['pair'])];x.update(status=status,visualNote=note,actuallyViewedAtNativeScale=True,reviewedAtUtc=now())
for x in M['junctions']:
 status='geometry_pass';note='Exact current four-tile corner viewed at 1:1; outlines continue, no additional junction break identified.'
 if x['tiles'][0]=='r09_c04':status='needs_paired_source_repair';note='Guide boundary at c05 local x115 remains visible through gold/wood frame; confirms open east shared-edge issue.'
 x.update(status=status,visualNote=note,actuallyViewedAtNativeScale=True,reviewedAtUtc=now())
dump('assembly-review-manifest.json',M)
oldpairs={
 ('r09_c02','r09_c03'):'c04-hardseam-west-r09c02-v01-review.json',
 ('r09_c02','r10_c02'):'c04-hardseam-west-r10c02-v01-review.json',
 ('r09_c03','r09_c04'):'connected-stepfoot-group-v01-root-review.json',
 ('r09_c03','r10_c03'):'connected-stepfoot-group-v01-root-review.json',
 ('r09_c04','r10_c04'):'connected-stepfoot-group-v01-root-review.json; current r10c04 repair bbox affects only bottom115px and does not touch north edge',
 ('r10_c02','r10_c03'):'c04-hardseam-west-r10c02-v01-review.json',
 ('r10_c03','r10_c04'):'connected-stepfoot-group-v01-root-review.json; current r10c04 lower roof repair bbox does not reach west edge',
 ('r10_c03','r11_c03'):'expansion-west-root-r11c03-review.json',
 ('r10_c04','r11_c04'):'central-r11c04-resume-final-west-review.json; central-r11c04-pond-right-crisp-v02-west-supplement.json; current source-report inheritance and repair bounds verified',
 ('r11_c03','r11_c04'):'central-r11c04-resume-final-west-review.json; later right pond repair does not reach west edge',
}
for e in I['edges']:
 pair=(e['tileId'],e['neighbor'])
 if pair in pair_notes:
  e.update(status=pair_notes[pair][0],evidence='assembly-review-manifest.json',visualNote=pair_notes[pair][1])
 elif pair in oldpairs:e.update(status='geometry_pass_reused',evidence=oldpairs[pair],reuseCondition='Current candidate/source-ID mask hashes and unchanged-region repair bounds checked; no complete outer-perimeter acceptance.')
 if e['status']=='neighbor_native_coverage_missing':e['neighborCoreCount']=T.get(e['neighbor'],{}).get('coreCount',0)

norm=[]
for issue in I['recordedOpenIssues']:
 d=issue.copy();t=T[d['tileId']];bx=d.get('tileLocalBox',d.get('tileLocalApproxBox',d.get('localBox')))
 if bx:d['normalizedGlobalApproxBox']=[bx[0]+t['origin'][0],bx[1]+t['origin'][1],bx[2]+t['origin'][0],bx[3]+t['origin'][1]]
 elif d.get('globalApproxBox'):d['normalizedGlobalApproxBox']=d['globalApproxBox']
 d['status']='open_recorded_issue; AI repair deferred; no generation in this audit'
 norm.append(d)
extra=[
 {'id':'east-r09-c04c05-guide-border','tiles':['r09_c04','r09_c05'],'globalApproxBoxes':[[16384,33587,16624,33767],[16384,34628,16624,34808],[16384,35863,16624,36043]],'issue':'Leaf/material/frame transition near c05 local x115 and y909/1950/3185. Native view confirms retained border defect.'},
 {'id':'east-r10-c04c05-wallcap','tiles':['r10_c04','r10_c05'],'globalApproxBoxes':[[16256,37864,16624,38514]],'issue':'Low wall cap and inset-panel bevel height mismatch; paired geometry repair required.'},
 {'id':'east-r09r10-c05-softwall','tiles':['r09_c05','r10_c05'],'globalApproxBoxes':[[19284,36736,19784,37064]],'issue':'Soft wall-cap/corner patch across north boundary compared with sharp adjacent native material.'},
 {'id':'north-r08r09-c04-material','tiles':['r08_c04','r09_c04'],'globalApproxBoxes':[[12288,32512,16384,33024]],'issue':'Retain prior shared-edge material/highlight exception; native pair viewed, no new full shared-edge pass granted.'},
]
I['normalizedRepairQueue']=norm+extra
I['currentVisualReview']=M
I['summary'].update(nativePixelCountIndependentlyVerified=sum(t.get('nativePixelValidation',{}).get('verifiedSelectedPixelCount',0) for t in I['tiles']),mismatchedNativePixels=sum(t.get('nativePixelValidation',{}).get('mismatchedPixels',0) for t in I['tiles']),nativePairsGeometryPassOrReused=sum(e['status'].startswith('geometry_pass') for e in I['edges']),nativePairsPendingMaterialOrGeometryRepair=sum(e['status'].startswith('needs_') for e in I['edges']),newNativePairMontagesViewed=len(M['seams']),newNativeJunctionsViewed=len(M['junctions']),nativeLocalAssemblies=len(M['assemblies']))
I['sourceReferenceAudit']['interpretation']='209 direct core records use one layout hash and one independent detail hash. Approved mail style appears as 190 JPEG-reference hashes plus 19 original PNG-reference hashes; this is a file/encoding variant, not proof of alternate style. Ten selected cores are mechanical resolved crops with derivedFrom provenance rather than a new model generation. All 220 selected core records report actualModel null.'
I['metadataConflicts'].append({'field':'progress.currentZoneMetrics.selectedNativeCoreCount','recorded':218,'independentlyCounted':220,'reason':'r12_c03 current selected matrix contains 15 cores; aggregate metric lagged'})
changes=[];checks=[]
for f in I['snapshotInputFiles']:
 p=Path(f['path']);current=sha(p) if p.is_file() else None;same=current==f.get('sha256');checks.append({'path':f['path'],'initialSha256':f.get('sha256'),'finalSha256':current,'unchanged':same})
 if not same:changes.append(checks[-1])
I['sourceChangeAudit']={'checkedAtUtc':now(),'checkedFileCount':len(checks),'changedFiles':changes,'allSnapshotInputsUnchanged':not changes,'snapshotStale':bool(changes),'rule':'If a candidate or its sources change, affected assemblies/crops are stale; source-map metadata changes require a new coverage snapshot.'}
dump('final-rehash.json',{'checkedAtUtc':now(),'files':checks})
I['completedAtUtc']=now();dump('inventory.json',I)
s=I['summary'];miss=[t['tileId'] for t in I['tiles'] if not t['fullCoverage']]
rows=['# 八仙岛西南区独立审计 v01','',f"审计完成时间（UTC）：{I['completedAtUtc']}。仅检查已有素材，无生图、AI 修图、生产目录写入、Git 操作或删除。",'',f"当前快照：49 个目标坐标；12 张完整 4096² 原生来源候选，8 张有可靠内部通过记录，4 张仍待修；已选 220/784 个 1024² 核心，缺 564 个。正式验收 0 张。",'',f"逐像素独立验证 12 张、{s['nativePixelCountIndependentlyVerified']:,} 像素，0 mismatch；原生来源图片与记录哈希全部匹配。派生 resolved 核心明确保留机械裁切来源，未将其记成新生图。",'',"当前采用路径以 current-native-map.json 的 candidateArtifacts 为准，与 progress.currentAdopted4kFiles 一致。progress.currentCandidateByTile 的 r10_c04 指向旧版本，早期四块包和 README 不再代表当前采用组合；汇总指标 218 也落后于实际 220。",'',"- 部分覆盖：r08_c02=12/16（仅第 2–4 子行）；r12_c03=15/16（只缺 s04_04）；r09_c06=1/16（仅 s01_01）。", "- 北边：r08_c03、r08_c04 全覆盖但内部待修；r08_c02 首子行缺失；其余 r08 列为空。全区 c07 没有已采用核心。",'',"已保存最新 r10–r11/c03–c04 四块 8192² 原生硬拼接，逐块复制验证 0 mismatch。预览明确标为缩放预览。此局部具有内部/共享边证据，外圈仍未验收，不能称为整区完成。",'',"接缝结论：",'']
for e in I['edges']:
 if e['neighborFullCandidateAvailable']:rows.append(f"- {e['tileId']} → {e['neighbor']}：{e['status']}。{e.get('visualNote',e.get('evidence',''))}")
rows+=['',"本轮实际查看 6 张 100% 接缝蒙版拼接（24 段）和 4 个 100% 四块交叉点。新检查的 r08_c03/r08_c04、r08_c03/r09_c03 轮廓连续；西侧粽叶交点、当前中央屋顶交点没有新增错接。东侧交点确认保留边带造成的金木框直线切换。",'',"仍需修补：r08_c03 的砖缝/竹轮廓/地面解释；r08_c04 的模糊铺地、石梁切角、柱轮廓及地缝；r09_c02 的竹环/球面长折线与材质块；r10_c05 内嵌面板双线。外部 r09 c04/c05、r10 c04/c05、r09/r10 c05 及 r08/r09 c04 的具体全图坐标保存在 normalizedRepairQueue。后续生产遵循最新根 AGENTS：现有免费 2.5 优先，不可用可用内置 2.0；本审计零生图。",'',"参考记录：209 个直接核心记录共享同一布局及细节参考哈希，邮件风格有原 PNG 与 JPEG 两种记录；未越权读取区外参考图。实际模型全部未确认，配置中的 2.5 不作实际型号证明。",'',f"最终复 hash：{len(checks)} 个快照输入，变更 {len(changes)} 个；{'输入稳定' if not changes else '快照已标过期，见 final-rehash.json'}。",'',"未完整覆盖坐标：",'',', '.join(miss),'',"机器可读交付：inventory.json、assembly-review-manifest.json、final-rehash.json。文件均位于本独立审计目录。"]
(OUT/'review.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print(json.dumps({'summary':I['summary'],'sourceChanged':len(changes),'inventory':(OUT/'inventory.json').as_posix(),'review':(OUT/'review.md').as_posix()},ensure_ascii=False))
