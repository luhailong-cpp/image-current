"""Export reviewed candidates with one fixed whole-canvas transform per direction.
No artwork, pose interpolation, mirroring, framewise fitting, or foot alignment.
"""
import hashlib,json,time
from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parents[2]/'combat-20260929'/'characters'/'00_reference_topright_boy'
RUN=ROOT.parents[2]/'run-correction-20260930'/'characters'/'00_reference_topright_boy'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.write-tmp')
    temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for attempt in range(5):
        try:
            temp.replace(p)
            return
        except OSError:
            if attempt==4: raise
            time.sleep(0.15*(attempt+1))
def main():
    transforms=read(ROOT/'export-settings.json')
    run_timing=read(ROOT/'run-timing.json')
    assert run_timing['cycleDurationMs']==960 and all(v==[60]*16 for v in run_timing['durationsByDirection'].values())
    selections=[]
    for seq in read(ROOT/'review/combat-reviewed.json')['sequences']:
        for f in seq['frames']:
            selections.append({'action':seq['action'],'direction':seq['direction'],'frame':f['slot'],'source':f['sourcePath'],'record':f['generationRecordPath'],'status':f['decision'],'observation':f['observation']})
    for f in read(ROOT/'review/cast-selection.json')['frames']:
        if not f.get('source'):continue
        records=[e['path'] for e in f.get('sourceEvidence',[]) if e['kind']=='generation_record']
        selections.append({'action':'cast','direction':f['direction'],'frame':f['frame'],'source':f['source'],'record':records[0] if records else None,'status':f['status'],'observation':f['continuityConclusion'],'evidence':f.get('sourceEvidence',[])})
    # Explicit reviewed selection only: never silently choose the largest version.
    additions=read(ROOT/'selected-new.json') if (ROOT/'selected-new.json').exists() else []
    for f in additions:
        relative=f['source'].replace('\\','/')
        if relative.startswith('generation/run/') and f['action']!='run':
            raise ValueError(f'Run source assigned to combat slot: {f}')
        if relative.startswith('generation/combat/') and relative.split('/')[2]!=f['action']:
            raise ValueError(f'Combat source action mismatch: {f}')
        p=ROOT/f['source']
        if not p.exists(): raise FileNotFoundError(p)
        selections=[old for old in selections if (old['action'],old['direction'],old['frame'])!=(f['action'],f['direction'],f['frame'])]
        selections.append({**f,'source':str(p),'record':str(p)+'.generation.json'})
    source_hash_slots={}
    for f in selections:
        key=(f['action'],f['direction'],f['frame']); source_hash=sha(f['source'])
        if source_hash in source_hash_slots:
            raise ValueError(f'Duplicate native source in distinct slots: {source_hash_slots[source_hash]} and {key}')
        source_hash_slots[source_hash]=key
    index={'schemaVersion':1,'character':'00_reference_topright_boy','status':'candidate_exports_not_runtime_approved','rootAnchor':[512,942],'frames':{}}
    manifest=[]
    for f in selections:
        src=Path(f['source']); meta=read(f['record']) if f.get('record') else {}
        transform=transforms['directions'].get(f['direction'],transforms['default'])
        scaled=tuple(transform['scaledCanvas']);offset=tuple(transform['offset'])
        with Image.open(src) as im:
            if im.mode!='RGBA' or im.size!=(1254,1254):raise ValueError(f'Unsupported native input {src}: {im.size} {im.mode}')
            # Preserve generated alpha; downsample whole canvas identically for all frames.
            tile=im.resize(scaled,Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(1024,1024),(0,0,0,0));canvas.alpha_composite(tile,offset)
        key=f"{f['action']}/{f['direction']}/{f['frame']:02d}.png";dst=ROOT/'frames'/key;dst.parent.mkdir(parents=True,exist_ok=True);canvas.save(dst)
        source_evidence=f.get('record') or str(ROOT/'review/cast-selection.json')
        row={'file':'frames/'+key,'sha256':sha(dst),'width':1024,'height':1024,'mode':'RGBA','nativeSourceSize':[1254,1254],'derivedAt':datetime.now(timezone(timedelta(hours=-4))).isoformat(),'timezone':'America/New_York','route':'derived','tool':'Pillow whole canvas fixed transform','configSnapshot':meta.get('configSnapshot'),'actualModel':meta.get('actualModel'),'actualQuality':meta.get('actualQuality'),'unverifiedReason':meta.get('unverifiedReason','历史回执未披露实际model/quality，保留未知，不以本轮配置补写。'),'derivedFrom':{'file':str(src),'sha256':sha(src),'generationRecord':f.get('record'),'evidence':f.get('evidence',[])},'operation':{'kind':'uniform_whole_canvas_downsample_fixed_direction_offset','nativeCanvas':[1254,1254],'scaledCanvas':list(scaled),'calibrationFile':'export-settings.json','calibrationStatus':transforms['status'],'nativeRoot':transform['nativeRoot'],'offset':list(offset),'alpha':'preserved','rootAnchor':[512,942],'framewiseFit':False,'mirrored':False,'interpolatedPose':False},'frameDurationMs':(run_timing['durationsByDirection'][f['direction']][f['frame']-1] if f['action']=='run' else {'hit':40,'attack':30,'cast':45}[f['action']]),'frameDurationStatus':('adopted_offline_960ms_client_pending' if f['action']=='run' else 'existing_combat_candidate_timing'),'visualStatus':f['status'],'observation':f['observation'],'sequenceVisualApproved':False,'clientIntegrated':False}
        write(Path(str(dst)+'.generation.json'),row)
        index['frames'][key]={'source_path':str(src),'source_kind':'single_frame','source_sha256':sha(src),'native_frame_size':[1254,1254],'evidence_path':source_evidence,'export_sha256':row['sha256'],'visual_status':f['status']}
        manifest.append(row)
    write(ROOT/'sources.json',index);write(ROOT/'manifest.json',{'status':('complete_candidate_exports_art_pending' if len(manifest)==196 else 'incomplete_candidate_exports'),'target':196,'candidateExports':len(manifest),'finalVisualApproved':0,'clientIntegrated':False,'runTiming':{**run_timing,'trials':'review/timing-grounding/review-data.json','finalAdopted':True,'adoptionScope':'offline_asset_timing_only'},'frames':manifest})
    print(json.dumps({'exports':len(manifest),'missing':196-len(manifest),'visualApproved':0}))
if __name__=='__main__':main()
