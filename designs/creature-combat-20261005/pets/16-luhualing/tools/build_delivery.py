"""Audit actual delivered frames and make honest previews; never creates poses."""
from pathlib import Path
import hashlib, json, math
from datetime import datetime, timezone
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPEC = {'hit': (6,40,3), 'attack': (12,30,7), 'cast': (16,45,11)}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    frames, errors, missing, groups = [], [], [], []
    review_path=ROOT/'visual-review.json'
    reviews=json.loads(review_path.read_text(encoding='utf-8')).get('frames',{}) if review_path.exists() else {}
    byte_seen, pixel_seen = {}, {}
    for action,(count,ms,event) in SPEC.items():
        for direction in ('E','W'):
            group = {'action':action, 'direction':direction, 'expected':count, 'durationMs':ms, 'files':[]}
            for number in range(1,count+1):
                rel = f'runtime/{action}/{direction}/{number:02}.png'
                path = ROOT/rel
                entry = {'file':rel, 'action':action, 'direction':direction, 'frame':number, 'durationMs':ms, 'pivot':[0.5,0.08], 'anchorTopLeft':[512,942], 'event': ('impact' if action=='hit' else 'release') if number==event else None, 'visualStatus':'not_reviewed', 'clientStatus':'not_integrated'}
                if not path.exists():
                    entry['status']='missing'
                    missing.append(rel)
                else:
                    with Image.open(path) as raw:
                        raw.load()
                        im=raw.convert('RGBA')
                        alpha=im.getchannel('A')
                        histogram=alpha.histogram()
                        bbox=alpha.getbbox()
                        pixelhash=hashlib.sha256(im.tobytes()).hexdigest()
                        entry.update({'status':'present', 'sha256':sha(path), 'pixelSHA256':pixelhash, 'width':raw.width, 'height':raw.height, 'mode':raw.mode, 'alpha':{'min':alpha.getextrema()[0], 'max':alpha.getextrema()[1], 'zeroPixels':histogram[0], 'partialPixels':sum(histogram[1:255]), 'opaquePixels':histogram[255], 'bbox':bbox}, 'format':raw.format})
                        if raw.size!=(1024,1024): errors.append(f'{rel}: size {raw.size}')
                        if raw.mode!='RGBA': errors.append(f'{rel}: mode {raw.mode}')
                        if not histogram[0] or not bbox: errors.append(f'{rel}: missing transparency or empty image')
                        if bbox and (bbox[0]==0 or bbox[1]==0 or bbox[2]==raw.width or bbox[3]==raw.height): errors.append(f'{rel}: alpha touches canvas edge; inspect crop')
                    for bank,key,label in ((byte_seen,entry['sha256'],'file'),(pixel_seen,pixelhash,'pixel')):
                        if key in bank: errors.append(f'{rel}: duplicate {label} of {bank[key]}')
                        else: bank[key]=rel
                    records=[path.with_suffix('.png.generation.json'), ROOT/f'records/{action}/{direction}/{number:02}.generation.json']
                    record=next((r for r in records if r.exists()),None)
                    if record:
                        entry['generationRecord']=record.relative_to(ROOT).as_posix()
                        entry['generationRecordSHA256']=sha(record)
                        metadata=json.loads(record.read_text(encoding='utf-8-sig'))
                        entry['actualModel']=metadata.get('actualModel')
                        entry['actualQuality']=metadata.get('actualQuality')
                    else: errors.append(f'{rel}: missing generation record')
                    review=reviews.get(rel,{})
                    if review.get('sha256')==entry['sha256']:
                        entry['visualStatus']=review.get('status','not_reviewed')
                        entry['visualReview']=review
                    group['files'].append(rel)
                frames.append(entry)
            groups.append(group)
    expected_paths={f['file'] for f in frames}
    for extra in (ROOT/'runtime').rglob('*.png'):
        if extra.relative_to(ROOT).as_posix() not in expected_paths:
            errors.append(f'Unexpected runtime image: {extra.relative_to(ROOT).as_posix()}')
    validation={'checkedAt':datetime.now(timezone.utc).isoformat(), 'expectedFrames':68, 'presentFrames':len(frames)-len(missing), 'missing':missing, 'errors':errors, 'technicalStatus':'passed' if not missing and not errors else 'incomplete_or_failed', 'visualStatus':'not_reviewed', 'dynamicStatus':'not_reviewed', 'clientStatus':'not_integrated', 'checks':['expected names/count','PNG decode','1024x1024 RGBA','nonempty transparent alpha','edge bounds','SHA256 file and pixel duplicates','generation records']}
    write_json(ROOT/'manifest.json', {'schemaVersion':1,'character':'露华灵','characterId':'16-luhualing','coordinateSystem':'1024x1024 top-left','transformPolicy':'one shared transform per direction; no per-frame bottom alignment','frames':frames,'groups':groups})
    validation['visualStatus']='passed_local_review' if len(frames)==68 and all(f.get('visualStatus')=='passed_local_review' for f in frames) else 'not_reviewed_or_incomplete'
    if review_path.exists():
        review_summary=json.loads(review_path.read_text(encoding='utf-8'))
        validation['dynamicStatus']=review_summary.get('dynamicStatus','not_reviewed')
        validation['reviewMethod']=review_summary.get('method')
    write_json(ROOT/'validation.json',validation)
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['file']}\n" for f in frames if f['status']=='present'),encoding='utf-8')
    make_previews(groups)
    print(json.dumps({k:validation[k] for k in ['expectedFrames','presentFrames','technicalStatus','errors']},ensure_ascii=False))

def make_previews(groups):
    preview=ROOT/'preview'
    preview.mkdir(exist_ok=True)
    for group in groups:
        files=group['files']
        if not files: continue
        columns=4; tile=320; label=28
        sheet=Image.new('RGB',(columns*tile,math.ceil(len(files)/columns)*(tile+label)), '#e5e5df')
        draw=ImageDraw.Draw(sheet)
        for i,rel in enumerate(files):
            im=Image.open(ROOT/rel).convert('RGBA'); im.thumbnail((tile,tile),Image.Resampling.LANCZOS)
            x=(i%columns)*tile; y=(i//columns)*(tile+label)
            sheet.paste(im,(x+(tile-im.width)//2,y+(tile-im.height)//2),im)
            draw.text((x+12,y+tile+7),f"{group['action']} {group['direction']} {Path(rel).stem}",fill='#203c38')
        sheet.save(preview/f"{group['action']}-{group['direction']}-contact.jpg",quality=92)
    data=json.dumps(groups,ensure_ascii=False)
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>露华灵 · 战斗动作逐帧预览</title>
<style>*{box-sizing:border-box}body{margin:0;background:#142c2a;color:#eee6cc;font:16px system-ui}header{padding:28px 32px;border-bottom:1px solid #6b785c}h1{margin:0 0 12px;font-size:28px}p{line-height:1.6;color:#cdd3c2}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:24px;padding:24px}article{padding:20px;border:1px solid #6b785c;border-radius:12px;background:#203d39}h2{margin:0 0 12px}.stage{aspect-ratio:1;background:repeating-conic-gradient(#dadbd5 0% 25%,#f0f0e9 0% 50%) 50%/32px 32px;border-radius:8px;position:relative}.stage img{width:100%;height:100%;object-fit:contain}.stage .empty[hidden]{display:none}.stage .empty{position:absolute;inset:0;display:grid;place-items:center;color:#44534a}button,select{background:#eee5cd;border:0;border-radius:5px;padding:8px 12px;margin:5px 3px 5px 0;color:#203d39;font:inherit}input{width:100%}.counter{font-variant-numeric:tabular-nums}.state{color:#d6c17c;font-size:14px}a{color:#d6c17c}</style>
<header><h1>露华灵 · 受击 / 普攻 / 施法</h1><p>E 斜前朝右下 · W 斜后朝左上。播放使用已落盘的真实帧。原时间 / 0.25×慢放 / 逐帧可切换。</p><p id="total"></p></header><main></main><script>
const groups=__DATA__;
document.querySelector('#total').textContent=`已落盘 ${groups.reduce((n,g)=>n+g.files.length,0)} / 68 帧。动态与客户端验收状态以 STATUS.md 为准。`;
for(const g of groups){const a=document.createElement('article');a.innerHTML=`<h2>${({hit:'受击',attack:'普攻',cast:'施法'})[g.action]} · ${g.direction}</h2><div class="stage"><img alt="${g.action} ${g.direction}" hidden><span class="empty">当前尚无生成帧</span></div><p class="state">${g.files.length}/${g.expected} 帧 · 每帧 ${g.durationMs}ms</p><div><button class="play">播放</button><select aria-label="播放速度"><option value="1">正常 1×</option><option value="0.25">慢放 0.25×</option></select><button class="prev">上一帧</button><button class="next">下一帧</button></div><input type="range" min="0" max="${Math.max(0,g.files.length-1)}" value="0" aria-label="逐帧"><p class="counter">—</p>`;document.querySelector('main').append(a);const img=a.querySelector('img'),slider=a.querySelector('input'),count=a.querySelector('.counter'),play=a.querySelector('.play'),speed=a.querySelector('select');let index=0,running=false,timer=null;const cache=g.files.map(src=>{const im=new Image();im.src='../'+src;return im});function show(){if(!g.files.length)return;img.hidden=false;a.querySelector('.empty').hidden=true;img.src=cache[index].src;slider.value=index;count.textContent=`${index+1} / ${g.files.length} · ${g.files[index]}`;}function stop(){running=false;clearTimeout(timer);play.textContent='播放'}function tick(){if(!running)return;index=(index+1)%g.files.length;show();timer=setTimeout(tick,g.durationMs/Number(speed.value))}play.onclick=()=>{if(!g.files.length)return;if(running)stop();else{running=true;play.textContent='暂停';timer=setTimeout(tick,g.durationMs/Number(speed.value))}};a.querySelector('.prev').onclick=()=>{stop();index=(index+g.files.length-1)%g.files.length;show()};a.querySelector('.next').onclick=()=>{stop();index=(index+1)%g.files.length;show()};slider.oninput=()=>{stop();index=Number(slider.value);show()};show()}
</script></html>'''.replace('__DATA__',data)
    (preview/'index.html').write_text(html,encoding='utf-8')

if __name__=='__main__': main()
