from native_work import *
for p in (ZONE/'native').glob('*.png.generation.json'):
    rec=read(p)
    for ref in rec['references']:
        rp=Path(ref['file'])
        gp=rp.with_suffix('.png.generation.json'); dp=rp.with_suffix('.png.derivation.json')
        if gp.exists(): ref['generationRecord']=gp.as_posix()
        if dp.exists():
            ref['derivationRecord']=dp.as_posix()
            deriv=read(dp)
            if deriv.get('base',{}).get('native'):
                ref['role']='edit target: existing native artwork with exact upper-neighbor native230px strip reinserted; no blurry layout region'
                base=Path(deriv['base']['file']); deriv['base']['generationRecord']=base.with_suffix('.png.generation.json').as_posix(); write(dp,deriv)
    if rec['id'] in ['r03_c12_p01_02','r03_c12_p02_01','r03_c12_p02_02','r03_c12_p02_04','r03_c12_p03_03','r03_c12_p03_04']:
        rec['status']='rejected_superseded_by_repair'; rec['supersededBy']=(ZONE/'native'/f"{rec['id']}_v2.png.generation.json").as_posix()
    write(p,rec)
    inputs=ZONE/'prompts'/f"{rec['id']}.inputs.json"
    if inputs.exists(): write(inputs,rec['references'])
    receipt=Path(rec['evidence']['receipt']); rr=read(receipt); rr['prompt']=rec['prompt']; rr['promptSha256']=sha(rec['prompt']); write(receipt,rr)
err=ZONE/'receipts/r03_c12_p02_02.attempt01-error.json'; rr=read(err); rr['references']=[]
for i,ref in enumerate(rr['referenced_image_paths']):
    rr['references'].append({'file':ref,'sha256':sha(ref),'role':['coordinate guide with native anchors','upper native neighbor','left native neighbor','sole layout authority','independent material style','primary approved Daoist Q style'][i]})
write(err,rr)
print('Provenance links, prompt hashes and superseded states updated.')
