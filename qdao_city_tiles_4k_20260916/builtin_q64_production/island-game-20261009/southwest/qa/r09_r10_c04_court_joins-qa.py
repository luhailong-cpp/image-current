from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
entries=[]
for which in [1,2]:
    stem=f'r09_r10_c04_court_join{which}_v01';src=R/'native'/(stem+'.png');before=R/'guides'/(stem+'.native-guide.png');rec=p.load(str(src)+'.generation.json');im=Image.open(src)
    assert im.size==(1254,1254) and im.mode=='RGB' and p.hashfile(src)==rec['sha256']
    for ref in rec['references']:assert p.hashfile(ref['path'])==ref['sha256']
    crop=[0,480,1254,690];out=Image.new('RGB',(1254,420));out.paste(Image.open(before).crop(crop),(0,0));out.paste(im.crop(crop),(0,210));dst=R/'qa'/(stem+'-before-top-after-bottom-native100.png');out.save(dst)
    p.dump(str(dst)+'.derivation.json',{'operation':'native crop/paste vertical comparison, no scaling','sources':[p.metadata(before,'before'),p.metadata(src,'after')],'sourceCrop':crop,'destinations':[[0,0],[0,210]],'sha256':p.hashfile(dst)})
    entry={'stem':stem,'nativeGlobalBox':rec['coordinates']['nativeGlobalBox'],'sha256':rec['sha256'],'suggestedROI':[0,300,1254 if which==1 else 900,950],'mandatoryTargetSuggested':[100,534,1154 if which==1 else 780,644],'suggestedBand':70,'method':'actual builtin AI material correction; final use only same-coordinate binary source selection','nativeDimensionsRGBVerified':True,'allReferenceHashesMatch':True,'visualEvidence':dst.as_posix(),'observations':['Horizontal straight value/material splice at local y584 removed from native paving.','Flagstone joints/bevels and original scene objects retained; no invented plants or structures.'],'limitations':['Final selection perimeter and cross-source overlap require composite QA.','Second source ROI stops before wood-right region to preserve accepted natural wood material variation.'] if which==2 else ['Final selection perimeter requires native composite QA.'],'formalAccepted':False}
    if which==1:entry['observations'].append('Existing two red-paper groups and stone support remain in original positions.')
    else:entry['observations'].append('Wood scroll, long beam and curved foot retain original geometry; first254 pixels seeded with previous source.')
    p.dump(R/'qa'/(stem+'-handoff.json'),entry);entries.append(entry)
a=R/'native/r09_r10_c04_court_join1_v01.png';b=R/'native/r09_r10_c04_court_join2_v01.png';out=Image.new('RGB',(600,1254));out.paste(Image.open(a).crop((827,0,1127,1254)),(0,0));out.paste(Image.open(b).crop((127,0,427,1254)),(300,0));dst=R/'qa/r09_r10_c04_court_joins-overlap-native100.png';out.save(dst)
p.dump(str(dst)+'.derivation.json',{'operation':'same-coordinate mechanical core-side crop/paste inside native254 overlap; no scaling','sources':[p.metadata(a,'left repair'),p.metadata(b,'right repair')],'sourceCrops':[[827,0,1127,1254],[127,0,427,1254]],'destinations':[[0,0],[300,0]],'globalBox':[14327,36280,14927,37534],'splitGlobalX':14627,'sha256':p.hashfile(dst)})
p.dump(R/'qa/r09_r10_c04_court_joins-handoff.json',{'sources':entries,'sourceOrder':['r09_r10_c04_court_join1_v01','r09_r10_c04_court_join2_v01'],'overlapPixels':254,'overlapNativeEvidence':dst.as_posix(),'col4MildWoodJoinDisposition':'Accept natural minor brush/material variation per root instruction; no extra source generated.','formalAccepted':False})
idx=R/'qa/r10_c04-right-column-worker-map.json';d=p.load(idx);d.setdefault('pendingNativeRepairs',[]).extend(entries);d['updatedAtUtc']=p.now();p.dump(idx,d)
print({'sources':[{k:e[k] for k in ['stem','nativeGlobalBox','sha256']} for e in entries],'overlap':dst.as_posix()})
