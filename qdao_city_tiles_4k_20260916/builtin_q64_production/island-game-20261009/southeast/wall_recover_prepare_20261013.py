from workflow import *
from PIL import Image
import sys,subprocess
sel={'11':'v01','12':'v01','13':'v02','14':'v01','22':'v02','23':'v01','24':'v03','33':'v01','34':'v02','43':'v02','44':'v02'}
q=ROOT/'qa'/'wall-resume-20261013'
p=ROOT/'production-resume-wall-20261013.json'
d=read(p)
for rc in ['22','24','33','34','43']:
 pid='r08_c10_p'+rc;v=sel[rc];src=ROOT/'native'/f'{pid}_{v}.png'
 status='not_passed_east_wall_foot' if rc=='24' else 'quick_layout_and_edges_passed'
 note='East wall foot still has hard step after second attempted repair. Retain v03 pending grouped repair; N pavement improved.' if rc=='24' else 'Recovered saved native, independently viewed full source and all saved actual core-edge cuts; geometry usable for further missing-core production. Full material/guide-boundary review remains pending.'
 d['generated'][pid]={'file':str(src),'sha256':sha(src),'version':v,'status':status,'note':note,'reviewedAt':now()}
 review=read(q/f'{pid}-{v}-review.json');review['recoveryReview']={'by':'wall_recover','at':now(),'status':status,'note':note};write(q/f'{pid}-{v}-review.json',review)
d['agent']='wall_recover';d['generatedNativeCount']=len(list((ROOT/'native').glob('r08_c10_*.png')));d['uniqueCoreCount']=len(set(f.name[:11] for f in (ROOT/'native').glob('r08_c10_*.png')));d['selectedCoreCount']=sum(x['status']=='quick_layout_and_edges_passed' for x in d['generated'].values());d['inFlightRequests']=[];d['inFlight']=False;d['updatedAt']=now();write(p,d)
neighbors={'21':['11','22'],'32':['22','33'],'42':['43'],'31':['21','32'],'41':['31','42']}
descs={'21':'Mostly open pale blue-grey diagonal rectangular paving with a narrow planted grass inset along lower-left edge, exactly as the guide. Do not invent objects. Match every stone edge across top and right anchor strips. Pale beige narrow separator ribbons follow guide.', '32':'Open diagonal pale grey courtyard stone paving. Match the exact stone joint geometry and warm-ivory separator ribbons in north and east anchors, preserving the small layout grass wedge at left only where shown. No new props.', '42':'Diagonal pale grey pavement with its existing narrow grass/floral inset along lower part as shown in guide. Preserve crossing ribbon width and exact angle at right neighbor. No new structures.', '31':'Existing small rectangular garden grass/flowers between pale stone paths as layout. Preserve all garden-boundary bends and width, crop-only no added shrub or lantern. Match north and east paving.', '41':'Existing pale grey walkway and small edge grass/flower area exactly per layout. Preserve northwest and northeast paths and all stone curb contours; no props, no new buildings.'}
for rc in sys.argv[1:]:
 pid='r08_c10_p'+rc
 assert not list((ROOT/'native').glob(pid+'*.png'))
 ns=[f'r08_c10_p{n}_{sel.get(n,"v01")}.png' for n in neighbors[rc]]
 out=subprocess.run([sys.executable,str(ROOT/'wall_batch_workflow_20261013.py'),'prepare',pid,'v01',descs[rc],*ns],capture_output=True,text=True,check=True)
 print(out.stdout)
