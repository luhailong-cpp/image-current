from workflow import *
import subprocess,sys,os
tid='r08_c13';pf=ROOT/f'progress-{tid}.json';env=dict(os.environ,ISLAND_PROGRESS_FILE=pf.name)
neighbors={'11':['r08_c12_p14_v01.png'],'14':[],'41':['r08_c12_p44_v02.png','r09_c13_p11_v01.png'],'44':['r09_c13_p14_v01.png'],'12':['11'],'13':['12','14'],'21':['r08_c12_p24_v01.png','11'],'31':['r08_c12_p34_v02.png','41'],'42':['41','r09_c13_p12_v01.png'],'43':['42','44','r09_c13_p13_v02.png'],'34':['44'],'24':['14','34'],'22':['21','12'],'23':['22','24','13'],'32':['31','42','22'],'33':['32','34','23','43']}
desc={
'11':'Upper-right end of an existing courtyard. The sharp LEFT edge contains the existing warm wood corner post and grey paving. Keep that narrow timber at the left, no additional wooden structure. Upper interior is the existing dense planted garden bed with green leaves and sparse small pale white/pink blossoms; lower area is broad pale-grey/blue-grey paving slabs with the few existing spent red rectangular paper/firecracker scraps at the exact layout positions. No new tree, urn, box or free-standing ornament.',
'14':'Close cropped section of an existing ivory stone balustrade. A large pale square stone pillar is cropped along the LEFT side and exits the TOP; do not fit a complete pillar or cap within this image. The same broad solid ivory stone panel extends diagonally upward toward the top-right, with its smooth low-contrast face and rounded coping. Small green planted verge and a few existing orange/pink blossoms below/right. Preserve exact silhouette and diagonal direction from guide; no new fence, gate, building, small nested panel, or decorative carving.',
'41':'Continuous existing dense garden canopy, filling the crop. Match the exact sharp LEFT and BOTTOM leaf/branch continuation: layered rounded green and fresh lime leaves, a few small white flowers with yellow centers, fine brown branches within deep green recesses. Bright painted daylight, crisp individual leaves at the same scale. No added trunk, ground, stone, flowerpot or new object.',
'44':'Close-cropped existing large rounded pale-grey rock on the RIGHT/lower portion. Continue its exact stone mass upward from the sharp BOTTOM anchor; no new separate boulder and do not shrink it to fit. Broad natural pale-grey paving and a narrow soft-green verge at the left, sparse existing wall-side foliage around the rock. Match native rock facet size and restrained hairline stone cracks. No added structure, people or objects.'}
for rc in sys.argv[1:]:
 pid=f'{tid}_p{rc}';v='v01';assert not (ROOT/'native'/f'{pid}_{v}.png').exists()
 ns=[n if n.endswith('.png') else f'{tid}_p{n}_v01.png' for n in neighbors[rc]]
 guide=ROOT/'guides'/f'{pid}.native-context-v01.png'
 if ns and not guide.exists():subprocess.run([sys.executable,str(ROOT/'r12_context.py'),pid,v,*ns],check=True,env=env,capture_output=True,text=True)
 d=desc.get(rc,'Continue precisely the existing ivory stone balustrade, broad natural pale-grey stone paving, and planted garden/rock portions that actually appear in this exact coordinate guide. Match the position, physical contour, scale and tangent of every sharp overlap. No added objects or miniature complete structures. Render only the local crop contents, matching each real material without retaining a straight boundary between sharp context and redrawn area.')
 af=ROOT/'prompts'/f'{pid}_{v}.args.json'
 if not af.exists():
  rr=subprocess.run([sys.executable,str(ROOT/'request.py'),pid,v,d],check=True,env=env,capture_output=True,text=True);write(af,json.loads(rr.stdout))
 print(json.dumps({'patch':pid,'args':str(af)}))
