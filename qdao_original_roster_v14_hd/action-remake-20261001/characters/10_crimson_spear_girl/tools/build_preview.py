from pathlib import Path
import json, re, hashlib, copy
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'delivery-current.json').exists():
    import runpy
    runpy.run_path(str(ROOT/'tools/build_current_player.py'),run_name='__main__')
    raise SystemExit(0)
preview=ROOT/'preview';preview.mkdir(exist_ok=True)
groups={}
for p in ROOT.rglob('*.png'):
    if any(s in p.parts for s in ['preview','export','rejected','superseded','archive']): continue
    if p.name=='native.png':
        m=re.fullmatch(r'run-([A-Z]+)-(\d+)(?:-v\d+)?',p.parent.name)
        if not m: continue
        action='run';direction=m[1];frame=int(m[2])
    else:
        m=re.fullmatch(r'(run|hit|attack|cast)-([A-Z]+)-(\d+)(?:-v\d+)?\.png',p.name)
        if not m: continue
        action,direction,frame=m[1],m[2],int(m[3])
    items=groups.setdefault(f'{action}/{direction}',[])
    existing=next((f for f in items if f['frame']==frame),None)
    if existing:
        if existing['path'].stat().st_mtime>=p.stat().st_mtime: continue
        items.remove(existing)
    items.append({'frame':frame,'url':'../'+p.relative_to(ROOT).as_posix(),'path':p})
selection_file=ROOT/'source-selection.json'
selected_sources=json.loads(selection_file.read_text(encoding='utf-8'))['slots'] if selection_file.exists() else {}
for private_selection in ['run-E-grounding-work/selection.json','run-W-work/selection.json','grounding-SE-work/selection.json','run-NE-work/selection.json','run-NW-work/selection.json','run-SW-work/selection.json','run-SW-first-work/selection.json']:
    source_file=ROOT/private_selection
    if source_file.exists():
        private_data=json.loads(source_file.read_text(encoding='utf-8-sig'))
        selected_sources.update(private_data.get('slots',{}))
        for entry in private_data.get('entries',[]):
            match=re.fullmatch(r'(run|hit|attack|cast)-([A-Z]+)-(\d+)',entry.get('slot',''))
            if match:
                entry_path=Path(entry.get('absolutePath') or source_file.parent/entry['path']).resolve()
                selected_sources[f'{match[1]}/{match[2]}/{int(match[3]):02}']=entry_path.relative_to(ROOT.resolve()).as_posix()
        if private_data.get('pendingSlots') and private_data.get('direction'):
            pending=set(private_data['pendingSlots']);key='run/'+private_data['direction']
            if key in groups: groups[key][:]=[f for f in groups[key] if f['frame'] not in pending]
attack_selection=ROOT/'attack-work/selection.json'
if attack_selection.exists():
    attack_rows=json.loads(attack_selection.read_text(encoding='utf-8-sig'))
    if 'slots' in attack_rows: selected_sources.update(attack_rows['slots'])
    else:
        for direction,rows in attack_rows.items():
            for frame,filename in rows.items(): selected_sources[f'attack/{direction}/{int(frame):02}']='attack-work/'+filename
attack_ground_selection=ROOT/'attack-W-grounding-work/selection.json'
if attack_ground_selection.exists():
    selected_sources.update(json.loads(attack_ground_selection.read_text(encoding='utf-8-sig')).get('slots',{}))
if selected_sources:
    remapped_paths={str((ROOT/source).resolve()):slot for slot,source in selected_sources.items()}
    for group,items in groups.items():
        items[:]=[f for f in items if str(f['path'].resolve()) not in remapped_paths or remapped_paths[str(f['path'].resolve())]==f"{group}/{f['frame']:02}" or f"{group}/{f['frame']:02}" in selected_sources]
    for slot,source in selected_sources.items():
        action,direction,number=slot.split('/');group=f'{action}/{direction}';frame=int(number)
        p=ROOT/source
        if not p.exists(): raise FileNotFoundError(f'Selected source missing: {source}')
        items=groups.setdefault(group,[])
        items[:]=[f for f in items if f['frame']!=frame]
        items.append({'frame':frame,'url':'../'+p.relative_to(ROOT).as_posix(),'path':p,'selectionBasis':'explicit reviewed source assignment; source filename need not equal assigned frame'})
manifest={'character':'10_crimson_spear_girl','status':'in_progress','expected':196,'producedNative':sum(map(len,groups.values())),'clientIntegrated':False,'root':[512,942],'groups':{}}
for group,frames in groups.items():
    frames.sort(key=lambda x:x['frame'])
    cols=4;rows=(len(frames)+cols-1)//cols
    sheet=Image.new('RGB',(cols*280,rows*304),'#e9e8e1');draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(frames):
        im=Image.open(f['path']);f['nativeSize']=list(im.size);f['sha256']=hashlib.sha256(f['path'].read_bytes()).hexdigest()
        im.thumbnail((280,280));x=i%cols*280;y=i//cols*304
        sheet.paste(im,(x,y),im if im.mode=='RGBA' else None)
        draw.text((x+6,y+282),f'{group} {f["frame"]:02} - CANDIDATE',fill='#222')
        del f['path']
    sheet_path=preview/(group.replace('/','-')+'-contact.jpg')
    sheet.save(sheet_path,quality=94)
    derived={'file':sheet_path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(sheet_path.read_bytes()).hexdigest(),'operation':'preview-only full-canvas thumbnail composition; no pose generation','derivedFrom':[{'file':f['url'][3:],'sha256':f['sha256'],'generationRecord':f['url'][3:]+'.generation.json'} for f in frames]}
    Path(str(sheet_path)+'.generation.json').write_text(json.dumps(derived,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest['groups'][group]=frames
(ROOT/'candidate-inventory.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
display_data=copy.deepcopy(manifest)
proposal_path=ROOT/'run-playback-proposals.json'
if proposal_path.exists():
    proposals=json.loads(proposal_path.read_text(encoding='utf-8-sig'))
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
data=json.dumps(display_data,ensure_ascii=False)
import runpy
runpy.run_path(str(ROOT/'tools/build_current_player.py'),run_name='__main__')
print(json.dumps({'produced':manifest['producedNative'],'groups':{k:len(v) for k,v in groups.items()}},ensure_ascii=False))
