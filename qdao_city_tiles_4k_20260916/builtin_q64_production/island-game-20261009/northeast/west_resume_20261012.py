from native_work import *
import sys
cmd,ident=sys.argv[1:3]
if cmd=='accept':
    for name in sys.argv[3:]:
        p=ZONE/'qa'/name
        q=read(p); q.update(status='passed_available_native_join',reviewer='west_resume_20261012',reviewedAtUtc=now());write(p,q)
    p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='usable_native_candidate',internalSeams='direct native and available 1:1 seams reviewed; final full tile review pending');write(p,q)
    tile=ident.split('_p')[0];p=ZONE/f'selection-{tile}.json';s=read(p);b=patch(ident)['coreWorldBox'];s['cores'][(b[1]%4096)//1024][(b[0]%4096)//1024]=ident;s['updatedAtUtc']=now();write(p,s)
    print(json.dumps({'selected':ident,'sha256':q['sha256']}))
elif cmd=='refs':
    p=ZONE/'prompts'/f'{ident}.inputs.json';x=read(p);x[1]['role']='native neighbor reference plate: LEFT=ABOVE, RIGHT=RIGHT neighbor; both1254-square unscaled';write(p,x);print(json.dumps(x))
elif cmd=='cross':
    ids=sys.argv[3:7];boxes=[(883,883,1139,1139),(115,883,371,1139),(883,115,1139,371),(115,115,371,371)];out=Image.new('RGB',(512,512));sources=[]
    for i,key in enumerate(ids):
        p=ZONE/'native'/f'{key}.png';out.paste(Image.open(p).crop(boxes[i]),((i%2)*256,(i//2)*256));sources.append({'file':p.as_posix(),'sha256':sha(p),'crop':list(boxes[i])})
    p=ZONE/'qa'/f'west-resume-{ident}.cross.png';assert not p.exists();out.save(p);write(p.with_suffix('.json'),{'sources':sources,'operation':'exact native crops, no resizing or blending','inspectionScale':1,'status':'pending_visual_review'});print(p)
