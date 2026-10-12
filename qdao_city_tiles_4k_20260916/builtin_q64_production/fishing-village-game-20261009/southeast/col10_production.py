"""Private col10 production helper: only owned tiles, four builtin references."""
import sys,json,re
from pathlib import Path
from datetime import datetime,timezone
import tile_native_workflow as w
Z=Path(__file__).resolve().parent
def own(t):
 assert t in ['r10_c10','r11_c10','r12_c10','r13_c10','r14_c10']
 return Z/t
def select(t,pid,rel):
 T=own(t);path=T/rel;assert path.resolve().is_relative_to(T.resolve()) and path.exists()
 sp=T/'selected-patches.json'
 s=w.read(sp) if sp.exists() else {'tile':t,'patches':{}}
 s['patches'][pid]=rel;s.update(updatedAt=w.now(),status='native_production_and_internal_QA',formalAccepted=False)
 w.write(sp,s)
 w.write(T/'progress.json',{'tile':t,'updatedAt':w.now(),'selectedNativeCount':len(s['patches']),'complete4kCount':0,'formalAcceptedCount':0,'status':s['status']})
 return {'selected':pid,'count':len(s['patches'])}
def request(t,pid,v,detail):
 T=own(t);r,c=int(pid[1]),int(pid[2]);tr,tc=w.tile_indices(t);spec=[]
 if c>1:
  sid=f'p{r}{c-1}';spec.append(f"{t}:{sid}:{w.read(T/'selected-patches.json')['patches'][sid]}")
 if r>1:
  nt=t;sid=f'p{r-1}{c}'
 else:nt=f'r{tr-1:02d}_c{tc:02d}';sid=f'p4{c}'
 if (Z/nt/'selected-patches.json').exists():
  spec.append(f"{nt}:{sid}:{w.read(Z/nt/'selected-patches.json')['patches'][sid]}")
 out=w.condition(t,pid,spec)
 coordinate=w.patch(w.read(T/'coordinate-plan.json'),pid)
 prompt=f"""Create exactly ONE native 1254 x 1254 pixel square raster game-map patch. This is {t}/{pid}, world native box {coordinate['globalBox']} on the locked 57344 square world. Its delivered core is [115,115,1139,1139], 1024 square; adjacent native overlap is 230 px. No final upscaling.
Four attached images have distinct roles. Image 1 is the mechanically coordinate-registered CONDITIONING GUIDE: sharp left x=0..229 and/or top y=0..229 are actual original-size neighboring pixels; lock their exact geometry, plank trajectories, scale, material color and lighting. Extend through x=230/y=230 smoothly with no visible boundary, ledge, line jump or rectangular change. Do not reinterpret the 230px boundary as scene geometry. The blurred remainder is layout-only position guidance, NEVER copy, upscale or preserve its pixels into finished artwork. Ignore blur artifacts and redesign every new pixel at native crisp quality.
Image 2 is approved full-world layout for placement only. Image 3 is independent daytime material/detail reference, not a coordinate crop. Image 4 is PRIMARY approved Q Daoist bright, clean, rounded painterly game style: smooth plump bevels, controlled hand-painted wood grain, saturated clean colors, polished shapes and warm daytime lighting. Use style only; do not import UI, text or night lighting. Other game layouts are functional only and cannot change this approved painting style.
Content requirements: {detail}
Camera, scale and vanishing directions are fixed by sharp neighbor strips. Preserve every feature crossing either sharp guide strip and continue it without moving, thickening, rotating or changing its design. Leave navigation surfaces open. Avoid standalone new buildings, whole boatyards, new prominent props absent from layout, thick outlines, photorealism, dirty texture, hazy blur, text, UI, logos and watermarks. Return only the single finished native artwork, no grids, frames, labels or comparison panels."""
 refs=[out['file']]+[r['path'] for r in w.approved_refs()]
 req={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':{'1':'exact native left/top overlap conditioning plus layout-only composition','2':'authoritative overall layout-only','3':'independent daylight detail/material','4':'primary approved rounded painterly Q Daoist style'},'submittedParameters':{'model':None,'quality':None}}
 (T/f'{pid}-{v}.prompt.txt').write_text(prompt,encoding='utf-8');w.write(T/f'{pid}-{v}.request.json',req)
 return {'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}
cmd,t,*args=sys.argv[1:]
if cmd=='request': result=request(t,*args)
elif cmd=='select': result=select(t,*args)
else:raise ValueError(cmd)
print(json.dumps(result,ensure_ascii=False))

