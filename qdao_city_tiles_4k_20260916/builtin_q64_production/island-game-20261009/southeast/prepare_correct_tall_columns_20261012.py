from workflow import *
jobs=[]
for pid in ['r12_c12_p44','r13_c12_p11']:
 v='v02';f=ROOT/'native'/f'{pid}_v01.png'
 refs=[{'file':str(f),'sha256':sha(f),'role':'complete native target with fixed north and west structural joins'}]+read(ROOT/'references.json')
 prompt="""Use case: precise-object-edit. Edit image 1 into the SAME registered 1254 x 1254 close-up of the existing daylight pier. Last three references are layout, material, painting style only. Preserve the exact top 230 pixels, left 230 pixels, all floorboards, railings, beam connections and other support columns.
Correct the full height of ONLY the broad MAIN CENTRAL TIMBER COLUMN continuing down from its existing gold cap/collar above. According to the approved layout, this tall main column continues straight vertically OUT OF THE BOTTOM EDGE of this crop. Its base and water-contact ring are below this crop and must NOT appear here. Remove the premature rounded foot, grey-green wet stain, encircling white ripple and reflection currently at the main column's lower end. Continue the same straight square timber faces, exact width, vertical grain, highlight and shade downward through the entire bottom edge. Keep it a single tall column with no new cap, base, seam or taper. Keep the attached diagonal/horizontal rails and genuine blue water openings untouched. The other narrower supports may retain their existing real wet bases/ripples. Keep all other water highlights unchanged except the erroneous main-column foot. No new props, metalwork, text or UI. Opaque square."""
 pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
 write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
 jobs.append({'pid':pid,'v':v,'args':{'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}})
print(json.dumps(jobs))
