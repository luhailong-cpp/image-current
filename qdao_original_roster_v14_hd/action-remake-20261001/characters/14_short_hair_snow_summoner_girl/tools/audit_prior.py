"""Read-only prior-asset audit; outputs only this character's audit/ directory."""
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime, timezone
import hashlib, json, os

ROOT = Path('D:/work/image')
OUT = ROOT / 'qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl/audit'
OLD = ROOT / 'qdao_original_roster_v14_hd/recovery-20260921/14-delivery-preview'
COMBAT = ROOT / 'qdao_original_roster_v14_hd/combat-20260929/characters/14_short_hair_snow_summoner_girl'
RUN = ROOT / 'qdao_original_roster_v14_hd/run-correction-20260930/characters/14_short_hair_snow_summoner_girl'
OUT.mkdir(parents=True, exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {}
entries=[]
for category, base in [('legacy_movement', OLD / 'assets'), ('prior_combat',COMBAT), ('prior_run_correction',RUN)]:
    for p in sorted(base.rglob('*.png')):
        im=Image.open(p)
        recpath=Path(str(p)+'.generation.json') if category=='legacy_movement' else COMBAT/'provenance/receipts'/f'{p.stem}.json'
        rec=load(recpath)
        a=im.getchannel('A') if im.mode=='RGBA' else None
        alpha8=a.point(lambda v:255 if v>8 else 0).getbbox() if a else None
        entry={'category':category,'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'size':list(im.size),'mode':im.mode,'alphaExtrema':list(a.getextrema()) if a else None,'alphaGt8BBox':alpha8,'lowestAlphaGt8Y':alpha8[3]-1 if alpha8 else None,'sourceRecord':recpath.relative_to(ROOT).as_posix() if recpath.exists() else None,'sourceRecordSHA256':sha(recpath) if recpath.exists() else None,'recordedImageShaMatches':rec.get('sha256')==sha(p) if rec else None,'originalNativeSize':rec.get('nativeSize') or [rec.get('width'),rec.get('height')],'sourceArchive':rec.get('sourceArchive'),'originalSourceSHA256':rec.get('derivedFrom',{}).get('sha256'),'configTarget':rec.get('configSnapshot'),'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'submittedParameters':rec.get('submittedParameters'),'legacyOperation':rec.get('operation'),'legacyReview':rec.get('visualReview') or rec.get('review'),'countedAsNewProduction':False,'runApprovedByThisAudit':False}
        entries.append(entry)
summary={c:sum(e['category']==c for e in entries) for c in ['legacy_movement','prior_combat','prior_run_correction']}
summary.update({'legacyWalk':128,'legacyIdle':8,'combatCandidateSlots':2,'combatRuntimeFrames':0,'runAcceptedByAudit':0,'targetFrames':196})
doc={'schema_version':1,'character':'14_short_hair_snow_summoner_girl','auditedAtUtc':datetime.now(timezone.utc).isoformat(),'userFacingDate':'2026-10-02 America/New_York','scope':'Existing local committed baseline, read-only; does not include action-remake new production.','summary':summary,'entries':entries}
(OUT/'inventory.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')

def sheet(paths,name,cols=4,cell=300):
    canvas=Image.new('RGB',(cols*cell,((len(paths)+cols-1)//cols)*(cell+26)),(35,43,57))
    draw=ImageDraw.Draw(canvas)
    for i,p in enumerate(paths):
        x=(i%cols)*cell; y=(i//cols)*(cell+26)
        im=Image.open(p).convert('RGBA'); im.thumbnail((cell,cell))
        canvas.paste(im,(x+(cell-im.width)//2,y),im)
        draw.text((x+10,y+cell+5),p.parent.name+'/'+p.stem,fill=(240,240,240))
    canvas.save(OUT/name)
for direction in ['E','W','N','NE','SE','S','SW','NW']:
    sheet(sorted((OLD/'assets/walk'/direction).glob('*.png')),f'walk-{direction}-audit.jpg')
sheet([OLD/'assets/idle/E.png',COMBAT/'staging/hit-E-01-v1.png',COMBAT/'staging/hit-E-03-v4.png',OLD/'assets/idle/W.png'],'combat-audit.jpg',4,400)
print(json.dumps(summary))

groups={}
for direction in ['E','W','N','NE','SE','S','SW','NW']:
    groups['old-walk-'+direction]=[{'label':p.parent.name+'/'+p.stem,'src':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p)} for p in sorted((OLD/'assets/walk'/direction).glob('*.png'))]
groups['old-hit-E-incomplete']=[{'label':p.stem,'src':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p)} for p in sorted((COMBAT/'staging').glob('*.png'))]
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>14 旧动作只读审图</title>
<style>body{font:16px system-ui;background:#18212d;color:#e9edf5;margin:24px}button,select,input{font:inherit;margin:5px;padding:6px}a{color:#9de1ff}#stage{width:min(512px,90vw);background:#232b39;border:1px solid #8492a5}#stage.light{background:#edf0f5}#stage img{width:100%;display:block}#grid{display:flex;flex-wrap:wrap}figure{margin:7px;padding:5px;background:#232b39;cursor:pointer}figure img{width:180px}code{font-size:12px;overflow-wrap:anywhere}small{color:#ffd7a0}</style>
<h1>14 唤雪少女 · 旧动作只读审图</h1><p>旧 walk 不是本批跑步完成品；hit 只有 E01/E03 两张候选。本页不写图片，不补槽，不计作新帧。</p><p><a href="PRIOR_AUDIT.md">审核结论</a> · <a href="inventory.json">138 张实际图片与来源 SHA</a></p>
<select id="group"></select><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="30">正常 30 ms</option><option value="120">慢速 120 ms</option><option value="500">慢速 500 ms</option></select><button id="bg">切换底色</button><br><small>战斗候选组不代表完整动画，只有 01 与 03；跳帧连播用于姿态对比。</small><p id="info"></p><div id="stage"><img id="active"></div><code id="hash"></code><div id="grid"></div>
<script>const groups=__DATA__;let selected=Object.keys(groups)[0],i=0,playing=true,last=0;const sel=document.querySelector('#group'),active=document.querySelector('#active'),info=document.querySelector('#info');for(const k of Object.keys(groups)){const o=document.createElement('option');o.value=k;o.textContent=k;sel.append(o)}function show(){const f=groups[selected][i];active.src=f.src;info.textContent=selected+' — '+f.label+' ('+(i+1)+'/'+groups[selected].length+')';document.querySelector('#hash').textContent='SHA256 '+f.sha256}function grid(){document.querySelector('#grid').replaceChildren();groups[selected].forEach((f,n)=>{const fig=document.createElement('figure'),im=document.createElement('img'),cap=document.createElement('figcaption');im.src=f.src;cap.textContent=f.label;fig.append(im,cap);fig.onclick=()=>{playing=false;i=n;show();document.querySelector('#play').textContent='播放'};document.querySelector('#grid').append(fig)})}function step(d){playing=false;i=(i+d+groups[selected].length)%groups[selected].length;show();document.querySelector('#play').textContent='播放'}sel.onchange=()=>{selected=sel.value;i=0;show();grid()};document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);document.querySelector('#play').onclick=()=>{playing=!playing;document.querySelector('#play').textContent=playing?'暂停':'播放'};document.querySelector('#bg').onclick=()=>document.querySelector('#stage').classList.toggle('light');function loop(t){if(playing&&t-last>=Number(document.querySelector('#speed').value)){i=(i+1)%groups[selected].length;show();last=t}requestAnimationFrame(loop)}show();grid();requestAnimationFrame(loop);</script></html>'''.replace('__DATA__',json.dumps(groups,ensure_ascii=False))
(OUT/'index.html').write_text(html,encoding='utf-8')
derivations=[]
for p in sorted(OUT.glob('*-audit.jpg')):
    sources=[e for e in entries if '/walk/'+p.stem.split('-')[1]+'/' in e['path']] if p.name.startswith('walk-') else [e for e in entries if e['category']=='prior_combat' or e['path'].endswith('idle/E.png') or e['path'].endswith('idle/W.png')]
    derivations.append({'file':p.name,'sha256':sha(p),'use':'audit-only contact sheet; never a runtime or generation source','operation':'Pillow proportional thumbnail and compositing onto labeled dark sheet','sources':[{'path':e['path'],'sha256':e['sha256']} for e in sources]})
(OUT/'contact-sheets.provenance.json').write_text(json.dumps(derivations,ensure_ascii=False,indent=2),encoding='utf-8')
