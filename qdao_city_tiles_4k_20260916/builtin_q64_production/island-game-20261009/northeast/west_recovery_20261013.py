"""Scoped r04_c10 recovery bookkeeping and policy verification; no artwork drawing."""
from native_work import *
import sys

WORKER='west_recovery_20261013'
def border(side,neighbor):
    selection=read(ZONE/'selection-r04_c10.json');current=read(selection['derivationPath'])
    ns=read(ZONE/f'selection-{neighbor}.json');np=Path(ns.get('candidatePath',ZONE/'tiles'/f'{neighbor}.png'))
    othermeta=read(np.with_suffix('.png.derivation.json'))
    im=Image.open(current['file']);other=Image.open(othermeta['file'])
    assert im.size==other.size==(4096,4096)
    assert sha(current['file'])==current['sha256'] and sha(othermeta['file'])==othermeta['sha256']
    aw,bw=current['worldBox'],othermeta['worldBox'];paths=[]
    for i in range(4):
        if side=='north':
            assert bw[3]==aw[1] and aw[0]==bw[0]
            out=Image.new('RGB',(1024,512));out.paste(other.crop((i*1024,3840,(i+1)*1024,4096)),(0,0));out.paste(im.crop((i*1024,0,(i+1)*1024,256)),(0,256))
        elif side=='east':
            assert aw[2]==bw[0] and aw[1]==bw[1]
            out=Image.new('RGB',(512,1024));out.paste(im.crop((3840,i*1024,4096,(i+1)*1024)),(0,0));out.paste(other.crop((0,i*1024,256,(i+1)*1024)),(256,0))
        else:raise ValueError(side)
        path=ZONE/'qa'/f'r04_c10-west-recovery-{side}-segment-{i+1}-100pct.png'
        assert not path.exists();out.save(path);paths.append(path.as_posix())
    record={'tileId':'r04_c10','neighbor':neighbor,'side':side,'sources':[{'file':r['file'],'sha256':r['sha256']} for r in (current,othermeta)],'segments':paths,'inspectionScale':1,'operation':'Exact 1:1 final candidate edges, no resampling or blending','status':'pending_visual_review'}
    write(ZONE/'qa'/f'r04_c10-west-recovery-{side}-border.json',record)
    print(json.dumps(record))
def checkpoint(current=None,status='local_native_production',error=None):
    selection=read(ZONE/'selection-r04_c10.json')
    picked=[v for row in selection['cores'] for v in row if v]
    missing=[f'r04_c10_p{r+1:02}_{c+1:02}' for r,row in enumerate(selection['cores']) for c,v in enumerate(row) if not v]
    record={'worker':WORKER,'tileId':'r04_c10','updatedAtUtc':now(),'status':status,'selectedCoreCount':len(picked),'requiredCoreCount':16,'selected':picked,'missing':missing,'currentPatch':current,'actualModel':None,'actualQuality':None,'generationRoute':'builtin image_gen.imagegen','formalAccepted':False,'error':error}
    write(ZONE/'qa'/'west-recovery-checkpoint-20261013.json',record)
    return record

def preflight(ident):
    assert ident.startswith('r04_c10_p')
    policy=ROOT/'AGENTS.md';split=ROOT/'docs'/'MAP_PARALLEL_SPLIT_20261013.json'
    policytext=policy.read_text(encoding='utf-8-sig');allocation=read(split)
    assert '允许继续使用现有内置绘图工具' in policytext
    for batch in allocation['batches']:
        assert not (batch.get('status')=='allocated_root_reserved' and batch.get('map')=='island-game-20261009' and 'r04_c10' in batch['tiles']), 'Coordinate now transferred; stop before generating'
    assert not (ZONE/'native'/f'{ident}.png').exists(), 'Native already saved; recover instead'
    refs=read(ZONE/'prompts'/f'{ident}.inputs.json')
    for ref in refs: assert sha(ref['file'])==ref['sha256']
    check={'readAtUtc':now(),'rootInstructionsSha256':sha(policy),'allocationSha256':sha(split),'allocatedElsewhere':[t for batch in allocation['batches'] if batch.get('map')=='island-game-20261009' and batch.get('status')=='allocated_root_reserved' for t in batch['tiles']],'currentCoordinate':'r04_c10','ownershipCheck':'allowed original NE owner coordinate'}
    write(ZONE/'receipts'/f'{ident}.preflight.json',check)
    checkpoint(ident,'prepared_for_builtin_generation')
    print(json.dumps({'prompt':(ZONE/'prompts'/f'{ident}.prompt.txt').read_text(encoding='utf-8-sig'),'references':[r['file'] for r in refs],'preflight':check},ensure_ascii=False))

if __name__=='__main__':
    if sys.argv[1]=='preflight':preflight(sys.argv[2])
    elif sys.argv[1]=='checkpoint':print(json.dumps(checkpoint(sys.argv[2] if len(sys.argv)>2 else None),ensure_ascii=False))
    elif sys.argv[1]=='border':border(sys.argv[2],sys.argv[3])
