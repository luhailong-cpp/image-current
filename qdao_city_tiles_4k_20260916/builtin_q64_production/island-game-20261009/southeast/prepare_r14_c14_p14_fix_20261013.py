from workflow import *
pid='r14_c14_p14';version='v02';src=ROOT/'native'/f'{pid}_v01.png'
prompt='Edit this exact native 1254 x 1254 water patch. Remove ONLY the pale yellow/gold reflected light in the upper-left corner and along the left edge. Replace that small gold area with matching blue/turquoise water and white/light-cyan caustics from the immediately surrounding water. There is NO golden reflection at this map coordinate. Preserve all wave contours, texture scale, blue hue, brightness and every other part of the image exactly. Keep full square dimensions and crop unchanged. No object, shore, boat, frame, writing or watermark. This is a local color/content correction on native generated artwork; output one opaque image.'
pf=ROOT/'prompts'/f'{pid}_{version}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
refs=[{'file':src.as_posix(),'sha256':sha(src),'role':'exact native edit target; change gold reflection to blue water only'}]
write(ROOT/'prompts'/f'{pid}_{version}.request.json',{'promptPath':pf.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
write(ROOT/'prompts'/f'{pid}_{version}.args.json',{'prompt':prompt,'referenced_image_paths':[src.as_posix()],'transparent_background':False})
write(ROOT/'r14_c14-quick-review-20261013.json',{'updatedAt':now(),'selected':{'11':'v01'},'unselected':{'14':{'version':'v01','reason':'unwanted upper-left gold reflection copied from material reference; layout is plain water; local correction v02 prepared'}},'internalPassed':False,'formalAccepted':False})
print('prepared local p14 gold-reflection correction; p11 layout pass')
