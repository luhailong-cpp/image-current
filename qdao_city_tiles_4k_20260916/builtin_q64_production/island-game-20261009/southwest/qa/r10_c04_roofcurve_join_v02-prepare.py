from pathlib import Path
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
old='r10_c04_roofcurve_join_v01';s='r10_c04_roofcurve_join_v02'
req=p.load(R/'prompts'/(old+'.request.json'));req['createdAtUtc']=p.now();req['references'][0]=p.metadata(R/'native'/(old+'.png'),'edit target with corrected full curve, remove single ghost gold strip on pavement only');req['repairOf']=old
p.dump(R/'prompts'/(s+'.request.json'),req);p.dump(R/'prompts'/(s+'.coordinates.json'),req['coordinates'])
p.dump(R/'qa'/(old+'-rejection.json'),{'status':'rejected','reason':'Curve and tile discontinuity repaired, but a ghost gold strip remains on the pavement above actual gold rim, local x540..990 y385..485.'})
