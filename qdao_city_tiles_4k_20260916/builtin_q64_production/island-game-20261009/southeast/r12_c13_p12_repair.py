from workflow import ROOT,read,write,sha
import json
T='r12_c13_p12';v='v02';p=ROOT/'native/r12_c13_p12_v01.png';refs=[{'file':p.as_posix(),'sha256':sha(p),'role':'Exact full native edit target; fix only top-left gold bulb bottom contour'}]+read(ROOT/'references.json')
prompt="""Use case: precise-object-edit. Keep this FIRST image exactly the same composition, native 1254 x 1254 pixels. Correct one small malformed contour on the large golden rounded finial at top-left. Its bottom currently has an unintended small notch/double lobe at about x=230, y=255, where it meets the cylindrical gold collar. Make that one bulb a single clean convex rounded form: its lower outline must be one smooth continuous shallow ellipse, flowing naturally from the existing left curve into the right curve. Remove the notch, double-bottom lump and pinched shape. Keep the bulb position, size, highlight, gold palette and relationship to the cylindrical collar. The collar stays one regular rounded cylinder with an uninterrupted elliptical top.

Keep every other shape and position fixed: the wooden post, grain, the handrail, the separate clipped lower-right gold cap, all ocean ripples. Preserve the outer 115-pixel border and already-correct upper bulb contour exactly so neighboring tiles remain aligned. Correct the interior notch only as part of this complete native object view; do not zoom or move the object. Last three references are style/context only, no new objects. Crisp bright hand-painted Daoist game art. Output single opaque square of exactly 1254 x 1254.
"""
pp=ROOT/'prompts'/f'{T}_{v}.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8');write(ROOT/'prompts'/f'{T}_{v}.request.json',{'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
print(json.dumps({'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}))

