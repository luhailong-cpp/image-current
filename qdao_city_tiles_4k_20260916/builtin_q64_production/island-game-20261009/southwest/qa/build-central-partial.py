from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from native_tile_candidate import *

tile,prefix,nrows=sys.argv[1],sys.argv[2],int(sys.argv[3])
assert 1<=nrows<=4 and prefix.startswith('central-partial-')
d=load(ROOT/'qa/expansion-central-worker-map.json'); rows=[]; masks=[]; inputs=[]; seams=[]
r,c=map(int,re.fullmatch(r'r(\d+)_c(\d+)',tile).groups()); origin=[(c-1)*4096,(r-1)*4096]
assert not (QA/(prefix+'-report.json')).exists()
for ri in range(nrows):
    for ci in range(4):
        stem=d[tile][ri][ci]; assert stem
        p=ROOT/'native'/(stem+'.png'); rec=load(str(p)+'.generation.json'); assert sha(p)==rec['sha256']
        arr=np.array(Image.open(p).convert('RGB')); sid=ri*4+ci+1; ids=np.full(arr.shape[:2],sid,np.uint8)
        inputs.append({'sourceId':sid,'path':str(p),'sha256':sha(p),'nativeGlobalBox':rec['coordinates']['nativeGlobalBox']})
        if ci==0: canvas,mask=arr,ids
        else: canvas,mask,trace=join(canvas,mask,arr,ids,ci*STEP,f'row{ri+1}-column{ci+1}'); seams.append(trace)
    rows.append(canvas); masks.append(mask)
canvas,mask=rows[0],masks[0]
for ri in range(1,nrows):
    canvas,mask,trace=join(canvas.transpose(1,0,2),mask.T,rows[ri].transpose(1,0,2),masks[ri].T,ri*STEP,f'row{ri+1}')
    canvas,mask=canvas.transpose(1,0,2),mask.T; seams.append(trace)
canvas=canvas[HALO:HALO+nrows*STEP,HALO:HALO+4096]; mask=mask[HALO:HALO+nrows*STEP,HALO:HALO+4096]
for src in inputs:
    yy,xx=np.where(mask==src['sourceId']); a=np.array(Image.open(src['path']))
    assert np.array_equal(canvas[yy,xx],a[yy+origin[1]-src['nativeGlobalBox'][1],xx+origin[0]-src['nativeGlobalBox'][0]])
out=QA/(prefix+'-native.png');Image.fromarray(canvas).save(out);Image.fromarray(mask).save(QA/(prefix+'-source-mask.png'))
Image.fromarray(canvas).resize((1600,400*nrows),Image.Resampling.LANCZOS).save(QA/(prefix+'-preview-QA-only.png'))
views=[]
for y in range(1024,nrows*STEP,1024):
    for ci in range(4):
        p=QA/(prefix+f'-h{y}-c{ci+1}-native100.png');Image.fromarray(canvas[y-250:y+250,ci*1024:(ci+1)*1024]).save(p);views.append(str(p))
for x in (1024,2048,3072):
    for ri in range(nrows):
        p=QA/(prefix+f'-v{x}-r{ri+1}-native100.png');Image.fromarray(canvas[ri*1024:(ri+1)*1024,x-250:x+250]).save(p);views.append(str(p))
dump(QA/(prefix+'-report.json'),{'tile':tile,'completeRows':nrows,'candidateGlobalBox':origin+[origin[0]+4096,origin[1]+nrows*1024],'art':str(out),'sha256':sha(out),'sourceInputs':inputs,'exactSourcePixels':True,'mismatchedPixels':0,'seams':seams,'views':views,'notCompleteTile':nrows<4})
print(json.dumps({'native':str(out),'preview':str(QA/(prefix+'-preview-QA-only.png')),'views':views,'mismatchedPixels':0}))
