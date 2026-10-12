from workflow import *
from PIL import Image
name='r13_c12_p23';v='v02'
old=ROOT/'native/r13_c12_p23_v01.png';west=ROOT/'native/r13_c12_p22_v01.png';east=ROOT/'native/r13_c12_p24_v01.png';north=ROOT/'native/r13_c12_p13_v01.png'
im=Image.open(old).convert('RGB')
placements=[(west,(1024,0,1254,1254),(0,0)),(east,(0,0,230,1254),(1024,0)),(north,(0,1024,1254,1139),(0,0))]
for f,box,dest in placements:im.paste(Image.open(f).convert('RGB').crop(box),dest)
g=ROOT/'guides'/f'{name}.native-context-{v}.png';assert not g.exists();im.save(g)
write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'usableAsFinalArt':False,'operation':'Registered complete staircase object edit target; exact actual west/east overlap and only actual north core115; no final pixels painted','sources':[{'file':str(x),'sha256':sha(x)} for x in [old,west,east,north]],'placements':[{'file':str(f),'sourceCrop':list(box),'destination':list(dest)} for f,box,dest in placements]})
refs=[{'file':str(g),'sha256':sha(g),'role':'whole staircase edit target with actual final-core neighbor endpoints'}]+read(ROOT/'references.json')
prompt="""Use case: precise-object-edit. Edit image1 into the same exact 1254-square opaque painted daylight pier crop. Rebuild the COMPLETE two visible golden wooden landing/tread surfaces so they continue physically from the immutable LEFT230 to the fixed foreground RIGHT column. The current center is wrong: it turns the wide lower landing from the left into a thin rail and drops both front edges.
The LEFT230 is the authoritative finished western neighbor. Its UPPER full deck front edge enters at about y410 at the inner edge of that stripe and runs up-right. Continue that SAME upper deck front edge, at the SAME tangent, across the entire center to its existing attachment on the right column. The LOWER landing has a broad real board surface, roughly 350 pixels deep at the left stripe, and several complete long wood-board boundaries. Continue its entire broad surface across the middle to the right column, with the same perspective width, slope, plank count and spacing. Its front bright rim enters around y920 at the left stripe. Do not leave a thin isolated horizontal rail here. Do not allow either deck contour to step up/down at the left stripe, and do not terminate any groove inside a board.
Preserve the genuine open blue-water gap BETWEEN the upper and lower levels and the water below the lower level. Retain only existing necessary supports at their exact positions. Do not fill sea gaps with solid brown riser panels.
The tall foreground right column body and its water foot are already correct: preserve the complete right230, its x position, width, gold collar, foot height and lighting. It has no new cap here. Top115 contains actual north final-core pixels and must remain fixed; the rest of the center is editable to reconnect the full decks. Keep warm honey wood and painted blue sea. Last3refs are layout, material and painting style only. No added posts, gold caps, extra step or props, no text/UI."""
pf=ROOT/'prompts'/f'{name}_{v}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
write(ROOT/'prompts'/f'{name}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
write(ROOT/'prompts'/f'{name}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False})
q=ROOT/'qa/r12_c11-sol-20261012-upper-v03';rr=read(q/'root-changed-region-review.json');rr.update(externalEast4Status='pass actual hard join viewed by root');write(q/'root-changed-region-review.json',rr)
resume=read(ROOT/'production-resume-20261012.json')
for c in resume['currentAdoptedCandidates']:
 if c['tile']=='r12_c11':c.update(candidate=str(ROOT/'tiles/r12_c11.candidate-sol-20261012-v03.png'),sha256='c84527b2316aa3415e3b4a5099e52eecb23d9db83bd868347bcdc3fa9d93e7a5',sourceProof=str(q/'source-pixel-proof.json'),review=str(q/'root-changed-region-review.json'),pending='New upper column passes all changed outer joins and unchanged24internal/9junctions; actual southern tile and remaining western neighbors unfinished.')
resume.update(updatedAtUtc=now(),inFlightRequests=['r13_c12_p23_v02'])
resume['counts']['generatedNativeCount']=len(list((ROOT/'native').glob('*.png')))
write(ROOT/'production-resume-20261012.json',resume)
for fname in ['progress.json','production-state.json']:
 p=read(ROOT/fname);p.update(updatedAt=now(),currentAdoptedCandidates=resume['currentAdoptedCandidates'],rootInFlightCount=1,inFlight=True,nextStep='Complete r13 native deck stair repair and lower sea.')
 if fname=='progress.json':p.update(**resume['counts'])
 else:p['counts']=resume['counts']
 write(ROOT/fname,p)
p=read(ROOT/'progress-r13_c12.json');p.update(workingVersions={'11':'v02','12':'v01','13':'v01','14':'v02','21':'v01','22':'v01','24':'v01'},pendingRepairs=['p23v01 staircase width/front-edge mismatch with west p22; entire staircase v02 in preparation.'],inFlightRequests=['r13_c12_p23_v02']);write(ROOT/'progress-r13_c12.json',p)
print(json.dumps({'guide':str(g),'internalPassed4kCount':resume['counts']['internalPassed4kCount']}))

