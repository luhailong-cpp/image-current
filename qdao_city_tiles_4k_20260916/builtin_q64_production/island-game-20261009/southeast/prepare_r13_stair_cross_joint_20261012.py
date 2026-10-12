from workflow import *
from PIL import Image
name='r13_c12_stair_cross_joint_v01'
origin=(1421,909)
versions={'12':'v01','13':'v01','22':'v01','23':'v02','32':'v01'}
guide=Image.new('RGB',(1254,1254))
coverage=Image.new('L',(1254,1254))
placements=[]
for rc,v,box,dst in [('22','v01',(512,0,1254,1254),(0,0)),('23','v02',(0,0,742,1254),(512,0))]:
 f=ROOT/'native'/f'r13_c12_p{rc}_{v}.png'
 guide.paste(Image.open(f).convert('RGB').crop(box),dst)
 coverage.paste(255,(dst[0],dst[1],dst[0]+box[2]-box[0],dst[1]+box[3]-box[1]))
 placements.append({'file':str(f),'sha256':sha(f),'sourceCrop':list(box),'destination':list(dst),'role':'registered native halo fallback; actual core authority pasted next'})
for rc,v in versions.items():
 r,c=map(int,rc);ox=(c-1)*1024;oy=(r-1)*1024
 x0=max(origin[0],ox);y0=max(origin[1],oy);x1=min(origin[0]+1254,ox+1024);y1=min(origin[1]+1254,oy+1024)
 if x0>=x1 or y0>=y1:continue
 f=ROOT/'native'/f'r13_c12_p{rc}_{v}.png'
 box=(115+x0-ox,115+y0-oy,115+x1-ox,115+y1-oy)
 dst=(x0-origin[0],y0-origin[1])
 guide.paste(Image.open(f).convert('RGB').crop(box),dst)
 coverage.paste(255,(dst[0],dst[1],dst[0]+x1-x0,dst[1]+y1-y0))
 placements.append({'file':str(f),'sha256':sha(f),'sourceCrop':list(box),'destination':list(dst)})
assert coverage.getextrema()==(255,255)
gf=ROOT/'guides'/f'{name}.png';assert not gf.exists();guide.save(gf)
write(Path(str(gf)+'.generation.json'),{'file':str(gf),'sha256':sha(gf),'usableAsFinalArt':False,'tile':'r13_c12','tileRelativeOrigin':list(origin),'operation':'Coordinate-registered actual final-core native pixels only as an editable guide.','placements':placements})
prompt='''Edit image1 as one complete unchanged-scale 1254-square native game-art crop. This is a WHOLE OBJECT repair spanning the internal left/right tile join at x627. The current two wooden pier landings have an accidental vertical discontinuity at x627: their golden front edges and lower floor back edge jump downward on the right. Rebuild the complete visible upper landing and lower landing as physically continuous wooden surfaces across this join. Match the left and right finished outer ends, use coherent perspective, uniform full-size board spacing, and one uninterrupted front contour for each landing. A plank groove must meet another real plank boundary or a complete perpendicular plank end; never leave a dangling groove. Preserve the exact TOP115 north finished floor and the outermost115 at left, right and bottom. The complete center is editable, including both sides of x627, so reconnect each complete landing instead of copying the current stepped seam. Keep the genuine open blue sea between the levels and under the lower landing, and retain only existing short wooden supports. No extra tread, no solid riser filling water, no new post or gold cap, no zoom or layout expansion. Same bright honey-gold wood, crisp rounded hand-painted forms, daylight turquoise painted sea and restrained grain. Final3refs supply whole-map layout, material and approved painting style; no text, UI, people or animals.'''
refs=[{'file':str(gf),'sha256':sha(gf),'role':'exact-registered whole-object edit target, guides only'}]+read(ROOT/'references.json')
pf=ROOT/'prompts'/f'{name}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
req={'tile':'r13_c12','tileRelativeOrigin':list(origin),'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}}
write(ROOT/'prompts'/f'{name}.request.json',req)
write(ROOT/'prompts'/f'{name}.args.json',{'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False})
p=read(ROOT/'progress-r13_c12.json');p['workingVersions'].update({'32':'v01','34':'v01'});p.update(updatedAt=now(),status='whole_stair_object_repair',inFlightRequests=['r13_c12_p31_v02','r13_c12_p42_v01','r13_c12_p44_v01',name],pendingRepairs=['p23v01/v02 rejected: upper/lower landing contours jump versus p22; complete crossing stair object in preparation.'])
p['missingPatches']=[f'r13_c12_p{r}{c}' for r in range(1,5) for c in range(1,5) if f'{r}{c}' not in p['workingVersions']]
write(ROOT/'progress-r13_c12.json',p)
write(ROOT/'qa/r13-stair-p23-rejected-v01-v02.json',{'status':'rejected_not_adopted','sources':[str(ROOT/'native/r13_c12_p23_v01.png'),str(ROOT/'native/r13_c12_p23_v02.png')],'reason':'Major physical upper/front and lower/back edge jumps at actual p22/p23 core cut; complete physical stair landing repair required.','evidence':[str(ROOT/'qa/r13p22p23-v01.hard-seam-100pct.png'),str(ROOT/'qa/r13p22p23-v02.hard-seam-100pct.png')]})
resume=read(ROOT/'production-resume-20261012.json');resume.update(updatedAtUtc=now(),currentTile='r13_c12',inFlightRequests=p['inFlightRequests'],nextStep='Complete r13 crossing stair object and remaining lower sea cores, assemble native-pixel candidate and inspect real joins.');resume['counts']['generatedNativeCount']=len(list((ROOT/'native').glob('*.png')));write(ROOT/'production-resume-20261012.json',resume)
print(json.dumps({'guide':str(gf),'request':str(ROOT/'prompts'/f'{name}.args.json'),'selectedCount':len(p['workingVersions'])}))
