from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
top=R/'guides/r10_c04_s03_02_v02.postfoot-context.png';lower=R/'native/r10_c04_s04_02_v02.png'
out=Image.new('RGB',(1254,600));out.paste(Image.open(top).crop((0,839,1254,1139)),(0,0));out.paste(Image.open(lower).crop((0,115,1254,415)),(0,300))
fp=R/'qa/r10_c04_s04_02_v02-corrected-top-native100.png';out.save(fp)
p.dump(str(fp)+'.derivation.json',{'operation':'same-coordinate native crop/paste at core boundary y39936; no interpolation','sources':[p.metadata(top,'above with corrected whole-foot source'),p.metadata(lower,'new lower tile')],'sourceCrops':[[0,839,1254,1139],[0,115,1254,415]],'destinations':[[0,0],[0,300]],'globalBox':[13197,39636,14451,40236],'sha256':p.hashfile(fp)})
repair='r10_c04_roofcurve_join_v02';rp=R/'native'/(repair+'.png');rec=p.load(str(rp)+'.generation.json')
entry={'stem':repair,'nativeGlobalBox':rec['coordinates']['nativeGlobalBox'],'sha256':rec['sha256'],'suggestedROI':[0,240,1254,1254],'mandatoryTargetSuggested':[386,250,686,1139],'roiReason':'Full-width curved eave plus all affected blue rows, top kept below earlier whole-foot target; native binary-selection perimeter QA required. Source extends beyond tile bottom to y41075.','baseAssemblySources':['r10_c04_s04_02_v02','r10_c04_s04_03_v01'],'observations':['Gold/red eave and blue cylindrical courses now continuous through former x14336 step.','Native crisp; first wide candidate residual hazy gold ghost removed by v02.'],'limitations':['Small tapered upper gold face near local x690..1100,y380..480 remains; root independent visual judgment requested before formal acceptance.','Whole source not yet integrated; raw s04_02_v02 alone retains original RIGHT geometry defect.'],'formalAccepted':False}
p.dump(R/'qa'/(repair+'-handoff.json'),entry)
idx=R/'qa/r10_c04-right-column-worker-map.json';d=p.load(idx);d.setdefault('pendingNativeRepairs',[]).append(entry);d['updatedAtUtc']=p.now();p.dump(idx,d)
entries=[]
for stem in ['r10_c04_s02_02_v01','r10_c04_s03_02_v02','r10_c04_s04_02_v02']:
    f=R/'native'/(stem+'.png');rr=p.load(str(f)+'.generation.json');im=Image.open(f)
    assert im.size==(1254,1254) and im.mode=='RGB' and p.hashfile(f)==rr['sha256']
    refs=[]
    for ref in rr['references']:
        ok=p.hashfile(ref['path'])==ref['sha256'];assert ok;refs.append({'path':ref['path'],'sha256Matches':ok})
    entries.append({'stem':stem,'sha256':rr['sha256'],'coordinates':rr['coordinates'],'nativeDimensionsRGBVerified':True,'allReferenceHashesMatch':True,'references':refs,'receiptPresent':(R/'receipts'/(stem+'.tool.json')).exists()})
p.dump(R/'qa/r10_c04-col2-handoff.json',{'selectedBases':entries,'pendingNativeRepairs':[p.load(R/'qa/r10_c04_postfoot_join_v01-handoff.json'),entry],'upperRailRepairOwner':'c04_native_review: r10_c04_wall_col12_join_v01','nativeQAEvidence':['qa/r10_c04_s04_02_v02-corrected-top-native100.png','qa/r10_c04_s04_02_v02-right-column-right-native100.png'],'notes':['All sources actually generated via builtin tool, provenance/1254 dimensions/ref hashes verified.','s02sc2v01 correct inset railing layout; old LEFT masonry source deliberately superseded by other worker.','s03sc2v02 is structure base requiring postfoot join. s04sc2v02 requires roofcurve join.','Do not use rejected sr3 v01/v03 or sr4v01; no progress/index/output mutation here.'],'formalAccepted':False})
print({'handoff':'qa/r10_c04-col2-handoff.json','roofRepair':entry,'bases':[{k:e[k] for k in ['stem','sha256']} for e in entries]})
