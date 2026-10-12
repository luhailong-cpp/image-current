from pathlib import Path
import sys,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_postfoot_join_v01'
src=Path(r'C:/Users/luyua/.codex/generated_images/01a1257c-207e-7641-9787-7abf0e2b872b/exec-eede9c02-9265-49e0-acfe-ce8e9b40f48f.png')
dst=ROOT/'native'/(stem+'.png');assert not dst.exists();shutil.copy2(src,dst)
with Image.open(dst) as im:size=list(im.size);fmt=im.format;mode=im.mode
assert size==[1254,1254] and mode=='RGB'
req=p.load(ROOT/'prompts'/(stem+'.request.json'))
rec={'file':dst.as_posix(),'sha256':p.hashfile(dst),'generatedAt':p.now(),'width':1254,'height':1254,'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':p.CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool exposes neither model/quality selectors nor actual model/quality identity.','prompt':(ROOT/'prompts'/(stem+'.prompt.txt')).as_posix(),'references':req['references'],'sourceToolPath':src.as_posix(),'evidence':[{'path':(ROOT/'receipts'/(stem+'.tool.json')).as_posix(),'type':'tool receipt; image data omitted'}],'coordinates':req['coordinates'],'status':'candidate_native_visual_QA_passed_pending_composite','nativeSizeMatchesPlan':True}
p.dump(str(dst)+'.generation.json',rec)
crop=[350,300,1100,1030]
with Image.open(ROOT/'guides'/(stem+'.native-guide.png')) as a,Image.open(dst) as b:
 out=Image.new('RGB',(1500,730));out.paste(a.crop(crop),(0,0));out.paste(b.crop(crop),(750,0))
 evidence=ROOT/'qa'/(stem+'-before-left-after-right-native100.png');out.save(evidence)
p.dump(str(evidence)+'.derivation.json',{'operation':'native crop/paste side-by-side; no resampling','sources':[p.metadata(ROOT/'guides'/(stem+'.native-guide.png'),'before'),p.metadata(dst,'after')],'sourceCrop':crop,'destinations':[[0,0],[750,0]],'sha256':p.hashfile(evidence)})
entry={'stem':stem,'nativeGlobalBox':req['coordinates']['nativeGlobalBox'],'sha256':rec['sha256'],'targetGlobalBox':[13880,39200,14500,39600],'mandatoryTargetSuggested':[380,403,1000,803],'suggestedROI':[220,250,1254,1254],'roiReason':'Keep top y<39047 outside repair selection to avoid overlap with independent upper-railing repair; include complete post foot and corrected bottom road. Visual perimeter QA required after binary selection.','baseAssemblySources':[x['path'] for x in req['sourceAssembly']],'bottomSeedGlobalBox':[13500,39821,14754,40051],'observations':['Entire post foot, raised base and adjacent slab plane continuous across former x14336 seam.','Vertical material rectangle and height jump removed; single existing post and inset panels preserved.','Corrected bottom230 available as same-coordinate sr4 TOP; old native candidates remain unchanged.'],'formalAccepted':False}
p.dump(ROOT/'qa'/(stem+'-handoff.json'),entry)
index=ROOT/'qa'/'r10_c04-right-column-worker-map.json';d=p.load(index);d['generationCount']+=1;d.setdefault('pendingNativeRepairs',[]).append(entry);d['updatedAtUtc']=p.now();p.dump(index,d)
print(entry)

