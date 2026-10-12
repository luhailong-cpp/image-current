"""Exact cross-tile border inspection; no resizing, blending, or synthesis."""
from native_work import *
import argparse
ap=argparse.ArgumentParser(); ap.add_argument('a'); ap.add_argument('b'); args=ap.parse_args()
records=[read(ZONE/'tiles'/f'{t}.png.derivation.json') for t in (args.a,args.b)]
ims=[Image.open(x['file']).convert('RGB') for x in records]
for im,rec in zip(ims,records): assert im.size==(4096,4096) and sha(rec['file'])==rec['sha256']
a,b=[x['worldBox'] for x in records]
assert a[1]==b[1] and a[3]==b[3] and a[2]==b[0], 'Pass left tile then right tile'
out=Image.new('RGB',(512,4096));out.paste(ims[0].crop((3840,0,4096,4096)),(0,0));out.paste(ims[1].crop((0,0,256,4096)),(256,0))
prefix=f'{args.a}__{args.b}.final-border'
out.save(ZONE/'qa'/f'{prefix}.png')
parts=[]
for i in range(4):
 p=ZONE/'qa'/f'{prefix}.segment-{i+1}.png';out.crop((0,i*1024,512,(i+1)*1024)).save(p);parts.append(p.as_posix())
write(ZONE/'qa'/f'{prefix}.json',{'a':records[0]['file'],'b':records[1]['file'],'aSha256':records[0]['sha256'],'bSha256':records[1]['sha256'],'worldSeamX':a[2],'worldY':[a[1],a[3]],'coverageGapPixels':0,'operation':'Exact256pixel final4K edge crops side by side; no resize or blending','inspectionScale':1,'segments':parts,'status':'pending_visual_review','formalAccepted':False})
print(json.dumps({'file':(ZONE/'qa'/f'{prefix}.png').as_posix(),'segments':parts}))

