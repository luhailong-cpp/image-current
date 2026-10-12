"""Export byte-identical current candidates and trace metadata; no image generation."""
from pathlib import Path
import sys,shutil,zipfile,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *

folder=ROOT/'output/current-eight-candidates-20261012-v01'
archive=ROOT/'output/sw-current-eight-4k-candidates-20261012-v01.zip'
assert not folder.exists() and not archive.exists()
folder.mkdir()
idx=load(ROOT/'current-native-map.json');arts=idx['candidateArtifacts'];assert len(arts)==8
items=[]
for tile,a in sorted(arts.items()):
 source=Path(a['path']);target=folder/f'{tile}-candidate-4096.png';shutil.copy2(source,target)
 assert hashfile(target)==hashfile(source)
 mask=a['sourceIdMask'];mask=Path(mask['path'] if isinstance(mask,dict) else mask)
 destmask=folder/f'{tile}-source-id-mask.png';shutil.copy2(mask,destmask)
 assert hashfile(mask)==hashfile(destmask)
 record=Path(a.get('sourceReport') or a.get('record'));destrecord=folder/f'{tile}-source-report.json'
 shutil.copy2(record,destrecord);assert hashfile(record)==hashfile(destrecord)
 items.append({'tile':tile,'file':target.name,'sha256':hashfile(target),'dimensions':[4096,4096],'sourceAdoptedPath':str(source),'sourceIdMask':{'file':destmask.name,'sha256':hashfile(destmask)},'sourceReport':{'file':destrecord.name,'sha256':hashfile(destrecord)},'internalPassed':bool(a.get('internalPassed') or a.get('internalTileSeamsPassed')),'allOuterTileEdgesPassed':False,'formalAccepted':False,'visualStatus':a.get('internalStatus') or a.get('status') or 'internal reviewed; unfinished outer perimeter'})
for name in ['production-resume-20261012.json','progress.json','current-native-map.json']:
 shutil.copy2(ROOT/name,folder/name)
for file in ['qa/north-r08c04-resume-v01-root-review.json','qa/expansion-west-root-r11c03-review.json','qa/east-r09c05-native-review.json','qa/c04-hardseam-west-r09c02-v01-review.json']:
 shutil.copy2(ROOT/file,folder/Path(file).name)
shutil.copy2(ROOT/'qa/central-partial-r11c04-rows12-resume-v01-native.png',folder/'r11_c04-upper-half-native-partial-4096x2048.png')
shutil.copy2(ROOT/'qa/central-partial-r11c04-rows12-resume-v01-report.json',folder/'r11_c04-upper-half-source-report.json')
manifest={'createdAtUtc':now(),'scope':'Current eight complete southwest 4K native-source candidates; entire49-tile zone is unfinished','tiles':items,'completeCandidateCount':8,'internalPassedCount':6,'formalAcceptedCount':0,'remainingTilesWithoutCompleteCandidate':41,'selectedCoreCount':158,'totalCoreCount':784,'missingCoreCount':626,'nativeAssembly':'All artwork pixels copied from native images at same global coordinates; no resampling, feathering, color changes or displacement','partialIncluded':'r11_c04 upper half4096x2048,8cores; unresolved gold-eave step and lower8cores remain','notNewGeneratedArtwork':'This export uses previously saved imagegen outputs; current network permission denies resumed agent runtime','currentAdoptionIndex':'current-native-map.json','sourcePixelsNotIncludedInThisReviewZip':'All original native sources, prompts, guides and receipts remain preserved in southwest/native,prompts,guides,receipts; migration upload owner handles them separately','repositoryGitModified':False}
dump(folder/'manifest.json',manifest)
(folder/'README.txt').write_text('八仙岛西南区当前8块完整4K候选，整区49块尚未完成。\n6块通过内部检查，外边与交点仍按各自报告继续，正式验收0。\n所有PNG与当前采用文件逐字节一致。另附r11_c04上半部4096x2048，非完整图块。\n原始native/提示词/引用/回执保留在工作区，由上传窗口补传。\n',encoding='utf-8')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
 for p in sorted(folder.iterdir()):z.write(p,p.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
out={'folder':str(folder),'archive':str(archive),'archiveBytes':archive.stat().st_size,'archiveSha256':hashfile(archive),'crcVerified':True,'tileCount':8,'internalPassedCount':6,'formalAcceptedCount':0,'allCopiedArtworkBytesEqualAdoptedSources':True}
dump(ROOT/'qa/current-eight-candidates-export-20261012-v01.json',out)
print(json.dumps(out,ensure_ascii=False))
