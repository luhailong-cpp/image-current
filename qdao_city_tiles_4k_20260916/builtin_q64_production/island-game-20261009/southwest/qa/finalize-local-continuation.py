from pathlib import Path
import sys,shutil,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import ROOT,load,dump,hashfile,now,metadata

folder=ROOT/'output/contiguous-r09-r10-c03-c04-v01'; manifest=load(folder/'manifest.json');tiles=[t['tile'] for t in manifest['tiles']]
remaining=[f'r{r:02}_c{c:02}' for r in range(8,15) for c in range(1,8) if f'r{r:02}_c{c:02}' not in tiles]
assert len(remaining)==45
outer=[]
for c in [3,4]:
 outer.extend([{'tile':f'r09_c{c:02}','side':'north','neighbor':f'r08_c{c:02}','globalLine':[(c-1)*4096,32768,c*4096,32768]}, {'tile':f'r10_c{c:02}','side':'south','neighbor':f'r11_c{c:02}','globalLine':[(c-1)*4096,40960,c*4096,40960]}])
for r in [9,10]:
 outer.extend([{'tile':f'r{r:02}_c03','side':'west','neighbor':f'r{r:02}_c02','globalLine':[8192,(r-1)*4096,8192,r*4096]}, {'tile':f'r{r:02}_c04','side':'east','neighbor':f'r{r:02}_c05','globalLine':[16384,(r-1)*4096,16384,r*4096]}])
for e in outer:e['status']='pending neighboring native tile generation and paired seam review'
index=load(ROOT/'current-native-map.json')
index.update(status='four_connected_native_candidates_passed_group_QA_outer_neighbors_pending',formalAccepted=False,rowsAvailable=4)
index['candidateArtifacts']={t['tile']:{'path':t['path'],'record':t['derivation'],'sourceIdMask':t['sourceIdMask']['path'],'sourceReport':t['sourceReport']['path'],'mode':'native same-coordinate pixel selection; no interpolation, feathering, warping or recoloring','baseArrayDoesNotFullyDescribeFinalPixels':True,'nativeSourceCount':t['uniqueNativeSourceCount'],'internalPassed':True,'connectedGroupEdgesPassed':True,'allOuterTileEdgesPassed':False,'formalAccepted':False} for t in manifest['tiles']}
index['currentGroup']={'manifest':str(folder/'manifest.json'),'combined':manifest['combined']['path'],'preview':manifest['preview']['path'],'spec':str(ROOT/'qa/connected-stepfoot-v01-spec.json'),'outerEdgesPending':outer,'formalAcceptedCount':0};dump(ROOT/'current-native-map.json',index)
progress=load(ROOT/'progress.json')
progress.update(status='local_work_complete_waiting_image_network_permission',updatedAtUtc=now(),complete4kCount=4,candidate4kCount=4,fullyCovered4kCount=4,internalPassed4kCount=4,connectedGroupPassed4kCount=4,externalPassed4kCount=0,formalAcceptedCount=0,outerEdgesPendingCount=8,remainingTiles=45,currentTile='/'.join(tiles),currentPatch='four-tile group exported; 64 native core positions; all group shared seams checked',currentCandidate=str(folder/'manifest.json'),currentPreview=manifest['preview']['path'],currentCombined=manifest['combined']['path'],sharedEdgeReview=str(ROOT/'qa/connected-stepfoot-group-v01-root-review.json'),pendingRepairs=[],pendingOuterEdges=outer,generationHoldActive=False,networkGenerationBlocked=True,nextStep='Wait for image-generation network permission restoration; then generate remaining45 southwest tiles beginning with a neighboring border-constrained group. Do not regenerate the completed4 group. No runtime work.',blocking={'kind':'reported_network_permission_revoked','evidence':'Coordinating chat message received2026-10-11: Fatal error: application network permission was revoked. Coordinator requested local-only continuation.','independentlyRetestedHere':False,'workaroundAttempted':False,'restoreConfirmationReceived':False})
dump(ROOT/'progress.json',progress)
queue=load(ROOT/'qa/current-2x2-repair-queue.json');queue.update(updatedAtUtc=now(),status='completed and exported as connected group; original suggested parameters are historical, final spec/reports take precedence',finalSpec=str(ROOT/'qa/connected-stepfoot-v01-spec.json'),finalManifest=str(folder/'manifest.json'),outstandingSource=None,otherWork='Current group complete; next45 coordinates require native generation; outer group8 edges pending.');dump(ROOT/'qa/current-2x2-repair-queue.json',queue)
old=ROOT/'qa/README-before-connected-group-20261011.txt'
if not old.exists():shutil.copy2(ROOT/'README.md',old)
readme='''# 八仙岛西南区：当前可读取交付

本轮完成 r09_c03、r09_c04、r10_c03、r10_c04 四张 4096×4096 原生拼接候选，以及一张 8192×8192 连续拼图。四块内部检查、组内全部横纵共享边和四块交点检查通过。逐像素来源核验共 67,108,864 像素，0 mismatch；没有放大、羽化、变形或调色。局部自然笔触/材质调子差见 QA 记录。

交付入口为 [manifest.json](output/contiguous-r09-r10-c03-c04-v01/manifest.json)，[连续8192图](output/contiguous-r09-r10-c03-c04-v01/r09-r10-c03-c04-native-8192.png)，[2048预览](output/contiguous-r09-r10-c03-c04-v01/preview-2048.png)。同目录包含四张4K图、每图source-ID掩码、来源报告和派生记录。

准确数量：4张候选、4张内部通过、4张组内共享边通过；8条组外图块边仍需邻块生成后检查，完整外缘通过0张、正式验收0张。西南分区总49张，剩45张未生成；本组不代表全区或整图完成。

本轮将粽叶/绳结、墙脚、台阶、庭院铺地、石栏、金肋和三段金色屋顶修补合入。完整组检查额外发现台阶下方断砖缝，已通过扩大已有原生修补选择范围修好。最终组合规格在 [connected-stepfoot-v01-spec.json](qa/connected-stepfoot-v01-spec.json)，最终根检查在 [root-review](qa/connected-stepfoot-group-v01-root-review.json)。旧候选和旧误通过记录保留，仅当前manifest为交付入口。

主控于2026-10-11报告生图网络权限撤销，要求本地续做并等待恢复。本窗口未反复重试网络，也未换入口/账号或付费API。所有当前可执行的拼接、检查、导出已完成。剩余坐标、8条外缘和阻塞见 [local-continuation-20261011.json](local-continuation-20261011.json)。恢复后从当前导出边界约束继续，勿重复生成本组。

每次内置生图的精确prompt、参考角色/hash、坐标、实测1254²尺寸、回执和源hash在 prompts、guides、receipts、native 中。最终每个像素按来源报告和source-ID掩码可追溯；16格基础数组不能单独重现修补后的成品。实际model/quality工具未披露，记录为null。

仅本区可写。日景Q版道家春节风格和既有地图布局继续有效。仅允许内置image_gen；实际游戏、Unity、容量运行测试不在本次范围，旧AGENTS要求已撤销。历史README保存在qa/README-before-connected-group-20261011.txt，仅供历史追溯。
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
record={'recordedAtUtc':now(),'request':'Continue available local work while coordinator reports image network permission revoked','status':'all currently executable local integration, native QA and exports completed; further coverage requires image generation','writeScope':str(ROOT),'currentCandidateCount':4,'internalPassedCount':4,'connectedGroupPassedCount':4,'outerEdgesPendingCount':8,'outerTileAcceptancePendingCount':4,'externalPassedCount':0,'formalAcceptedCount':0,'generatedNativeCount':progress['generatedNativeCount'],'selectedCoreCount':64,'tilePixelSize':[4096,4096],'combinedPixelSize':[8192,8192],'outputs':[{'tile':t['tile'],'path':t['path'],'sha256':t['sha256'],'uniqueNativeSourceCount':t['uniqueNativeSourceCount'],'derivation':t['derivation']} for t in manifest['tiles']],'manifest':{'path':str(folder/'manifest.json'),'sha256':hashfile(folder/'manifest.json')},'combined':manifest['combined'],'preview':manifest['preview'],'outerEdgesPending':outer,'stillNeedsGenerationCoordinates':remaining,'remainingTileCount':45,'zoneTileCount':49,'remainingCorePositions':45*16,'nextNeighborCoordinates':[e['neighbor'] for e in outer],'newIntegrations':['native package leaf/rope and wallfoot corrections','both stair sections and two courtyard paving sections','r10c03 scroll, rails, roof junction and left transition','r10c04 wall-top, post foot, wall base, roof curve and low rib','three shared gold finial/pedestal sections with original background protection','final stair-foot disconnected paving-line correction using existing native source'],'localVerification':{'totalFinalPixels':4*4096*4096,'mismatchedPixels':0,'internalAndConnectedSeamsPassed':True,'combinedTileCropsExact':True,'lowerBuiltinRecordAudit':str(ROOT/'qa/lower-native-records-audit.json'),'runtimeTestsRun':False},'blocking':progress['blocking'],'fullZoneComplete':False,'fullMapComplete':False,'nextStep':progress['nextStep']}
dump(ROOT/'local-continuation-20261011.json',record)
shutil.copy2(ROOT/'README.md',folder/'README.md');shutil.copy2(ROOT/'local-continuation-20261011.json',folder/'local-continuation-20261011.json')
archive=ROOT/'output/sw-r09-r10-c03-c04-4k-delivery-v01.zip'
assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for p in sorted(folder.iterdir()):
  if p.is_file() and not p.name.startswith('r09-r10-c03-c04-native-8192'):z.write(p,p.name)
 for n in ['connected-stepfoot-group-v01-root-review.json','connected-stepfoot-group-v01-vertical-review.json','connected-group-v01-horizontal-review.json','connected-final-merge-independent-review.json']:
  p=ROOT/'qa'/n
  if p.exists():z.write(p,'QA/'+n)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
dump(str(archive)+'.manifest.json',{'createdAtUtc':now(),'path':str(archive),'sha256':hashfile(archive),'bytes':archive.stat().st_size,'scope':'four4K PNGs, source-ID masks/reports, per-tile derivations, preview and group QA; 8192 combined separately available','combinedPath':manifest['combined']['path'],'originalNativeSourcesRemainInWorkspace':str(ROOT/'native'),'zipCrcAllPass':True})
record['fourKDeliveryArchive']={'path':str(archive),'sha256':hashfile(archive),'bytes':archive.stat().st_size};dump(ROOT/'local-continuation-20261011.json',record)
print({'status':progress['status'],'candidateCount':4,'remaining':45,'archive':str(archive),'bytes':archive.stat().st_size})
