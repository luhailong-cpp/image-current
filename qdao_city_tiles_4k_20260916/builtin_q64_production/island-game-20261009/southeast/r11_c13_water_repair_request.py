from workflow import ROOT,read,write,sha,patch,now
T='r11_c13_p24';v='v02'
assert not (ROOT/'prompts'/f'{T}_{v}.request.json').exists()
target=ROOT/'native/r11_c13_p24_v01.png'
refs=[{'file':target.as_posix(),'sha256':sha(target),'role':'Exact original native art to repair; keep composition, coastline geometry and outside 115-pixel border unchanged'}]+read(ROOT/'references.json')
prompt="""Use case: precise-object-edit. Edit the FIRST attached native 1254 x 1254 image, retaining exact canvas size and exact composition. Output only the same repaired native patch.

The first image is the full-resolution target, not a blurry layout guide. Repair ONE defect: a faint perfectly vertical seam in the water at x=230 pixels from the left edge. It extends through the water from top to bottom and causes ripple facets to meet a straight material boundary. Remove this artificial vertical guide edge by making the water ripple and foam pattern naturally continuous on both sides of x=230. Use varied curved oblique wave shapes so there is no long straight seam, rectangle, stripe or change in cyan brightness. Work across the local water as needed, without adding or relocating anything.

PRESERVE exactly the outer 115-pixel border on all four sides, because these are immutable overlaps with neighboring native art. Preserve the entire large stone cliff on the right, all rock creases, every coastline contour, existing foam at the rock contact, top rocks/greenery, their global positions, proportions, perspective, color and texture. Do not change the broad cyan-blue water balance or white foam scale. Do not widen the rock, move the coast, introduce land or create architecture. Only remove the artificial interior water seam while keeping the target geometry intact.

The last three references are global layout and style context only. Do not recreate their buildings or island inside this local crop. No zoom, rescale, rotation, perspective shift, posterization, blur, text or new object. Preserve bright clean Daoist Q game painting. Native 1254 x 1254 opaque square.
"""
pp=ROOT/'prompts'/f'{T}_{v}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
req={'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}}
write(ROOT/'prompts'/f'{T}_{v}.request.json',req)
d=read(ROOT/'progress-r11_c13.json');d.update({'status':'repairing_water_guide_boundary','updatedAt':now(),'currentPatch':T,'nextStep':'One native edit to remove interior water guide boundary; keep v01 candidate until QA'});write(ROOT/'progress-r11_c13.json',d)
import json
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))

