"""Package four already reviewed candidate files; no rendering or generation."""
import sys,json
from pathlib import Path
from PIL import Image
import pipeline as p
spec=p.read(sys.argv[1]);out=p.owned_path(p.ROOT/spec['directory']);out.mkdir(exist_ok=True)
assert {i['tile'] for i in spec['tiles']}==set(p.OWNED) and len(spec['tiles'])==4
tiles=[];preview=Image.new('RGB',(2048,2048));positions={'r03_c04':(0,0),'r03_c05':(1024,0),'r04_c04':(0,1024),'r04_c05':(1024,1024)}
for item in spec['tiles']:
 tile=item['tile'];source=Path(item['candidate']);assembly=p.read(item['assembly'])
 assert p.sha(source)==assembly['candidate']['sha256']
 with Image.open(source) as opened:
  assert opened.size==(4096,4096) and opened.format=='PNG' and opened.convert('RGBA').getchannel('A').getextrema()==(255,255)
  im=opened.convert('RGB');preview.paste(im.resize((1024,1024),Image.Resampling.LANCZOS),positions[tile])
 dest=out/(tile+'.png');p.put_bytes(dest,source.read_bytes());assert p.sha(dest)==p.sha(source)
 selected=[{'patch':patch,**p.native_info(p.selected(p.ROOT/tile,patch))} for patch in p.patch_ids()]
 report=Path(item['review']);assert report.exists()
 tileinfo={**item,'candidate':str(dest),'sourceCandidate':str(source),'sha256':p.sha(dest),'pixels':[4096,4096],'worldBox':p.tile_box(tile),'coreCount':16,'corePixels':1024,'haloPixels':115,'selectedPatchPixels':[1254,1254],'selectedNativeOrDerivedPatches':selected,'reviewSHA256':p.sha(report),'formalAccepted':False,'isNativeSingleGeneration4096':False,'finalArtUpscaled':False}
 tileinfo['supplementaryReviews']=[{'file':str(f),'sha256':p.sha(f)} for f in item.get('supplementaryReviews',[])]
 tiles.append(tileinfo)
previewinfo=p.save_png(out/'overview-preview-2048.png',preview)
parameters=[];seen=set()
for f in list(p.ROOT.rglob('*parameters*.json'))+list(p.ROOT.rglob('*.generation.json')):
 if out in f.parents:continue
 d=p.read(f);args=d if isinstance(d,dict) and isinstance(d.get('prompt'),str) else d.get('submittedParameters') if isinstance(d,dict) else None
 if not isinstance(args,dict) or not isinstance(args.get('prompt'),str):continue
 key=(p.sha(f),str(f))
 if key in seen:continue
 seen.add(key);parameters.append({'recordFile':str(f),'recordSHA256':key[0],'submittedParameters':args,'actualModel':None,'actualQuality':None,'route':'builtin image_gen.imagegen; execution model and quality not independently disclosed'})
p.put_json(out/'prompt-records-index.json',{'records':parameters,'recordCount':len(parameters),'countMeaning':'Parameter record count includes provenance duplicates and rejected attempts; it is not a count of selected patches or billable calls.'})
manifest={'schemaVersion':1,'createdAtUTC':p.now(),'scope':'Assigned four-tile yamen-north acceleration window only; neither full zone nor full map completion','status':'four_candidates_delivered_with_recorded_QA_findings','ownedWorldBox':[12288,8192,20480,16384],'candidateCount':4,'coveredCoreCoordinates':64,'missingAssignedCores':0,'formalAcceptedCount':0,'builtinOnly':True,'paidApiUsed':False,'gameUnityRuntimeCapacityTestsPerformed':False,'actualModel':None,'actualQuality':None,'nativeDimensionsDisclosure':'Original generated patches and repair crops are 1254x1254. Final 4096x4096 files are same-coordinate native-pixel composites, with explicitly recorded alpha derivations where used. They are not native single-generation 4K and are not upscaled final art.','tiles':tiles,'overview':{**previewinfo,'isDownscaledPreviewOnly':True},'promptRecordsIndex':str(out/'prompt-records-index.json'),'outerNeighborInventory':str(p.ROOT/'outer-neighbor-inventory.json'),'crossBoundarySummary':spec['crossBoundarySummary'],'remainingWork':spec['remainingWork']}
p.put_json(out/'delivery-manifest.json',manifest)
notes=['官府北部加速区｜四块候选交付','范围：r03_c04、r03_c05、r04_c04、r04_c05；世界范围 [12288,8192,20480,16384]。','数量：4张独立4096×4096 PNG；64/64核心区域已有素材；正式验收0/4。','这些4K图为原尺寸素材合成；原始生成与修补图为1254×1254，未将成图放大。局部alpha合成及来源均有记录。','全部使用内置生图；工具未披露可独立验证的实际模型/质量值，记录为null。','未执行游戏、Unity或容量运行测试。','这只表示本加速窗口的候选产出，不能表示整区或整图完成。','', '候选文件：']
notes += [t['tile']+'：'+t['candidate']+'\nSHA256：'+t['sha256']+'\n检查报告：'+t['review'] for t in tiles]
notes += ['', '尚未通过或待验收：']+[str(v) for v in spec['remainingWork']]
notes += ['', '边界检查：']+[str(v) for v in spec['crossBoundarySummary']]
notes += ['', '参数、来源、坐标与完整状态：'+str(out/'delivery-manifest.json'),'提示词与实际提交参数索引：'+str(out/'prompt-records-index.json'),'overview-preview-2048.png仅为缩小预览，不是交付原图。']
p.put_bytes(out/'delivery-notes.txt',('\n'.join(notes)+'\n').encode('utf-8'))
progress=p.read(p.ROOT/'progress.json');progress.update({'status':manifest['status'],'deliveredCandidateCount':4,'coveredCoreCoordinates':64,'missingNativeCount':0,'formalAcceptedCount':0,'deliveryManifest':str(out/'delivery-manifest.json'),'nextCoordinate':None,'nextStep':spec['remainingWork'],'scopeCompletion':'four assigned candidates delivered; formal seam acceptance and complete map remain open'})
p.replace_json(p.ROOT/'progress.json',progress)
p.put_json(out/'progress.json',{'status':manifest['status'],'candidateCount':4,'coveredCoreCoordinates':64,'formalAcceptedCount':0,'tiles':[{'tile':t['tile'],'file':t['candidate'],'sha256':t['sha256'],'pixels':t['pixels'],'review':t['review']} for t in tiles],'remainingWork':spec['remainingWork']})
print(json.dumps({'manifest':str(out/'delivery-manifest.json'),'preview':previewinfo['file'],'candidates':[{'tile':t['tile'],'file':t['candidate'],'sha256':t['sha256']} for t in tiles],'promptRecordCount':len(parameters)}))
