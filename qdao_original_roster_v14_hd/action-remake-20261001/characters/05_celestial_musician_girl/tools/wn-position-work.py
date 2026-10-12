from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'provenance/ground-contact-20261004'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def source(d,f):
    rel=f'final/run/{d}/{f:02}.png'; p=ROOT/rel; m=read(ROOT/(rel+'.generation.json'))
    r=read(ROOT/m['sourceGeneration']['evidence']['result'])
    if r.get('rawToolResult'): r=json.loads(r['rawToolResult'])
    host=r.get('artifactPath') or re.search(r'as (C:\\[^\r\n]+?\.png) by default',r['output_hint'])[1]
    assert sha(Path(host))==m['source']['sha256'],host
    return {'file':rel,'sha256':sha(p),'generationRecord':rel+'.generation.json','generationRecordSha256':sha(ROOT/(rel+'.generation.json')),'nativeHostFile':host,'nativeSha256':m['source']['sha256'],'nativeGenerationRecord':m['nativeSourceRecord']}
def initialize():
    mapping={1:16,2:1,3:2,4:3,5:3,6:3,7:4,8:4,9:8,10:9,11:10,12:11,13:11,14:11,15:12,16:12}
    rows=[]
    for d in ['W','N']:
      for target,old in mapping.items():
        phase=['front_initial_contact','front_accept_load','early_stance_a','early_stance_b','late_stance_under_hip','late_stance_slightly_behind','rear_forefoot_push_a','rear_forefoot_push_b'][(target-1)%8]
        edit=target in [5,6,8,13,14,16] or (d=='W' and target==1)
        s=source(d,old)
        note='真实姿态保留并重排；来源随图，不重编号历史。'
        if edit: note='独立 AI 编辑补真实负重/蹬地姿态；不能平移整图或复制一张用于两槽。'
        if d=='W' and target==1: note='原16前脚尚未清楚接地；需下沉/转踝为右远腿初触，保持上身。'
        if target in [7,15]: note='原04/12后腿伸展、鞋跟抬起的前掌蹬地姿态；整段配对后再复核，不把露底误等同腾空。'
        rows.append({'action':'run','direction':d,'targetFrame':target,'sourceFrame':old,'mode':'new_edit' if edit else 'reuse','source':s,'phase':phase,'supportLeg':'RIGHT' if target<=8 else 'LEFT','status':'needs_generation' if edit else 'provisional_reuse_reviewed','notes':note})
    doc={'createdAt':datetime.now(timezone.utc).isoformat(),'requirement':'每只脚连续8帧：前方2/早承重2/髋下到略后2/后侧前掌蹬地2；16×75ms=1200ms均匀。','sourceFinalSelectionSha256':sha(ROOT/'final-selection.json'),'globalScale':0.65,'targetRoot':[512,942],'sourceRoots':{'W':[565,1202],'N':[645,1180]},'prohibition':['no duplicate image for distinct slots','no whole-image translation to fake contact','no per-frame bbox/min-foot registration','no final/manifest/selection modification'],'visualBasis':'实际看W/N整圈表与W04/12、N04/12原生图；复用原16/01/02/03及08/09/10/11，原04/12蹬地进入07/15；W原16另补明确初触。晚承重与更晚蹬地缺独立姿态，必须新编辑。','rows':rows}
    save(OUT/'WN-position-plan.json',doc)
    print(json.dumps({'path':str(OUT/'WN-position-plan.json'),'reuse':sum(x['mode']=='reuse' for x in rows),'edit':sum(x['mode']=='new_edit' for x in rows)}))
    save(OUT/'WN-source-snapshot.json',[{'direction':d,'frame':f,**source(d,f)} for d in ['W','N'] for f in range(1,17)])
def selection():
    plan=read(OUT/'WN-position-plan.json')
    versions={'W':{1:6,5:2,6:2,7:3,8:3,13:2,14:2,16:4},'N':{5:2,6:2,8:4,13:2,14:2,16:2}}
    notes=['前方初触，鞋掌沿行进向接受负荷。','同脚前方接受负荷，膝部进入缓冲。','支撑脚早承重，身体经过该脚。','同脚经过到支撑中段，自由腿前摆。','同脚髋下晚承重，膝伸展而鞋掌仍负重。','支撑移到略后，重心转到前掌而非整脚腾空。','后侧抬跟前掌蹬地，自由腿向下次接触推进。','同脚第二张后蹬；另一脚进入下一半圈落地过渡。']
    rows=[]
    for p in plan['rows']:
        d,t=p['direction'],p['targetFrame'];v=versions[d].get(t)
        f=f'staging/run/{d}/ground-{t:02}-v{v}.png' if v else p['source']['file']
        if not (ROOT/f).exists(): raise FileNotFoundError(f)
        rec=f+'.generation.json';m=read(ROOT/rec)
        rows.append({'action':'run','direction':d,'targetFrame':t,'sourceFile':f,'sourceGenerationRecord':rec,'sha256':sha(ROOT/f),'sourceGenerationRecordSha256':sha(ROOT/rec),'nativeSha256':m['source']['sha256'],'supportLeg':'RIGHT' if t<=8 else 'LEFT','positionSegment':((t-1)%8)//2+1,'pairOrdinal':(t-1)%2+1,'phase':p['phase'],'visualNotes':notes[(t-1)%8]+(' W侧视近LEFT/远RIGHT腿属按裤腿遮挡追踪。' if d=='W' else ' N背视脚尖沿北向，屏左右即解剖左右，保留前后深度投影。'),'visualStatus':'candidate_pending_sequence_review','sourceFinalAtStart':p['source']['file'],'sourceFinalAtStartSha256':p['source']['sha256'],'operation':'independent_builtin_AI_edit_then_fixed_registration' if v else 'byte_exact_reuse_reordered_with_lineage','durationMs':75,'globalScale':0.65,'sourceRoot':plan['sourceRoots'][d],'targetRoot':[512,942],'clientValidated':False})
    assert len(rows)==32 and len({r['sourceFile'] for r in rows})==32 and len({r['sha256'] for r in rows})==32
    save(OUT/'position-selection-WN.json',rows)
    for d in ['W','N']:
      seq=[r for r in rows if r['direction']==d]
      for detail in [False,True]:
        cellw,cellh=(400,424) if not detail else (400,190)
        canvas=Image.new('RGB',(cellw*4,cellh*4),(207,218,224));draw=ImageDraw.Draw(canvas)
        for i,r in enumerate(seq):
          im=Image.open(ROOT/r['sourceFile']).convert('RGBA')
          if detail: im=im.crop((160,710,860,1000)); im.thumbnail((400,164),Image.Resampling.LANCZOS)
          else: im.thumbnail((400,400),Image.Resampling.LANCZOS)
          x=(i%4)*cellw;y=(i//4)*cellh;canvas.paste(im,(x,y),im)
          draw.text((x+4,y+cellh-22),f"{d}{r['targetFrame']:02} {r['supportLeg']} S{r['positionSegment']}.{r['pairOrdinal']}",fill=(15,25,30))
        canvas.save(OUT/f"WN-position-{d}-{'legs' if detail else 'full'}.jpg",quality=95)
    print(json.dumps({'count':len(rows),'uniqueHashes':32,'selection':str(OUT/'position-selection-WN.json'),'new':sum(r['operation'].startswith('independent') for r in rows)}))
if __name__=='__main__':
  if sys.argv[1]=='init': initialize()
  if sys.argv[1]=='selection': selection()

