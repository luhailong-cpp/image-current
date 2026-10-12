from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys
import numpy as np
from PIL import Image

Q=Path(__file__).resolve().parent; W=Q.parents[1]; R=W.parent
REC=R/'work-r03_c04/resume-20261010'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
BOXES={'u':[7408,8781,8662,10035],'l':[7408,9805,8662,11059]}
CONTRACT=read(R.parent/'production-contract.json')
MANDATORY=[CONTRACT['layoutReference'],CONTRACT['detailStyleReference'],str(REC/'designs/mail-ui-v1/01-mail-event.png')]
MANDATORY_ROLES=['mandatory whole-map layout reference; no zoom-out or objects copied','mandatory independent material painting style','mandatory approved primary painting style; recovered byte-exact mail reference']
def base():
    ns={'__file__':str(W/'east_gate_qa.py')}
    exec(compile((W/'east_gate_qa.py').read_text().split("prefix=W/'qa/east-full-height-gate'")[0],str(W/'east_gate_qa.py'),'exec'),ns)
    return ns
def prepare(side,version='v01'):
    ident=f'r03_c03_e3_door_{side}_{version}'; b=BOXES[side]
    ns=base(); pair=ns['pair']; crop=pair[8781-8192:11059-8192,7408-4096:8662-4096].copy()
    sources=[{'file':str(R/'tiles/r03_c03.candidate-repair-v5.png'),'sha256':sha(R/'tiles/r03_c03.candidate-repair-v5.png')},{'file':str(W/'qa/east-full-height-gate.json'),'sha256':sha(W/'qa/east-full-height-gate.json')}]
    if side=='l' and version=='v01':
        up=R/'native/r03_c03_e3_door_u_v01.png'; a=np.array(Image.open(up).convert('RGB')); assert a.shape==(1254,1254,3)
        crop[:1254]=a; sources.append({'file':str(up),'sha256':sha(up),'operation':'exact upper1254 in object context and actual230 top-overlap in lower guide'})
    if version=='v03':
        ep=R/'tiles/r03_c03.candidate-repair-v5.png';ev=np.array(Image.open(ep).convert('RGB'));crop[1024:,784:]=ev[9805-8192:11059-8192,:470]
        sources.append({'file':str(ep),'sha256':sha(ep),'operation':'exact current-v5 pixels for all context east ofglobal8192; removes west-overlap pixels from north anchor'})
    context=Q/f'{ident}.whole-door-context.png'; guide=Q/f'{ident}.edit-target.png'
    assert not context.exists() and not guide.exists()
    Image.fromarray(crop).save(context); y=b[1]-8781;Image.fromarray(crop[y:y+1254]).save(guide)
    der={'role':'mechanical native-pixel edit input only, not generated art','globalNativeBox':b,'globalCoreBox':[b[0]+115,b[1]+115,b[2]-115,b[3]-115],'objectContextBox':[7408,8781,8662,11059],'scale':1,'sources':sources,'guideSHA256':sha(guide),'contextSHA256':sha(context)}
    write(Q/f'{ident}.guide-derivation.json',der)
    if side=='u':
        instruction='This is the UPPER half of a two-part repair of one tall wooden shop doorway. Establish the same existing warm timber appearance continuously across the complete header and upper door planks. Preserve the diagonal roof eave, rounded brackets, door gaps, post edges, red lantern silhouette and cap/ribs, cream wall and red window exactly. The upper half supplies the lighting and wood-grain standard for the next lower half. Gently resolve abrupt pasted-looking timber tone blocks inside this upper doorway while leaving its sunlight/shadow geometry unchanged; do not move any structural line or redraw unrelated roof/wall objects.'
    else:
        instruction='This is the LOWER half of the SAME tall wooden shop doorway. The first230 rows of Image1 are exact existing UPPER-object native pixels at the same global positions; retain them exactly as the north join anchor. Retain the original dark wood values at the top; do not brighten the complete doorway or its upper half. Remove the conspicuous scalloped horizontal paint-value step across the right-hand vertical door planks around local x860..1045,y315..355 (global x8270..8455,y10120..10155). Continue each existing upper plank tone and vertical grain downward through the defect without a transverse cutoff, with natural gradual painted shading toward the sill; keep the existing real diagonal sunlight shadow, vertical door gaps, right post, lantern tassel, threshold stones, and all silhouette positions. Do not turn the defect into a horizontal board, scratch, seam, shadow edge, band or decorative line. Full door frame context is Image2.'
    prompt='Use case: precise-object-edit. Asset: native hand-painted Q-style game-map doorway repair. EDIT Image1 at its exact existing scale, framing and1254x1254 dimensions. Image2 is the complete tall doorway context only, never squeeze it into the output. Images3,4,5 are mandatory layout and painting-style references only.\n'+instruction+'\nKeep all timber thicknesses, plank widths and gap paths, perspective, warm colors and soft rounded hand-painted volume. Preserve positions at all four borders, including the outer115px neighbor context. Keep the existing crop; no zoom, rotate, stretch, warp, new architecture, labels, people, UI, grid, watermark or vignette. Output only one opaque1254x1254 square close-up at exactly Image1 scale. Preserve completed red lantern details; do not invent another lantern. Highest visual completion consistent with the attached approved style.'
    pf=Q/f'{ident}.prompt.txt';pf.write_text(prompt,encoding='utf8')
    refs=[str(guide),str(context)]+MANDATORY; roles=['exact1254 native-coordinate edit target','complete doorway object context and geometry; preserve crop scale of Image1']+MANDATORY_ROLES
    for p in refs:assert Path(p).is_file()
    assert sha(MANDATORY[2])=='3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2'
    req={'ident':ident,'promptFile':str(pf),'prompt':prompt,'referenced_image_paths':refs,'referenceRoles':roles,'transparent_background':False,'submittedAt':datetime.now(timezone.utc).isoformat(),'globalNativeBox':b,'globalCoreBox':der['globalCoreBox'],'references':[{'file':p,'sha256':sha(p),'role':r}for p,r in zip(refs,roles)],'submittedParameters':{'model':None,'quality':None}}
    write(Q/f'{ident}.request.json',req)
    write(Q/'config-evidence.json',{'configSnapshot':read(REC/'config/image-generation.json'),'file':str(REC/'config/image-generation.json'),'sha256':sha(REC/'config/image-generation.json'),'recoveryManifest':str(REC/'recovery-manifest.json'),'officialRecheckDate':'2026-10-10','officialRecheck':['https://openai.com/index/introducing-chatgpt-images-2-5/','https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst'],'recheckObservation':'Official page still identifies Sunburst as most capable and lists max quality; retained same-batch target, no shared config changed. Built-in exposes no model or quality selectors.'})
    print(json.dumps({'request':str(Q/f'{ident}.request.json'),'guide':str(guide),'context':str(context)}))
def record(ident):
    req=read(Q/f'{ident}.request.json');receipt=read(Q/f'{ident}.receipt.json');dst=R/'native'/f'{ident}.png';assert not dst.exists()
    shutil.copy2(receipt['originalFile'],dst);im=Image.open(dst);im.load();assert im.size==(1254,1254),f'unexpected native {im.size}'
    meta={'file':str(dst),'sha256':sha(dst),'generatedAt':receipt['returnedAt'],'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(REC/'config/image-generation.json'),'configEvidence':str(Q/'config-evidence.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in tool exposes no model/quality selector and returned no model/quality evidence. Historical target and prompt do not establish actual version.','prompt':req['promptFile'],'references':req['references'],'evidence':{'receipt':str(Q/f'{ident}.receipt.json'),'request':str(Q/f'{ident}.request.json'),'fields':['output_hint']},'globalNativeBox':req['globalNativeBox'],'globalCoreBox':req['globalCoreBox'],'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'status':'proposal-pending-native-geometry-and-material-QA','purpose':'E3 whole-door object repair group; no shared tile selected'}
    write(str(dst)+'.generation.json',meta);print(json.dumps(meta))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare(*sys.argv[2:])
    elif sys.argv[1]=='record':record(sys.argv[2])
