from workflow import ROOT,read,write,sha,now
from pathlib import Path
for rc in ['14','34']:
 pid='r14_c11_p'+rc;target=ROOT/'native'/f'{pid}_v01.png';p=ROOT/'prompts'/f'{pid}_v02.prompt.txt';q=ROOT/'prompts'/f'{pid}_v02.request.json'
 assert not p.exists() and not q.exists()
 defect='horizontal line at y=230 and vertical line at x=1024' if rc=='14' else 'vertical line at x=1024'
 prompt=f'''Use case: precise-object-edit.
Edit image 1, a native 1254 x 1254 hand-painted turquoise sea game-map patch. Remove the artificial rectangular material transitions at {defect}: make the interior water coloration, caustic cell size and fine painted texture vary organically across these straight guide-boundary lines so no rectangular strip can be seen. These lines are accidental editing artifacts, not real objects. Preserve the exact caustic and wave positions within the outermost 150 pixels on all four sides, including their current brightness, so neighboring tiles remain continuous. Smoothly redraw only the inner transitions and their immediate neighborhoods, maintaining crisp original-scale painted detail, never blur or smear. Keep continuous soft daylight and the same ocean colors. No new objects, stars, boats, rocks, text, border or UI.
Image 2 is full-island layout only; image 3 materials only; image 4 painting style only. Preserve the close crop of image 1; do not import any objects from the references. Output the same opaque 1254 x 1254 square framing.'''
 p.write_text(prompt,encoding='utf-8');write(q,dict(promptPath=str(p),promptSha256=sha(p),references=[dict(file=str(target),sha256=sha(target),role='existing native edit target; preserve exact outermost 150-pixel geometry')]+read(ROOT/'references.json'),transparent_background=False,submittedParameters=dict(model=None,quality=None),preparedAt=now(),status='prepared_not_submitted'))
 print(str(q))
