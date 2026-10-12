exec((__import__('pathlib').Path(__file__).parent/'prepare.py').read_text(encoding='utf-8').split('snapshot=freeze')[0])
d=read(OUT/'prepared.json'); adopted=read(OUT/'snapshots/current-adopted-20261012.json'); amap={t['tileId']:t for t in adopted['tiles']}
checks=[]
for t in d['tiles']:
 cur=amap[t['tileId']]['record']['path']
 for index,item in enumerate(t['repairChain']):
  rec=read(cur); outpath=rec['output']['image']['path'] if 'image' in rec['output'] else rec['output']['path']
  base=np.array(Image.open(rec['base']['image']['path']).convert('RGB')); out=np.asarray(Image.open(outpath).convert('RGB'))
  source=np.asarray(Image.open(item['source']).convert('RGB'));mask=np.asarray(Image.open(item['mask']['path']).convert('L'));box=item['cropBox'];sel=mask==255
  region=base[box[1]:box[3],box[0]:box[2]];region[sel]=source[sel]
  checks.append({'tileId':t['tileId'],'record':cur,'recordSha256':sha(cur),'output':outpath,'outputSha256':sha(outpath),'source':item['source'],'sourceHashMatches':sha(item['source'])==item['sourceSha256'],'maskHashMatches':sha(item['mask']['path'])==item['mask']['sha256'],'maskValues':np.unique(mask).tolist(),'rawPixelReplayExact':bool(np.array_equal(base,out)),'mismatchingPixels':int(np.any(base!=out,axis=2).sum())})
  cur=rec['base']['record']['path']
 # First/last sixteen rows/columns: distinguishes actual border edits from near-border patches.
 old=np.asarray(Image.open(t['baselineFile']).convert('RGB'));new=np.asarray(Image.open(t['file']).convert('RGB'));mask=np.any(old!=new,axis=2)
 t['outer16PixelChangeCounts']={'north':int(mask[:16].sum()),'south':int(mask[-16:].sum()),'west':int(mask[:,:16].sum()),'east':int(mask[:,-16:].sum())}
# Focus on the two retained north-edge findings; create native 512px evidence, no scaling.
focus=[]
for tid,name,box in [('r05_c02','north-blossom-focus',(0,0,512,512)),('r07_c03','north-canopy-focus',(3072,0,3584,512)),('r07_c03','north-roof-focus',(2560,0,3072,512))]:
 t=next(t for t in d['tiles'] if t['tileId']==tid)
 pairfile=OUT/'crops'/f'{tid}-neighbor-north-'+Path('') if False else None
 seg=1 if tid=='r05_c02' else (4 if name=='north-canopy-focus' else 3)
 other='r04_c02' if tid=='r05_c02' else 'r06_c03'
 joined=Image.open(OUT/'crops'/f'{tid}-neighbor-north-{other}-seg{seg}.png').convert('RGB')
 left=0 if seg==1 or seg==4 else 512
 crop=joined.crop((left,0,left+512,512));p=OUT/'crops'/f'{tid}-{name}.png';crop.save(p)
 focus.append({'tileId':tid,'path':str(p),'sourceCrop':str(OUT/'crops'/f'{tid}-neighbor-north-{other}-seg{seg}.png'),'sourceCropBox':[left,0,left+512,512]})
write(OUT/'prepared.json',d);write(OUT/'native-repair-pixel-replay.json',checks);write(OUT/'focus-crops.json',focus)
print(json.dumps({'repairCount':len(checks),'allExact':all(x['rawPixelReplayExact'] and x['sourceHashMatches'] and x['maskHashMatches'] for x in checks),'border16changes':[{k:t[k] for k in ['tileId','outer16PixelChangeCounts']} for t in d['tiles']],'focus':focus},ensure_ascii=False,indent=2))
