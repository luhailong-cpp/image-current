import json,hashlib,datetime,argparse
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('direction',choices=['N','W']);a=p.parse_args();d=a.direction
iv=json.loads((R/'inventory-run-north.json').read_text(encoding='utf-8-sig'))
rows=[];errors=[]
for n in range(1,17):
    p=R/f'frames/run/{d}/{n:02}.png';im=Image.open(p);sha=hashlib.sha256(p.read_bytes()).hexdigest()
    entry=next(x for x in iv['frames'] if x['direction']==d and x['frame']==n)
    rec=json.loads((R/entry['native_evidence']).read_text(encoding='utf-8-sig'))
    if sha!=entry['sha256'] or im.size!=(1024,1024) or im.mode!='RGBA':errors.append(n)
    prompt=R/rec.get('prompt','missing')
    if not prompt.is_file() and rec.get('candidateKey'):
        req=json.loads((R/'records'/f'{rec["candidateKey"]}.request.json').read_text(encoding='utf-8-sig'))
        prompt.write_text(req['prompt'],encoding='utf-8')
    rows.append({'frame':n,'path':str(p.relative_to(R)).replace('\\','/'),'sha256':sha,'sourceRecord':entry['native_evidence'],'supportFoot':'anatomical_RIGHT' if n<=8 else 'anatomical_LEFT','pairPosition':((n-1)%8)//2+1,'pairHalf':((n-1)%2)+1,'durationMs':75,'visualReview':'actual_single_frame_and_contact_sheet_review','observations':'后跟及鞋缘显形，同脚连续承重；远近透视下后移与关节弯曲渐进，不以整鞋底朝镜头代替接地。' if d=='N' else '鞋长轴朝西，连续同脚从中间支撑到后端推进，反向手臂摆动保留右符左铃。'})
report={'direction':d,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'current formal pixels, actual visual contact-sheet review; browser dynamic review delegated to root','sameFootGroups':{'RIGHT':[1,2,3,4,5,6,7,8],'LEFT':[9,10,11,12,13,14,15,16]},'pairs':[[n,n+1] for n in range(1,17,2)],'frameMs':75,'cycleMs':1200,'nativeSizes':sorted(set(tuple(x['native_size']) for x in iv['frames'] if x['direction']==d)),'actualModel':None,'actualQuality':None,'clientStatus':'not_integrated','technicalErrors':errors,'frames':rows,'staticReviewEvidence':f'work/run-{d}/contact-current.png','dynamicPreview':f'work/run-{d}/preview.html','gif':f'work/run-{d}/run-{d}-normal.gif','dynamicStatus':'pending_root_browser_review'}
(R/f'reviews/finish-north-{d}-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'direction':d,'frames':len(rows),'technicalErrors':errors}))
