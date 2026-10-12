from pathlib import Path
p=Path(__file__).resolve().parent/'build_preview.py'
t=p.read_text(encoding='utf-8')
t=t.replace("import json, re, hashlib","import json, re, hashlib, copy")
old="data=json.dumps(manifest,ensure_ascii=False)"
new="""display_data=copy.deepcopy(manifest)
proposal_path=ROOT/'run-playback-proposals.json'
if proposal_path.exists():
    proposals=json.loads(proposal_path.read_text(encoding='utf-8'))
    for group,order in proposals.get('groups',{}).items():
        frames=display_data['groups'].get(group,[])
        frames.sort(key=lambda f:order.index(f['frame']) if f['frame'] in order else len(order)+f['frame'])
        for f in frames:f['trialOrder']=True
for group,frames in display_data['groups'].items():
    for f in frames:
        candidate=ROOT/'candidate'/group/f"{f['frame']:02}.png"
        metadata=Path(str(candidate)+'.generation.json')
        if candidate.exists() and metadata.exists():
            m=json.loads(metadata.read_text(encoding='utf-8'))
            if any(x.get('sha256')==f['sha256'] for x in m.get('derivedFrom',[])):
                f['candidateUrl']='../'+candidate.relative_to(ROOT).as_posix()
data=json.dumps(display_data,ensure_ascii=False)"""
assert old in t
t=t.replace(old,new)
t=t.replace('<select id="group"></select>','<select id="group"></select><select id="render"><option value="native">原生整画布</option><option value="candidate">1024临时注册</option></select>')
t=t.replace("function load(){last=", "function url(f){return document.querySelector('#render').value==='candidate'&&f.candidateUrl?f.candidateUrl:f.url}function load(){last=")
t=t.replace('im.src=f.url;im.onload=draw;images[f.url]=im','im.src=url(f);im.onload=draw;images[url(f)]=im')
t=t.replace("const im=images[f.url]","const im=images[url(f)]")
t=t.replace("g.value+' / '+String(f.frame).padStart(2,'0')+' / 原生 '+f.nativeSize.join('×')","g.value+' / 播放位 '+(idx+1)+' / 来源帧 '+String(f.frame).padStart(2,'0')+(f.trialOrder?'（试排）':'')+' / '+(url(f)===f.candidateUrl?'1024临时注册':'原生 '+f.nativeSize.join('×'))")
t=t.replace("g.onchange=load;","g.onchange=load;document.querySelector('#render').onchange=load;")
p.write_text(t,encoding='utf-8')
print('preview updated')

