"""Read-only alpha-envelope measurements in human-selected support-foot ROIs."""
from pathlib import Path
from PIL import Image
import json
B=Path(__file__).resolve().parents[1]
rois={
 'run-W-01-v2':(270,1060,650,1254), 'run-W-02-v1':(350,1050,650,1254),
 'run-W-03-v2':(550,1070,780,1254), 'run-W-04-v5':(560,1050,830,1254),
 'run-W-05-v3':(740,1090,950,1254), 'run-W-06-v5':(700,1110,930,1254),
 'run-W-07-v6':(820,1080,1090,1254), 'run-W-08-v4':(870,1080,1100,1254),
 'run-W-09-v5':(330,1080,640,1254), 'run-W-10-v4':(390,1070,675,1254),
 'run-W-11-v6':(560,1050,830,1254), 'run-W-12-v5':(620,1060,880,1254),
 'run-W-13-v4':(720,1060,980,1254), 'run-W-14-v4':(620,1080,900,1254),
 'run-W-15-v5':(820,1100,1080,1254), 'run-W-16-v4':(820,1100,1130,1254)}
result={}
for key,roi in rois.items():
 p=B/'staging'/f'{key}.png'
 if not p.exists():continue
 im=Image.open(p).convert('RGBA'); a=im.getchannel('A').crop(roi); mask=a.point(lambda v:255 if v>128 else 0)
 bb=mask.getbbox(); result[key]={'roi':roi,'alpha128BBox':None if not bb else [bb[0]+roi[0],bb[1]+roi[1],bb[2]+roi[0],bb[3]+roi[1]],'measurementOnlyNotApproval':True}
(B/'review/support-boot-envelope-W.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
