from pathlib import Path
import sys,subprocess,json
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest');S=B/'r13_c05/pipeline';py=sys.executable
tile,patch,attempt,source,observation=sys.argv[1:6]
def run(args):
 r=subprocess.run([py,'-X','utf8']+list(map(str,args)),capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;return r.stdout
if source!='none':
 run([S/'save-builtin-20261012.py',tile,patch,attempt,source,observation])
 run([B/'native_pipeline.py',tile,'ingest','--row',int(patch[1:3]),'--col',int(patch[4:6]),'--attempt',attempt,'--source',B/tile/'pipeline/returns'/f'{patch}.{attempt}.png','--receipt',B/tile/'pipeline/receipts'/f'{patch}.{attempt}.receipt.json'])
if len(sys.argv)>6:
 nextpatch,prefix=sys.argv[6:8]; p=B/tile/'pipeline'/f'{nextpatch}.content-prefix-20261012.txt';assert not p.exists();p.write_text('CONTENT LOCK: '+prefix+'\n',encoding='utf-8')
 args=[B/'native_pipeline.py',tile,'prepare','--row',int(nextpatch[1:3]),'--col',int(nextpatch[4:6]),'--attempt','resumed-full64-v01','--content-prefix-file',p]
 if int(nextpatch[1:3])==1:
  anchors=list((B/tile/'pipeline/anchors').glob('*bottom230.native.png'));assert len(anchors)==1;args+=['--anchor-top',anchors[0]]
 run(args)
 run([S/'checkpoint-lane-20261012.py',tile,nextpatch,'none','Continue16 native slots; next prepared. Internal/formal false; real visual and native seam QA pending.'])
 print(json.dumps({'selectedNativeSlots':len(list((B/tile/'native').glob('*.generation.json'))),'nextRequest':str(B/tile/'pipeline/prompts'/f'{nextpatch}.resumed-full64-v01.request.json'),'nextSeed':str(B/tile/'pipeline/guides'/f'{nextpatch}.resumed-full64-v01.continuity-seed.png')}))
else: print(json.dumps({'saved':patch,'tile':tile}))
