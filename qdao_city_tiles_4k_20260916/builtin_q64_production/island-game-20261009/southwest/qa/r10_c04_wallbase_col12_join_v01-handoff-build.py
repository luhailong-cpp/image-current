from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
stem='r10_c04_wallbase_col12_join_v01';src=R/'native'/(stem+'.png');before=R/'guides'/(stem+'.native-guide.png');co=p.load(R/'prompts'/(stem+'.coordinates.json'))
crop=[320,440,820,1254];out=Image.new('RGB',(1000,814));out.paste(Image.open(before).crop(crop),(0,0));out.paste(Image.open(src).crop(crop),(500,0));dst=R/'qa'/(stem+'-before-left-after-right-native100.png');out.save(dst)
p.dump(str(dst)+'.derivation.json',{'operation':'native crop/paste side-by-side only; no scaling','sourceCrop':crop,'sources':[p.metadata(before,'before'),p.metadata(src,'after')],'destinations':[[0,0],[500,0]],'sha256':p.hashfile(dst)})
entry={'stem':stem,'nativeGlobalBox':co['nativeGlobalBox'],'sha256':p.hashfile(src),'suggestedROI':[120,300,950,1254],'mandatoryTargetSuggested':[400,503,700,1139],'roiReason':'Top y>=39097 avoids upper-wall repair; right x<=13700 avoids whole-postfoot ROI beginning13720. Whole gold rim and wall base included through bottom native halo.','bottomSeedGlobalBox':[12750,39821,14004,40051],'baseAssemblySources':['r10_c04_s03_01_v03','r10_c04_s03_02_v02'],'guidePriorRepairs':['r10_c04_wall_col12_join_v01','r10_c04_postfoot_join_v01'],'observations':['Existing single lower wall plinth and moss footline continuous at former x13312 join.','Foreground gold disk/collar contour continuous with green panels and radial ribs retained.','Full native blue/red/gold bottom remains sharp and can seed sr4 TOP.'],'limitations':['Native binary-selection perimeter must be reviewed after integration.','Bottom230 guidance is mechanical same-coordinate use of this actual source, not modification of prior source files.'],'formalAccepted':False}
p.dump(R/'qa'/(stem+'-handoff.json'),entry)
idx=R/'qa/r10_c04-right-column-worker-map.json';d=p.load(idx);d.setdefault('pendingNativeRepairs',[]).append(entry);d['updatedAtUtc']=p.now();p.dump(idx,d)
print(entry)
