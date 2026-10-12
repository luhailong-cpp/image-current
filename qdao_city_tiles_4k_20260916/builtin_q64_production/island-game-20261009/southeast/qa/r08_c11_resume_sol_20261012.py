from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageFilter
import json, hashlib, shutil, sys, subprocess, os
import numpy as np

R = Path(__file__).resolve().parent.parent
Q = R / 'qa/r08_c11-production'
P = R / 'progress-r08_c11.json'
RESUME = R / 'production-resume-wall-sol-20261012.json'

def rd(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def wr(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sh(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def coord(pid):
    return next(p for t in rd(R/'coordinate-plan.json')['tiles'] for p in t['patches'] if p['id'] == pid)

def update_progress(**fields):
    d = rd(P)
    d.update(fields)
    d['updatedAt'] = now()
    wr(P, d)

def prepare():
    assert not RESUME.exists()
    authority = Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
    assert rd(authority)['newArtworkGenerationAllowed'] is True
    freeze = R/'migration-freeze-coordinate-audit-20261011.json'
    review = Q/'r08_c11_p14-v01-resume-sol-review.json'
    evidence = rd(Q/'r08_c11_p14-v01-evidence.json')
    assert not review.exists()
    evidence.update({
        'reviewedAt': now(), 'reviewer': 'wall_resume_sol',
        'status': 'candidate_geometry_pass', 'nativeViewed': True,
        'directlyViewed': ['native/r08_c11_p14_v01.png', 'qa/r08_c11-production/r08_c11_p14-v01-east.png', 'qa/r08_c11-production/r08_c11_p14-v01-bottom-native.png'],
        'findings': ['Saved original p14v01 reused without regeneration. Actual hard east seam against r08c12v15 and bottom seam against selected p24v01 preserve the paving grid and connected material at original scale.', 'No wall/roof discontinuity or duplicated objects in this core. Formal external acceptance remains pending the completed 4K tile.'],
        'formalAccepted': False,
    })
    wr(review, evidence)
    sf = R/'selected-native-r08_c11.json'
    selection = rd(sf)
    selection['selected']['r08_c11_p14'] = 'r08_c11_p14_v01.png'
    wr(sf, selection)
    pid, ver = 'r08_c11_p33', 'v05'
    guide = R/'guides'/f'{pid}.native-context-{ver}.png'
    refs = [{'file': str(guide), 'sha256': sh(guide), 'role': 'EDIT TARGET. Blurry coordinate layout without any rejected old-left wall pixels, with exact right230 and bottom230 original-coordinate selected native anchors. Sharp source-ID anchors are the connection authority.'}] + rd(R/'references.json')
    assert all(sh(r['file']) == r['sha256'] for r in refs)
    prompt = '''Use case: precise-object-edit.
Asset type: native game map tile close-up, ONE opaque 1254x1254 square.
Primary request: edit image1 at exactly the same crop, camera, scale and object positions. Render its blurred unknown region as refined daylight Q Daoist painted game-map art and reconstruct the complete broad pale stone wall panel, the narrow lower recessed bevel with fine light rim, base, and contact/cast shadow as ONE coherent perspective object.
Image1 is the only coordinate edit target. Its central and left blurry region is layout guidance only, NOT a rendered geometry constraint. There is no approved left wall line to preserve. Infer and reconstruct the whole wall from the actual sharp RIGHT230 wall and BOTTOM230 paving/foliage anchors. Extend the right anchor's existing wall edges and slope continuously toward the unknown left, preserving the endpoint at the actual core boundary local x1139. The wall lower bevel at x1139 must meet the sharp right-side line around y579; keep its base depth and parallel upper/lower projections continuous, with no step, jog, kink, second trim, diagonal shift or thick white bridge. Do not carry a wrong interior line into the right anchor. The still-unknown left neighbor will follow this newly corrected whole wall.
RIGHT230 (local x1024..1253) and BOTTOM230 (local y1024..1253) are true original-coordinate connections. Maintain their geometry, silhouettes, floor grid and material. Respect sharp selected roof scroll at the lower right and sharp green/yellow flowering foliage at the lower left: same position, size and object count. Do not duplicate or invent the scroll. Keep the top wall/coping only where indicated by image1; do not add a column, ball finial, fence, divider, rail, roof or ornament. Rebuild the unknown pale gray/cyan paving with varied subtle natural stone texture and the same existing stone joint directions so all right and bottom stone lines meet coherently.
Image2 is the sole full-map layout reference, used only to understand this close-up's place; do not draw a complete island. Image3 is independent natural stone/architecture material reference, not a coordinate crop. Image4 supplies approved refined Q Daoist painted form and brush style only, without its interface, text, people or night lighting. Bright daylight, soft rounded modeled forms, restrained clear fine painted stone texture matching the sharp anchors, no overall red ground. No extra objects, text, watermark, UI, black or transparent areas. Output sharp native art, no blur, image rescale, invented camera or enlargement. Single full square only.'''
    pf = R/'prompts'/f'{pid}_{ver}.prompt.txt'
    rf = R/'prompts'/f'{pid}_{ver}.request.json'
    assert not pf.exists() and not rf.exists()
    pf.write_text(prompt, encoding='utf-8')
    wr(rf, {'createdAt': now(), 'promptPath': str(pf), 'promptSha256': sh(pf), 'references': refs, 'transparent_background': False, 'submittedParameters': {'model': None, 'quality': None}, 'actualModel': None, 'actualQuality': None, 'coordinate': coord(pid), 'status': 'prepared_not_submitted', 'repairAuthority': str(authority), 'strategy': 'Remove all rejected old-left geometry; use blurry coordinate layout with exact native right/bottom anchors. No programmatic line shifting or final-art RGB manipulation.'})
    wr(RESUME, {'schemaVersion': 1, 'agent': 'wall_resume_sol', 'resumedAt': now(), 'authority': {'file': str(authority), 'sha256': sh(authority)}, 'historicalFreezeEvidence': {'file': str(freeze), 'sha256': sh(freeze), 'unmodified': True}, 'tile': 'r08_c11', 'builtinOnly': True, 'paidApiAllowed': False, 'noGitActionsPerformed': True, 'allOriginalsPreserved': True, 'status': 'waiting_root_builtin_generation_success', 'inFlight': False, 'activeImageGenCalls': 0, 'p14Reused': {'file': str(R/'native/r08_c11_p14_v01.png'), 'sha256': sh(R/'native/r08_c11_p14_v01.png'), 'review': str(review)}, 'preparedRequest': str(rf), 'selectedCoreCount': 7, 'selectedOverlayCount': 1, 'candidate4kCount': 0, 'formalAccepted': False})
    update_progress(status='resumed_local_preparation_waiting_builtin_confirmation', currentPatch=pid, inFlight=False, selectedNativeCount=7, lastReview=str(review), nextStep='Root must confirm a real successful builtin request before generation; then submit prepared p33v05 full-wall reconstruction and continue missing cores.')
    print(json.dumps({'promptPath': str(pf), 'requestPath': str(rf), 'references': [r['file'] for r in refs], 'p14Reused': True}))

def ingest(pid, ver, source, receipt_path):
    src, receipt = Path(source), Path(receipt_path)
    out = R/'native'/f'{pid}_{ver}.png'
    assert src.exists() and receipt.exists() and not out.exists()
    with Image.open(src) as im:
        im.load()
        assert im.size == (1254,1254), f'Unexpected native pixels {im.size}; no resizing permitted'
        fmt, mode = im.format, im.mode
    shutil.copy2(src,out)
    reqpath = R/'prompts'/f'{pid}_{ver}.request.json'
    req = rd(reqpath)
    assert all(sh(r['file']) == r['sha256'] for r in req['references'])
    assert sh(src) == sh(out)
    rec = {'file': str(out), 'sha256': sh(out), 'generatedAt': now(), 'width': 1254, 'height': 1254, 'format': fmt, 'mode': mode, 'tool': 'image_gen.imagegen', 'route': 'builtin', 'sourceOutputPath': str(src), 'sourceOutputSha256': sh(src), 'prompt': req['promptPath'], 'promptSha256': sh(req['promptPath']), 'request': str(reqpath), 'requestSha256': sh(reqpath), 'references': req['references'], 'receipt': str(receipt), 'receiptSha256': sh(receipt), 'submittedParameters': {'model': None, 'quality': None}, 'actualModel': None, 'actualQuality': None, 'configSnapshotTargetOnly': rd(P).get('configSnapshotTargetOnly'), 'unverifiedReason': 'Builtin tool does not disclose actual model/quality; target config is not actual evidence.', 'coordinate': req['coordinate'], 'resizedAfterGeneration': False, 'status': 'candidate_pending_visual_and_seam_review'}
    wr(Path(str(out)+'.generation.json'), rec)
    d = rd(RESUME)
    d.update({'status': 'native_saved_pending_review', 'lastNative': str(out), 'lastNativeSha256': sh(out), 'inFlight': False, 'activeImageGenCalls': 0, 'updatedAt': now()})
    wr(RESUME,d)
    update_progress(status='native_received_pending_review', generatedNativeCount=len(list((R/'native').glob('r08_c11*.png'))), currentPatch=pid, lastNative=str(out), lastNativeSha256=sh(out), inFlight=False)
    print(json.dumps({'file':str(out), 'sha256':sh(out), 'nativePixels':[1254,1254]}))

def prepare_next(pid, ver, neighbors):
    assert pid.startswith('r08_c11_p') and pid not in rd(R/'selected-native-r08_c11.json')['selected']
    env = dict(os.environ)
    env['ISLAND_PROGRESS_FILE'] = 'progress-r08_c11.json'
    guide = R/'guides'/f'{pid}.native-context-{ver}.png'
    if not guide.exists():
        strong_blur = (pid=='r08_c11_p32' and ver=='v03') or (pid=='r08_c11_p22' and ver in ['v02','v03']) or (pid=='r08_c11_p21' and ver in ['v02','v06']) or (pid=='r08_c11_p11' and ver=='v02')
        rawver=ver+'-raw' if strong_blur else ver
        subprocess.run([sys.executable, str(R/'qa/r08_c11_prepare.py'), 'context', pid, rawver, *neighbors], env=env, check=True)
        if rawver!=ver:
            rawguide=R/'guides'/f'{pid}.native-context-{rawver}.png';gm=rd(Path(str(rawguide)+'.generation.json'));a=np.array(Image.open(rawguide).convert('RGB'));ids=np.asarray(Image.open(gm['sourceID']));blur=np.asarray(Image.open(R/'guides'/f'{pid}.layout-only.png').convert('RGB').filter(ImageFilter.GaussianBlur(160)));a[ids==0]=blur[ids==0];Image.fromarray(a).save(guide)
            wr(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sh(guide),'operation':'Mechanical strong blur of layout-only unknown region, with all original-coordinate source-ID native anchors preserved identically. Guide only.','rawGuide':str(rawguide),'rawGuideSha256':sh(rawguide),'sourceID':gm['sourceID'],'sources':gm['sources'],'coordinate':coord(pid),'layoutOnlyMechanicalBlurRadius':160,'usableAsFinalArt':False})
    scenes = {
        'r08_c11_p33': 'Continue the same broad pale stone wall face, single narrow lower recessed bevel with fine light rim, short base and floor contact shadow from the authoritative sharp entire right half into the unknown left. Reconstruct one coherent perspective wall with no new top coping or wall termination. Continue existing paving and lower-left green/yellow flowering foliage; preserve the sharp same roof scroll at lower right.',
        'r08_c11_p32': 'Complete the open gray/cyan stone paving and same flowering green/yellow tree canopy in the unknown left region. Continue only the partial pale stone wall visible at the UPPER RIGHT in the sharp anchors. Its single narrow lower bevel and base continue out through the crop TOP; do not force a wall across the upper-left or introduce a wall termination, stone shelf, bench, platform, column or step. The left is paving and existing tree canopy. Match the sharp right and bottom foliage into one coherent natural canopy and retain the visible walkable paving lane.',
        'r08_c11_p31': 'Continue the walkable pale gray/cyan stone lane across the left and upper part, and the same dense green flowering tree canopy along the right/lower part. Keep the lane clear and preserve the layout shape of foliage.',
        'r08_c11_p23': 'Continue the same broad pale natural-stone wall panel and coping in the lower part, with the courtyard paving visible in the upper part. All long parallel wall projections must continue the sharp right and bottom anchors smoothly. Maintain a single coherent wall; do not invent a fence or column.',
        'r08_c11_p22': 'Reconstruct the entire existing pale stone wall end as one coherent object by extending the exact sharp RIGHT wall coping, lower trim and base projections backward toward the unknown left. The blurry interior is not a wall-line constraint. Continue the right wall slope, height and thickness without a step. Retain the single existing stone post near the left crop edge only where the continuous wall geometry places it; the coping projects upward toward the upper-left and may leave the crop, so do not lower the complete wall to fit a full post head or ball into this view. Preserve the existing post scale, without adding a new post, extra finial or decorative band. Continue pale stone ground and the existing foliage behind it.',
        'r08_c11_p21': 'Continue the broad pale stone wall face from the sharp right anchor out through the unknown LEFT edge as one perspective object, with its lower trim, base and contact shadow continuing the exact right slope. The coping largely exits above the crop; do not lower the wall to fit a full object. Retain only the already visible single stone post in the RIGHT anchor, same scale and position. No extra post, corner turn, wall end or new finial in the unknown left. Rebuild the flat open pale stone walkway beneath the single wall and continue exact bottom paving joints.',
        'r08_c11_p13': 'Render the open pale gray/cyan courtyard paving below the existing partial wooden table/stool furniture at the upper crop edge, retaining only furniture portions actually indicated by the layout. Preserve all existing sharp edge furniture and paving. Sparse existing red fallen petals or firecracker paper only where indicated.',
        'r08_c11_p12': 'Render the open pale stone courtyard pavement and continue the ONE existing decorated stone post head at the lower-left crop edge from the exact bottom anchor. Retain only the same partial wooden table/stool object entering the sharp right upper anchor, completing its existing portion naturally without adding furniture. Preserve the actual post, furniture and paving scale, position and object count. Follow the connected stone joint directions and neighboring courtyard layout. No new objects.',
        'r08_c11_p11': 'Continue the existing diagonal pale stone wall coping across the lower part from the exact bottom/right anchors, and reconstruct the open courtyard paving above it. Retain ONLY the single decorated stone post/ball already present in the sharp right anchor at exactly its current position and scale. There is no large additional post, lantern, architecture or finial in the unknown left or center. The blurry unknown layout is not an object or wall-line constraint. Follow the true sharp anchors for all geometry, foliage and stone joints; continue the wall projection into the left edge naturally without a corner turn or wall end. Maintain the existing single wall face below the coping. No new objects.',
    }
    prompt = f'''Use case: precise-object-edit.
Asset type: native game-map close-up, ONE opaque 1254x1254 square.
Edit image1 at exactly its present crop, scale, camera and coordinate layout. Complete its blurry unknown area as sharp refined painted Q Daoist daylight map art matching all sharp neighboring native anchors. {scenes[pid]}
Image1 is the only local coordinate edit target. Its sharp regions are original-coordinate native connection anchors. Preserve their geometry, stone joint endpoints, perspective, objects, foliage silhouettes, position, size and count; continue them naturally into the unknown region. The central blurry layout conveys composition but is not final art. Right230 and bottom230 connections must join continuously at actual core x1139/y1139, with no source cut, wall step, doubled outline, displaced tile grid, rectangular texture band, invented object or projection change. Maintain the existing full object's shape wherever it enters a sharp anchor.
Image2 is sole full-map layout reference only; do not draw a complete map. Image3 is independent material/architecture detail, not coordinate guidance. Image4 is approved refined Q Daoist painting style only, without its interface, text, people or night. Bright daylight, rounded painted modeled forms, natural varied pale gray/cyan stone with subtle restrained brush texture, connected walkable lanes, no overall red ground. No text/UI/watermark, new furniture or architecture, isolated potted plants, noise, sharpen filter, blur, black or transparent areas. Exactly one full square native image.'''
    refs = [{'file':str(guide), 'sha256':sh(guide), 'role':'EDIT TARGET. Exact original-coordinate selected neighboring anchors over blurry layout-only guidance; reconstruct unknown area with all connections and positions fixed.'}] + rd(R/'references.json')
    assert all(sh(r['file']) == r['sha256'] for r in refs)
    pf, rf = R/'prompts'/f'{pid}_{ver}.prompt.txt', R/'prompts'/f'{pid}_{ver}.request.json'
    assert not pf.exists() and not rf.exists()
    pf.write_text(prompt, encoding='utf-8')
    wr(rf, {'createdAt':now(), 'promptPath':str(pf), 'promptSha256':sh(pf), 'references':refs, 'transparent_background':False, 'submittedParameters':{'model':None,'quality':None}, 'actualModel':None, 'actualQuality':None, 'coordinate':coord(pid), 'status':'prepared_not_submitted', 'authority':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'})
    update_progress(status='next_request_prepared', currentPatch=pid, inFlight=False)
    print(json.dumps({'promptPath':str(pf), 'requestPath':str(rf), 'guide':str(guide)}))

def select(pid, ver, notes_path):
    evidence = rd(Q/f'{pid}-{ver}-evidence.json')
    notes = rd(notes_path)
    assert notes['nativeViewed'] and notes['allListedEvidenceDirectlyViewed']
    assert notes['status'] == 'candidate_geometry_pass'
    f = R/'native'/f'{pid}_{ver}.png'
    assert sh(f) == evidence['sha256']
    review = Q/f'{pid}-{ver}-resume-sol-review.json'
    assert not review.exists()
    evidence.update(notes)
    evidence.update({'reviewedAt':now(), 'reviewer':'wall_resume_sol', 'formalAccepted':False})
    wr(review,evidence)
    sf = R/'selected-native-r08_c11.json'
    selection = rd(sf)
    selection['selected'][pid] = f.name
    wr(sf,selection)
    d = rd(RESUME)
    d.update({'status':'selected_continue_missing_cores', 'selectedCoreCount':len(selection['selected']), 'lastReview':str(review), 'inFlight':False, 'activeImageGenCalls':0, 'updatedAt':now()})
    wr(RESUME,d)
    update_progress(status='patch_reviewed_continue', selectedNativeCount=len(selection['selected']), inFlight=False, lastReview=str(review))
    print(json.dumps({'selected':pid, 'version':ver, 'selectedCount':len(selection['selected'])}))

def prepare_wall_joint(pid='r08_c11_wall_joint',ver='v02',origin=None):
    origin=[2445,1933] if origin is None else origin
    world=[40960+origin[0],28672+origin[1],40960+origin[0]+1254,28672+origin[1]+1254]
    refs=rd(R/'references.json')
    im=Image.open(refs[0]['file']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(x*1254/57344 for x in world),Image.Resampling.BICUBIC)
    if pid=='r08_c11_wall_left_joint' and ver=='v03':
        im=im.filter(ImageFilter.GaussianBlur(160))
    placements=[]
    def place(file,src_origin,domain,role):
        x0=max(origin[0],domain[0]);y0=max(origin[1],domain[1]);x1=min(origin[0]+1254,domain[2]);y1=min(origin[1]+1254,domain[3])
        if x0>=x1 or y0>=y1:return
        box=[x0-src_origin[0],y0-src_origin[1],x1-src_origin[0],y1-src_origin[1]]
        dest=[x0-origin[0],y0-origin[1]]
        im.paste(Image.open(file).convert('RGB').crop(box),dest)
        placements.append({'file':str(file),'sha256':sh(file),'sourceCrop':box,'destination':dest,'role':role})
    if pid!='r08_c11_wall_joint':
        place(R/'native/r08_c11_p33_v06.png',[1933,1933],[1933,1933,3187,3187],'true right742 entire wall native; no rejected left lines')
        place(R/'native/r08_c11_p42_v01.png',[909,2957],[909,2957,2163,4211],'true bottom230 native')
    place(R/'native/r08_c11_p34_v01.png',[2957,1933],[2957,1933,4211,3187],'true right entire wall native; no rejected left lines')
    place(R/'native/r08_c11_p43_v02.png',[1933,2957],[1933,2957,3187,4211],'true bottom230 paving native')
    place(R/'native/r08_c11_p44_v01.png',[2957,2957],[2957,2957,4211,4211],'true bottom-right paving/roof native')
    for fn in rd(R/'selected-native-r08_c11.json')['selected'].values():
        f=R/'native'/fn;g=rd(Path(str(f)+'.generation.json'))['coordinate']['nativeGlobalBox'];o=[g[0]-40960,g[1]-28672]
        place(f,o,[o[0]+115,o[1]+115,o[0]+1139,o[1]+1139],'exact selected core ownership')
    for z in rd(R/'selected-overlays-r08_c11.json')['overlays']:
        place(Path(z['file']),z['originInTile'],z['destinationBox'],'exact selected whole roof overlay')
    guide=R/'guides'/f'{pid}.native-context-{ver}.png'
    assert not guide.exists()
    im.save(guide)
    co={'id':pid,'nativeGlobalBox':world,'coreGlobalBox':[world[0]+115,world[1]+115,world[0]+1139,world[1]+1139],'originInTile':origin,'layoutReferenceBox':[x*1254/57344 for x in world]}
    wr(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sh(guide),'operation':'Blurry sole coordinate-layout crop with exact original-coordinate selected right742/bottom230 native anchors; zero rejected p33 or old walljoint pixels. Guide only.','layoutOnlyMechanicalBlurRadius':160 if pid=='r08_c11_wall_left_joint' and ver=='v03' else None,'coordinate':co,'placements':placements,'usableAsFinalArt':False})
    prompt='''Use case: precise-object-edit. Output ONE opaque native1254x1254 square editing image1 at exactly the same crop, scale and camera.
Complete the blurry LEFT512 region of this local close-up by extending the actual sharp wall/paving in its RIGHT742 region into a single uninterrupted whole pale stone wall object. The right region contains authoritative sharp selected wall with its broad face, narrow lower recessed bevel, fine light rim, short base and cast/contact shadow. Reconstruct the complete unknown left portion of that same wall face, bevel, base and shadow using precisely the right region's existing projected slope, line thickness and depth. Continue every existing long single diagonal edge straight and consistently through the blurry left. There is no existing approved left wall geometry to preserve. Do not invent a different left slope or carry a blurry layout line into the right anchors. No step, jog, double edge, thick bridge, shifted line or visible rectangular source boundary.
The sharp RIGHT742 and BOTTOM230 are actual original-coordinate native anchors, not style examples. Preserve all their outline positions, wall edges and floor grid connection endpoints exactly. The former tile border is interior localx627, already within the sharp wall, and must remain naturally continuous across it. Preserve all the existing sharp wall upper/coping edges as indicated by the right; do not invent an additional stone top coping, platform, column, finial, divider, rail, fence or wall termination in the unknown left. The wall continues out of the crop. Preserve the sharp foreground gold-red roof curl at the right/lower edge as one same object of same size and position. No new scroll, hook or duplicate curl. Continue pale gray/cyan natural stone paving across the left so every floor joint meets the sharp right/bottom anchors. No new objects or map expansion.
Image2 is full-map layout only, not output composition. Image3 is independent stone material/architecture reference only. Image4 is approved refined Q Daoist painting style only, without text/UI/people/night. Crisp bright daylight, rounded modeled painted forms, natural pale stone, restrained fine brush texture matching existing sharp anchors. Do not change camera or scale, blur output, add scratches/noise/text/watermark, or render black/transparent areas. Exactly one native full square.'''
    if pid!='r08_c11_wall_joint':
        prompt=prompt.replace('Preserve the sharp foreground gold-red roof curl at the right/lower edge as one same object of same size and position. No new scroll, hook or duplicate curl.', 'Preserve the existing sharp flowering green/yellow foliage at the lower left/bottom, with the same composition, silhouette, size and object count. Do not add a roof, curl, scroll or architecture.')
    rs=[{'file':str(guide),'sha256':sh(guide),'role':'EDIT TARGET. Blurry unknown left512 + authoritative sharp true right742/bottom230. No old rejected left wall pixels.'}]+refs
    assert all(sh(r['file'])==r['sha256'] for r in rs)
    pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json'
    assert not pf.exists() and not rf.exists()
    pf.write_text(prompt,encoding='utf-8')
    wr(rf,{'createdAt':now(),'promptPath':str(pf),'promptSha256':sh(pf),'references':rs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':co,'status':'prepared_not_submitted','authority':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'})
    update_progress(status='complete_wall_joint_v02_prepared',currentPatch=pid,inFlight=False)
    d=rd(RESUME);d.update({'status':'complete_wall_joint_prepared','preparedRequest':str(rf),'updatedAt':now()});wr(RESUME,d)
    print(json.dumps({'guide':str(guide),'request':str(rf),'prompt':str(pf)}))

def qa_wall_joint():
    base=Image.new('RGB',(4096,4096))
    for p in next(t for t in rd(R/'coordinate-plan.json')['tiles'] if t['id']=='r08_c11')['patches']:
        sr,sc=p['subrow'],p['subcolumn']
        base.paste(Image.open(R/'guides'/f'{p["id"]}.layout-only.png').convert('RGB').crop((115,115,1139,1139)),((sc-1)*1024,(sr-1)*1024))
    for pid,fn in rd(R/'selected-native-r08_c11.json')['selected'].items():
        sr,sc=int(pid[-2]),int(pid[-1])
        base.paste(Image.open(R/'native'/fn).convert('RGB').crop((115,115,1139,1139)),((sc-1)*1024,(sr-1)*1024))
    overlays=rd(R/'selected-overlays-r08_c11.json')['overlays']
    for z in overlays:base.paste(Image.open(z['file']).convert('RGB').crop(z['sourceCrop']),z['destinationBox'][:2])
    src=R/'native/r08_c11_wall_joint_v02.png'
    trial=base.copy();trial.paste(Image.open(src).convert('RGB').crop((115,115,1139,1139)),(2560,2048))
    boxes={'right':[3328,2048,3840,3072],'bottom':[2560,2816,3584,3328],'top':[2560,1792,3584,2304],'former-joint':[2816,2048,3328,3072]}
    entries=[]
    for name,box in boxes.items():
        f=Q/f'wall-joint-v02-{name}.png';assert not f.exists();trial.crop(box).save(f);entries.append({'file':str(f),'sha256':sh(f),'box':box})
    for z in overlays:trial.paste(Image.open(z['file']).convert('RGB').crop(z['sourceCrop']),z['destinationBox'][:2])
    f=Q/'wall-joint-v02-roof-restored-right.png';trial.crop(boxes['right']).save(f);entries.append({'file':str(f),'sha256':sh(f),'box':boxes['right'],'operation':'Original selected complete roof object owns its existing box after the tentative wall joint core.'})
    wr(Q/'wall-joint-v02-evidence.json',{'native':str(src),'sha256':sh(src),'entries':entries,'sourceCrop':[115,115,1139,1139],'destinationBox':[2560,2048,3584,3072],'status':'pending_direct_visual_review','formalAccepted':False})
    print(json.dumps(entries))

def select_wall_joint():
    src=R/'native/r08_c11_wall_joint_v02.png'
    review=Q/'wall-joint-v02-resume-sol-review.json'
    assert not review.exists()
    evidence=rd(Q/'wall-joint-v02-evidence.json')
    evidence.update({'status':'candidate_complete_wall_geometry_pass','reviewedAt':now(),'reviewer':'wall_resume_sol','nativeViewed':True,'allListedEvidenceDirectlyViewed':True,'findings':['The original interior source cut is removed. The actual right boundary connects the narrow wall bevel, wall base and top trim without a major step at native scale.','Bottom paving, gold curl/hook, cladding and roof connections are continuous; minor painted texture/collar variation remains. Upper left connection is pending an ungenerated core.','The wall joint must own its complete core after the older roof overlay. Restoring the older roof box on top recreates an incompatible wall segment; that alternative is rejected.','No RGB changes, resampling, warps or line shifting used. Continue the still-unknown left half from this new complete native wall.'],'formalAccepted':False})
    wr(review,evidence)
    sf=R/'selected-overlays-r08_c11.json';d=rd(sf)
    assert all(Path(z['file']).name!='r08_c11_wall_joint_v02.png' for z in d['overlays'])
    d['overlays'].append({'file':str(src),'sha256':sh(src),'originInTile':[2445,1933],'sourceCrop':[115,115,1139,1139],'destinationBox':[2560,2048,3584,3072],'review':str(review),'ownershipOrder':'After older whole roof overlay; this complete core owns wall and its connected foreground fragment.'})
    wr(sf,d)
    update_progress(status='complete_wall_joint_selected_continue_left',selectedOverlayCount=2,lastReview=str(review),inFlight=False)
    d=rd(RESUME);d.update({'status':'complete_wall_joint_selected_continue_left','selectedOverlayCount':2,'lastReview':str(review),'updatedAt':now()});wr(RESUME,d)
    print(json.dumps({'selectedOverlay':str(src),'overlayCount':2}))

def qa_effective_patch(pid,ver,neighbors):
    f=R/'native'/f'{pid}_{ver}.png'
    overlays=rd(R/'selected-overlays-r08_c11.json')['overlays']
    def core(p,n):
        sr,sc=int(p[-2]),int(p[-1]);x0=(sc-1)*1024;y0=(sr-1)*1024
        out=Image.open(n).convert('RGB').crop((115,115,1139,1139))
        for z in overlays:
            db=z['destinationBox'];sp=z['sourceCrop'];ix0=max(x0,db[0]);iy0=max(y0,db[1]);ix1=min(x0+1024,db[2]);iy1=min(y0+1024,db[3])
            if ix0>=ix1 or iy0>=iy1:continue
            box=[sp[0]+ix0-db[0],sp[1]+iy0-db[1],sp[0]+ix1-db[0],sp[1]+iy1-db[1]]
            out.paste(Image.open(z['file']).convert('RGB').crop(box),(ix0-x0,iy0-y0))
        return out
    own=core(pid,f);sr,sc=int(pid[-2]),int(pid[-1]);entries=[]
    def save(name,img,desc):
        path=Q/f'{pid}-{ver}-{name}.png'
        if path.exists():
            assert np.array_equal(np.asarray(Image.open(path).convert('RGB')),np.asarray(img)), 'Existing evidence differs; use a new version.'
        else:img.save(path)
        entries.append({'file':str(path),'sha256':sh(path),'composition':desc,'nativeScale':True})
    for fn in neighbors:
        npid=fn.split('_v')[0];n=R/'native'/fn;nr,nc=int(npid[-2]),int(npid[-1]);other=core(npid,n)
        if nr==sr and nc==sc+1:
            out=Image.new('RGB',(512,1024));out.paste(own.crop((768,0,1024,1024)),(0,0));out.paste(other.crop((0,0,256,1024)),(256,0));save('right-native',out,'Actual own and neighbor 1024 cores with selected overlays in their current ownership order; hard seam x256.')
        elif nr==sr+1 and nc==sc:
            out=Image.new('RGB',(1024,512));out.paste(own.crop((0,768,1024,1024)),(0,0));out.paste(other.crop((0,0,1024,256)),(0,256));save('bottom-native',out,'Actual own and neighbor 1024 cores with selected overlays in current ownership order; hard seam y256.')
        else:raise ValueError(fn)
    x0=(sc-1)*1024;y0=(sr-1)*1024
    for i,z in enumerate(overlays):
        db=z['destinationBox']
        if x0<db[0]<x0+1024 and db[1]<y0+1024 and db[3]>y0:
            x=db[0]-x0;save(f'overlay{i+1}-left',own.crop((max(0,x-256),0,min(1024,x+256),1024)),'Current actual core at the complete-object overlay left ownership boundary; no blend.')
    if sc==4:
        right=Image.open(R/'tiles/r08_c12.candidate-v15.png').convert('RGB');out=Image.new('RGB',(512,1024));out.paste(own.crop((768,0,1024,1024)),(0,0));out.paste(right.crop((0,(sr-1)*1024,256,sr*1024)),(256,0));save('east',out,'Actual fixed final east candidate at x256.')
    wr(Q/f'{pid}-{ver}-evidence.json',{'native':str(f),'sha256':sh(f),'entries':entries,'formalAccepted':False})
    print(json.dumps(entries))

def prepare_p32_repair():
    pid,ver='r08_c11_p32','v02';base=R/'native/r08_c11_p32_v01.png';oldguide=R/'guides/r08_c11_p32.native-context-v01.png';gm=rd(Path(str(oldguide)+'.generation.json'))
    arr=np.array(Image.open(base).convert('RGB'));anchor=np.asarray(Image.open(oldguide).convert('RGB'));ids=np.asarray(Image.open(gm['sourceID']));mask=ids>0;arr[mask]=anchor[mask]
    guide=R/'guides'/f'{pid}.native-context-{ver}.png';assert not guide.exists();Image.fromarray(arr).save(guide)
    wr(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sh(guide),'operation':'Unscaled whole native candidate with exact current neighboring anchor pixels restored from provenance-ID guide; guide only, no final pixel manipulations.','base':str(base),'baseSha256':sh(base),'anchorGuide':str(oldguide),'anchorGuideSha256':sh(oldguide),'anchorSourceID':gm['sourceID'],'restoredAnchorPixels':int(mask.sum()),'coordinate':coord(pid),'usableAsFinalArt':False})
    prompt='''Use case: precise-object-edit. Output one opaque native1254x1254 square, exactly editing image1 at the same crop, scale and camera.
Remove the ENTIRE invented broad raised stone shelf/platform/ledge occupying the upper-left and upper-middle of image1. This long horizontal raised slab and its vertical front face are a mistake; there is NO raised platform, bench, step or extra coping at the base of this wall. Reconstruct the actual existing single pale stone wall FACE behind it and the flat walkable stone paving beneath it. The correct wall has only ONE narrow recessed diagonal lower bevel and a fine light rim, a short plain base and floor contact shadow. Continue that one exact diagonal from the sharp RIGHT230 wall anchor backward through the whole left wall, with the same projected slope, line thickness and base depth. Do not retain the broad slab's top/front/back edges, termination or erroneous left slope. Remove every platform boundary and complete one coherent continuous wall-floor contact instead. No new top coping, post, ornament or additional horizontal trim.
The sharp RIGHT230 and BOTTOM230 have been restored from true approved neighboring natives and are connection authority. Preserve their geometry, outlines, positions, paving-grid endpoint angles and all foliage silhouettes. They override any contradictory interior candidate geometry. The actual core right seam localx1139 must meet the right single wall bevel, without a jog, step, doubled line or rectangular repair boundary. Preserve the flowering green/yellow tree canopy below with exactly the same composition and object count; preserve the actual bottom and right paving stone shapes and grid connections. Change the complete unwanted platform/wall object and adjacent ground as necessary, no other objects.
Image2 sole full-map layout only, image3 stone material reference only, image4 approved refined Q Daoist painting style only, without text/UI/people/night. Bright daylight, fine restrained painted textures, natural pale gray/cyan stone, rounded forms. No additional objects, black/transparent areas, text, watermark, blur, altered camera or rescale. One native full square.'''
    refs=[{'file':str(guide),'sha256':sh(guide),'role':'EDIT TARGET. Remove entire invented platform object; true sharp right230/bottom230 anchor pixels restored exactly.'}]+rd(R/'references.json');pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json';assert not pf.exists();pf.write_text(prompt,encoding='utf-8');wr(rf,{'createdAt':now(),'promptPath':str(pf),'promptSha256':sh(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':coord(pid),'status':'prepared_not_submitted','authority':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'})
    wr(Q/'r08_c11_p32-v01-resume-sol-review.json',{'native':str(base),'sha256':sh(base),'status':'rejected_invented_raised_wall_platform','nativeViewed':True,'findings':['Generated tree/paving are plausible but an invented long raised stone platform covers the wall base and changes the actual right wall projection. Not selected. Full-object removal prepared with current true anchors restored.'],'formalAccepted':False})
    print(json.dumps({'guide':str(guide),'request':str(rf)}))

def qa_custom_wall(pid,ver,tag=None):
    src=R/'native'/f'{pid}_{ver}.png';rec=rd(Path(str(src)+'.generation.json'));o=rec['coordinate']['originInTile'];x,y=o[0]+115,o[1]+115
    base=Image.new('RGB',(4096,4096))
    for p in next(t for t in rd(R/'coordinate-plan.json')['tiles'] if t['id']=='r08_c11')['patches']:
        base.paste(Image.open(R/'guides'/f'{p["id"]}.layout-only.png').convert('RGB').crop((115,115,1139,1139)),((p['subcolumn']-1)*1024,(p['subrow']-1)*1024))
    for p,fn in rd(R/'selected-native-r08_c11.json')['selected'].items():base.paste(Image.open(R/'native'/fn).convert('RGB').crop((115,115,1139,1139)),((int(p[-1])-1)*1024,(int(p[-2])-1)*1024))
    for z in rd(R/'selected-overlays-r08_c11.json')['overlays']:base.paste(Image.open(z['file']).convert('RGB').crop(z['sourceCrop']),z['destinationBox'][:2])
    base.paste(Image.open(src).convert('RGB').crop((115,115,1139,1139)),(x,y))
    boxes={'right':[x+768,y,x+1280,y+1024],'bottom':[x,y+768,x+1024,y+1280],'top':[x,y-256,x+1024,y+256],'interior':[x+256,y,x+768,y+1024]}
    entries=[]
    for name,box in boxes.items():
        suffix='-'+tag if tag else '';f=Q/f'{pid}-{ver}-{name}{suffix}.png';assert not f.exists();base.crop(box).save(f);entries.append({'file':str(f),'sha256':sh(f),'box':box,'nativeScale':True})
    suffix='-'+tag if tag else '';ef=Q/f'{pid}-{ver}-evidence{suffix}.json';assert not ef.exists();wr(ef,{'native':str(src),'sha256':sh(src),'entries':entries,'sourceCrop':[115,115,1139,1139],'destinationBox':[x,y,x+1024,y+1024],'formalAccepted':False})
    print(json.dumps(entries))

def select_custom_wall(pid,ver,notes_path):
    src=R/'native'/f'{pid}_{ver}.png';rec=rd(Path(str(src)+'.generation.json'));e=rd(Q/f'{pid}-{ver}-evidence.json');notes=rd(notes_path)
    assert notes['status']=='candidate_geometry_pass' and notes['nativeViewed'] and notes['allListedEvidenceDirectlyViewed']
    review=Q/f'{pid}-{ver}-resume-sol-review.json';assert not review.exists();e.update(notes);e.update({'reviewedAt':now(),'reviewer':'wall_resume_sol','formalAccepted':False});wr(review,e)
    sf=R/'selected-overlays-r08_c11.json';d=rd(sf);d['overlays'].append({'file':str(src),'sha256':sh(src),'originInTile':rec['coordinate']['originInTile'],'sourceCrop':e['sourceCrop'],'destinationBox':e['destinationBox'],'review':str(review)});wr(sf,d)
    update_progress(status='complete_wall_joint_selected_continue_left',selectedOverlayCount=len(d['overlays']),lastReview=str(review),inFlight=False)
    re=rd(RESUME);re.update({'status':'complete_wall_joint_selected_continue_left','selectedOverlayCount':len(d['overlays']),'lastReview':str(review),'updatedAt':now()});wr(RESUME,re)
    print(json.dumps({'selectedOverlay':str(src),'overlayCount':len(d['overlays'])}))


def prepare_upper_joint(post=False):
    strong=post in ['strong','strong3']
    pid,ver,origin=('r08_c11_wall_post_joint' if post else 'r08_c11_wall_upper_joint'),('v03' if post=='strong3' else ('v02' if strong else 'v01')),([397,909] if post else [1421,909])
    world=[40960+origin[0],28672+origin[1],40960+origin[0]+1254,28672+origin[1]+1254]
    refs=rd(R/'references.json')
    im=Image.open(refs[0]['file']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(x*1254/57344 for x in world),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(160))
    ids=np.zeros((1254,1254),np.uint16);sources=[]
    def place(f,o,domain):
        x0=max(origin[0],domain[0]);y0=max(origin[1],domain[1]);x1=min(origin[0]+1254,domain[2]);y1=min(origin[1]+1254,domain[3])
        if x0>=x1 or y0>=y1:return
        box=[x0-o[0],y0-o[1],x1-o[0],y1-o[1]]
        im.paste(Image.open(f).convert('RGB').crop(box),(x0-origin[0],y0-origin[1]))
        n=len(sources)+1;ids[y0-origin[1]:y1-origin[1],x0-origin[0]:x1-origin[0]]=n
        sources.append({'id':n,'file':str(f),'sha256':sh(f),'sourceCrop':box,'destination':[x0-origin[0],y0-origin[1]],'originInTile':o})
    selection=rd(R/'selected-native-r08_c11.json')['selected']
    for pid0 in (['r08_c11_p31','r08_c11_p32'] if strong else (['r08_c11_p22','r08_c11_p31'] if post else ['r08_c11_p23','r08_c11_p32'])):
        f=R/'native'/selection[pid0];g=rd(Path(str(f)+'.generation.json'))['coordinate']['nativeGlobalBox'];o=[g[0]-40960,g[1]-28672];place(f,o,[o[0],o[1],o[0]+1254,o[1]+1254])
    overlays=rd(R/'selected-overlays-r08_c11.json')['overlays']
    for z in overlays:
        o=z['originInTile'];place(Path(z['file']),o,[o[0],o[1],o[0]+1254,o[1]+1254])
    for fn in selection.values():
        if strong and fn=='r08_c11_p22_v03.png':continue
        f=R/'native'/fn;g=rd(Path(str(f)+'.generation.json'))['coordinate']['nativeGlobalBox'];o=[g[0]-40960,g[1]-28672];place(f,o,[o[0]+115,o[1]+115,o[0]+1139,o[1]+1139])
    for z in overlays:place(Path(z['file']),z['originInTile'],z['destinationBox'])
    if strong:
        place(R/'native/r08_c11_p22_v03.png',[909,909],[942,909,1074,1759])
    guide=R/'guides'/f'{pid}.native-context-{ver}.png';assert not guide.exists();im.save(guide)
    sid=Q/f'{pid}-{ver}.context-source-id.png';Image.fromarray(ids).save(sid)
    co={'id':pid,'tile':'r08_c11','originInTile':origin,'nativeGlobalBox':world,'nativePixels':[1254,1254],'coreCrop':[115,115,1139,1139],'coreDestinationBox':[origin[0]+115,origin[1]+115,origin[0]+1139,origin[1]+1139]}
    wr(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sh(guide),'operation':'Strong blurred full-map layout guide, with exact unscaled same-coordinate right742 and bottom230 selected native anchors. Guide only.','sources':sources,'sourceID':str(sid),'sourceIDSha256':sh(sid),'coordinate':co,'usableAsFinalArt':False})
    prompt='''Use case: precise-object-edit. ONE opaque native1254x1254 square, exactly editing image1 at its same crop, scale and camera.
Reconstruct the complete continuous pale stone WALL FACE and coping in the unknown LEFT512 from the exact sharp RIGHT742 and BOTTOM230. This is the middle wall segment, not a wall end. The single broad wall continues out of the LEFT edge; no post, column, ball, platform or termination is visible in this crop. The top coping, top rim of wall panel, lower trim and base form one coherent perspective object, with the sharp right wall projections extending smoothly backward toward the left. Do not lower the wall to reveal extra ground or fit an entire decorative object into the view. Do not add foliage behind the wall except existing foliage already visible in sharp anchors. The blurry left region only gives approximate material/composition, not a wall line to preserve.
The existing entire RIGHT742 occupies local x512..1253 and contains the true wall height, coping thickness, panel grid and projections. These exact sharp geometry anchors override any blurry interior shape. The entire actual core x115..1138 must continue the same wall without a step, double cap, triangular wedge, crop boundary or kink at old seam x627. Preserve all right and bottom paving tile endpoints, plants, size, position and count. Complete the unknown single wall panel and existing pale gray/cyan paving as one coherent object. No finial, new shrub, bench, raised platform, rail, second coping or extra architectural detail.
Image2 is sole full-map layout only; do not render a complete map. Image3 gives natural stone materials only; image4 approved refined daylight Q Daoist painted style only, without text/UI/people/night. Bright daylight, pale natural stone, restrained clear painted texture, rounded forms. No black/transparent area, image resizing, blur, text or watermark. One full native square.'''
    if post:
        prompt='''Use case: precise-object-edit. ONE opaque native1254x1254 square, exactly edit image1 at its same crop, camera and scale.
Complete the unknown LEFT512 as sharp refined painted wall and paving, using the complete exact RIGHT742 and BOTTOM230 original-coordinate neighbors as connection authority. Continue the existing broad pale stone wall face, narrow lower rim, plain base and flat stone walkway out through the LEFT edge. Retain the ONE existing decorated stone post already visible in the right anchor near local x550..650: keep its ENTIRE body, engraving, head portion and low foot at exactly their original-coordinate position and scale. No other post, column, pilaster, wall corner, fence or ornament exists in the unknown left. Do not add one. No platform or wall termination.
The approved right anchor contains the whole post and the true coherent stone floor beneath it. Keep its wall projections and paving joints. Render the entire foreground paving sheet as one coherent perspective ground, with right and bottom joint endpoints extending smoothly into unknown left. No image cut, shifted tile grid, rectangular texture band, hard repair border, duplicate line or floor step. Preserve wall and post heights: do not raise the low pillar foot or shorten its body. Infer unknown wall and paving from these actual native anchors; blurry left material has no approved line to preserve.
Image2 sole full-map layout only, no complete map. Image3 independent stone material only. Image4 approved refined daylight Q Daoist painting style only, without interface/text/people/night. Pale natural gray/cyan stone, rounded forms, fine restrained painted texture. No extra objects, blur, resizing, black/transparent area, text or watermark. One sharp native square.'''
    if strong:
        prompt=prompt.replace('complete exact RIGHT742 and BOTTOM230','exact RIGHT230, BOTTOM230 and complete single post')
        prompt+='''\nThe only approved left-interior architectural anchor is the complete post itself in its narrow original-coordinate strip. All other old left-interior wall lines have been removed. Reconstruct the WHOLE wall panel/coping from the true RIGHT230 around that existing complete post. The true RIGHT230 begins at local x1024 and comes from the already corrected upper-wall native. At actual core x1139 continue its exact coping, panel rim and wall-base slopes with no step. No old incorrect left line should constrain this wall. Complete the entire ground from the actual bottom and right paving. Do not preserve rectangular post-reference edges; continue surrounding wall and ground naturally around the whole existing object.'''
    rs=[{'file':str(guide),'sha256':sh(guide),'role':'EDIT TARGET. Exact same-coordinate right/bottom anchors and complete existing post; no rejected left wall lines.'}]+refs
    pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json';assert not pf.exists() and not rf.exists();pf.write_text(prompt,encoding='utf-8')
    wr(rf,{'createdAt':now(),'promptPath':str(pf),'promptSha256':sh(pf),'references':rs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':co,'status':'prepared_not_submitted','authority':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'})
    update_progress(status='upper_wall_joint_prepared',currentPatch=pid,inFlight=False)
    print(json.dumps({'guide':str(guide),'request':str(rf),'prompt':str(pf)}))

def prepare_p21_repair(ground=False):
    pid,ver='r08_c11_p21','v05' if ground=='preserve' else ('v04' if ground else 'v03');base=R/'native'/('r08_c11_p21_v03.png' if ground else 'r08_c11_p21_v02.png');oldguide=R/'guides/r08_c11_p21.native-context-v02.png';gm=rd(Path(str(oldguide)+'.generation.json'))
    a=np.array(Image.open(base).convert('RGB'));anchors=np.asarray(Image.open(oldguide).convert('RGB'));ids=np.asarray(Image.open(gm['sourceID']));mask=ids>0
    if ground=='preserve':
        paving=np.asarray(Image.open(R/'native/r08_c11_p21_v04.png').convert('RGB'));a[900:,:]=paving[900:,:]
    a[mask]=anchors[mask]
    guide=R/'guides'/f'{pid}.native-context-{ver}.png';assert not guide.exists();Image.fromarray(a).save(guide)
    wr(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sh(guide),'operation':'Full native object edit target with true same-coordinate right/bottom anchors restored. Guide only.','base':str(base),'baseSha256':sh(base),'anchorGuide':str(oldguide),'anchorGuideSha256':sh(oldguide),'sourceID':gm['sourceID'],'restoredAnchorPixels':int(mask.sum()),'coordinate':coord(pid),'usableAsFinalArt':False})
    prompt='''Use case: precise-object-edit. ONE opaque native1254x1254 square, editing image1 exactly at its same crop, scale and camera.
Remove both invented vertical stone PILASTERS in the unknown LEFT part of image1: the narrow raised vertical strip near x110..165 and the wide raised vertical strip near x450..520, including each entire base/plinth, projecting edges and cast shadow. These two vertical columns are mistakes. Replace their entire objects with the single uninterrupted broad pale natural stone WALL FACE behind them. Continue the fine diagonal wall-panel texture and the ONE narrow lower bevel/rim and short plain base smoothly across the removed column areas, using the existing wall and base projection on both sides. Preserve the continuous wall height; do not add a corner, fence, post, finial, platform, raised ledge, new trim, ornament or extra vertical divider.
Retain exactly ONE approved existing tall decorated post in the RIGHT sharp anchor near x1070..1160, preserving its full visible body, foot, existing flower engraving, head portion, scale and position. The true RIGHT230 and BOTTOM230 pixels have been restored from neighboring originals. They are connection authority. Keep that one right post, wall projection, ground tile endpoints, foliage shadows and material continuous at actual core x1139 and y1139. Keep the open stone walkway below and all paving joints connected. Do not redesign or simplify the right post and do not add any new object elsewhere.
Image2 sole full-map layout only; image3 independent stone material reference only; image4 approved refined Q Daoist painted style only, no text/UI/people/night. Bright daylight, natural pale gray/cyan stone, rounded modeled forms, restrained clear painted texture. No black/transparent areas, image resize, blur, text or watermark. Single full native square.'''
    if ground:
        prompt='''Use case: precise-object-edit. ONE opaque native1254x1254 square, editing image1 exactly at the same crop, scale and camera.
Reconstruct the entire connected flat STONE PAVING SHEET beneath the existing wall as one coherent perspective ground object. Remove the straight rectangular image boundary near local x1024 in the foreground below the right post: its stone lines jump and the shadow texture abruptly changes. This vertical boundary is a wrong pasted-image cut, not an edge, step, wall, paving feature or object. Remove all traces of that cut by re-rendering the complete foreground ground, including the stone shapes and shadows across it.
The sharp original-coordinate RIGHT230 and BOTTOM230 are true neighboring anchors. Their stone joint endpoints, sizes, slopes, grass tufts, shadows, positions and count are the geometry authority. Continue every right and bottom stone joint smoothly into the unknown left/top foreground with a single coherent grid. Do not preserve the wrong interior grid or its shifted endpoint if it conflicts with these anchors. No straight vertical repair border, displaced joint, texture band, hard rectangular change, doubled stone edge or invented paving divider may remain. The original narrow pale paving strip may remain only if it continues actual bottom anchor geometry.
Preserve the entire already-correct stone WALL above, its single narrow lower rim/base, and exactly ONE tall approved post at the RIGHT. Do not change wall size, slope, viewpoint, post position or count. No new pilasters, columns, corners, ornaments or furniture. No newly raised platform or floor step.
Image2 is full-map layout only; image3 stone material only; image4 approved refined Q Daoist painted style only, without text/UI/people/night. Bright daylight, natural pale gray/cyan stone, restrained subtle painted texture. One full sharp native square, no resize, blur, black/transparent areas, text or watermark.'''
    if ground=='preserve':
        prompt+='''\nPreserve the COMPLETE architectural wall and decorated right pillar exactly as image1 currently shows them, including the entire long pillar body and its LOW FOOT resting on the ground around local y850..880. Do not shorten the pillar or raise its foot; no floating foot above the wall base. The ground is the only object to re-render. The rectangular source transition in foreground paving and shadows is an image-guide defect only; unify all foreground stone joints beneath the unchanged architecture. All stone post outlines and plinth height are fixed.'''
        wr(Path(str(guide)+'.repair-inputs.json'),{'operation':'Guide only. Top900 rows from correct-architecture v03, foreground900+ from paving v04, then exact original-coordinate right/bottom anchors restored; no shifting or drawing.','architecture':str(base),'architectureSha256':sh(base),'foreground':str(R/'native/r08_c11_p21_v04.png'),'foregroundSha256':sh(R/'native/r08_c11_p21_v04.png'),'foregroundSameCoordinateRegion':[0,900,1254,1254],'usableAsFinalArt':False})
    refs=[{'file':str(guide),'sha256':sh(guide),'role':'EDIT TARGET. Whole native object repair; true sharp right/bottom neighbor anchors restored. No final RGB edits.'}]+rd(R/'references.json')
    pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json';assert not pf.exists() and not rf.exists();pf.write_text(prompt,encoding='utf-8');wr(rf,{'createdAt':now(),'promptPath':str(pf),'promptSha256':sh(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':coord(pid),'status':'prepared_not_submitted','authority':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'})
    print(json.dumps({'guide':str(guide),'request':str(rf),'prompt':str(pf)}))

def prepare_post_coping():
    pid,ver='r08_c11_wall_post_joint','v04';base=R/'native/r08_c11_wall_post_joint_v03.png';oldguide=R/'guides/r08_c11_wall_post_joint.native-context-v03.png';gm=rd(Path(str(oldguide)+'.generation.json'));origin=[397,909]
    a=np.array(Image.open(base).convert('RGB'));g=np.asarray(Image.open(oldguide).convert('RGB'));ids=np.asarray(Image.open(gm['sourceID']));blur=np.asarray(Image.open(base).convert('RGB').filter(ImageFilter.GaussianBlur(160)));a[:450,:1024]=blur[:450,:1024];a[ids>0]=g[ids>0]
    im=Image.fromarray(a);placements=[]
    def place(f,o,domain):
        x0=max(origin[0],domain[0]);y0=max(origin[1],domain[1]);x1=min(origin[0]+1254,domain[2]);y1=min(origin[1]+1254,domain[3])
        if x0>=x1 or y0>=y1:return
        box=[x0-o[0],y0-o[1],x1-o[0],y1-o[1]];dest=[x0-origin[0],y0-origin[1]];im.paste(Image.open(f).convert('RGB').crop(box),dest);placements.append({'file':str(f),'sha256':sh(f),'originInTile':o,'sourceCrop':box,'destination':dest})
    place(R/'native/r08_c11_p12_v01.png',[909,-115],[909,-115,2163,1139])
    z=rd(R/'selected-overlays-r08_c11.json')['overlays'][3];place(Path(z['file']),z['originInTile'],z['destinationBox'])
    guide=R/'guides'/f'{pid}.native-context-{ver}.png';assert not guide.exists();im.save(guide)
    co=rd(Path(str(base)+'.generation.json'))['coordinate']
    wr(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sh(guide),'operation':'Whole-object edit guide only: previous complete post/wall native, unknown upper450 strongly blurred to remove incorrect coping line; all original-coordinate right/bottom/post anchors restored, new exact upper p12 native anchor supplied, actual owned right overlay restored last. No drawing, displacement or final RGB manipulation.','base':str(base),'baseSha256':sh(base),'anchorGuide':str(oldguide),'anchorGuideSha256':sh(oldguide),'placements':placements,'coordinate':co,'usableAsFinalArt':False})
    prompt='''Use case: precise-object-edit. ONE opaque native1254x1254 square, exact image1 crop, scale and camera.
+Reconstruct the ENTIRE single stone WALL-TOP COPING OBJECT and its narrow lower rim/shadow band as a continuous perspective object, extending the exact sharp RIGHT230 coping backward through the unknown left. The unknown top450 has been blurred to remove the incorrect old line. No old left coping slope is approved. At actual core x1139, EVERY long upper/lower coping projection and the narrow dark lower rim must meet the real right anchor smoothly, without even a small vertical jump or source step. Preserve one uniform projected coping thickness and depth from the right; do not keep a wrong interior intercept or curve, do not add another coping layer or diagonal wedge. Rebuild all individual stone blocks in this whole coping as necessary, preserving the existing object scale and block size.
+The sharp TOP230 contains actual upper neighboring courtyard and post-head pixels; continue their exact same-object projection into the unknown coping. The complete decorated post body, ONE head and low foot are existing fixed native anchors: keep their scale and position. Continue the existing broad wall face around that one post, with only its single existing coping. No new post, pilaster, raised shelf, corner, finial, ornament or extra shrub.
+Keep the already continuous wall base and the entire connected foreground stone pavement unchanged in geometry. True RIGHT230, BOTTOM230 and TOP230 anchor joint endpoints are authoritative. No hard rectangle, shifted grid, texture band, image cut or new floor step. If an interior wall-top line contradicts an anchor, reconstruct the complete wall-top object to the anchor; do not preserve the wrong line.
+Image2 sole full-map layout only, no full map; image3 independent stone material only; image4 approved refined Q Daoist painted style only, no text/UI/people/night. Bright daylight, pale natural gray/cyan stone, rounded forms, restrained painted texture. One native sharp square, no resize, blur, black/transparent area, text or watermark.'''.replace('\n+','\n')
    refs=[{'file':str(guide),'sha256':sh(guide),'role':'EDIT TARGET. Entire wall-top object repair, incorrect upper interior line removed; real right/top/bottom/post native anchors.'}]+rd(R/'references.json')
    pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json';assert not pf.exists() and not rf.exists();pf.write_text(prompt,encoding='utf-8');wr(rf,{'createdAt':now(),'promptPath':str(pf),'promptSha256':sh(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':co,'status':'prepared_not_submitted','authority':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'})
    print(json.dumps({'guide':str(guide),'request':str(rf),'prompt':str(pf)}))
def assemble(ver):
    selection = rd(R/'selected-native-r08_c11.json')['selected']
    expected = {f'r08_c11_p{r}{c}' for r in range(1,5) for c in range(1,5)}
    assert set(selection) == expected, f'Missing cores: {sorted(expected-set(selection))}'
    out = R/'tiles'/f'r08_c11.candidate-{ver}.png'
    q = R/'qa'/f'r08_c11-{ver}-sol'
    assert not out.exists() and not q.exists()
    q.mkdir()
    im = Image.new('RGB',(4096,4096))
    ids = np.zeros((4096,4096),np.uint16)
    sources = []
    for pid in sorted(selection):
        f = R/'native'/selection[pid]
        rec = rd(Path(str(f)+'.generation.json'))
        assert sh(f) == rec['sha256']
        assert Image.open(f).size == (1254,1254)
        sr, sc = int(pid[-2]), int(pid[-1])
        x,y=(sc-1)*1024,(sr-1)*1024
        im.paste(Image.open(f).convert('RGB').crop((115,115,1139,1139)),(x,y))
        sid=len(sources)+1
        ids[y:y+1024,x:x+1024]=sid
        sources.append({'id':sid,'file':str(f),'sha256':sh(f),'sourceCrop':[115,115,1139,1139],'destinationBox':[x,y,x+1024,y+1024],'originInTile':[x-115,y-115],'role':'selected_original_native_1024_core'})
    for z in rd(R/'selected-overlays-r08_c11.json')['overlays']:
        f=Path(z['file'])
        assert sh(f)==z['sha256']
        box,db=z['sourceCrop'],z['destinationBox']
        im.paste(Image.open(f).convert('RGB').crop(box),db[:2])
        sid=len(sources)+1
        ids[db[1]:db[3],db[0]:db[2]]=sid
        sources.append({'id':sid,**z,'role':'selected_complete_object_overlay'})
    assert np.all(ids>0)
    final=np.asarray(im)
    for s in sources:
        ys,xs=np.where(ids==s['id'])
        a=np.asarray(Image.open(s['file']).convert('RGB'))
        ox,oy=s['originInTile']
        assert np.array_equal(final[ys,xs],a[ys-oy,xs-ox]), f'Pixel provenance mismatch {s["file"]}'
        s['visiblePixels']=int(xs.size)
    im.save(out)
    sidfile=q/'visible-source-id.png'
    Image.fromarray(ids).save(sidfile)
    wr(q/'source-audit.json',{'file':str(out),'sha256':sh(out),'pixels':[4096,4096],'operation':'Exact unscaled native core crop/paste plus selected complete-object overlay; no RGB adjustments, blend, warp, rescale, painting or line shifting.','sourceID':str(sidfile),'sourceIDSha256':sh(sidfile),'sources':sources,'visiblePixelIdentityVerified':True,'formalAccepted':False})
    for r in range(1,5):
        for c in range(1,4):
            im.crop((c*1024-256,(r-1)*1024,c*1024+256,r*1024)).save(q/f'internal-r{r}-c{c}-c{c+1}.png')
    for r in range(1,4):
        for c in range(1,5):
            im.crop(((c-1)*1024,r*1024-256,c*1024,r*1024+256)).save(q/f'internal-r{r}-r{r+1}-c{c}.png')
    for r in range(1,4):
        for c in range(1,4):
            im.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)).save(q/f'junction-r{r}-c{c}.png')
    for s in sources:
        if s['role']=='selected_complete_object_overlay':
            x0,y0,x1,y1=s['destinationBox']
            for side,box in {'left':[x0-256,y0,x0+256,y1],'right':[x1-256,y0,x1+256,y1],'top':[x0,y0-256,x1,y0+256],'bottom':[x0,y1-256,x1,y1+256]}.items():
                if min(box)>=0 and box[2]<=4096 and box[3]<=4096:im.crop(box).save(q/f'overlay{s["id"]}-{side}.png')
    east=Image.open(R/'tiles/r08_c12.candidate-v15.png').convert('RGB')
    south=Image.open(R/'tiles/r09_c11.candidate-v05.png').convert('RGB')
    e=Image.new('RGB',(512,4096));e.paste(im.crop((3840,0,4096,4096)),(0,0));e.paste(east.crop((0,0,256,4096)),(256,0));e.save(q/'external-east.png')
    s=Image.new('RGB',(4096,512));s.paste(im.crop((0,3840,4096,4096)),(0,0));s.paste(south.crop((0,0,4096,256)),(0,256));s.save(q/'external-south.png')
    preview=im.copy();preview.thumbnail((1024,1024));preview.save(q/'preview-only-1024.png')
    d=rd(RESUME);d.update({'status':'4k_candidate_assembled_pending_full_visual_review','candidate4kCount':1,'candidate4k':str(out),'candidate4kSha256':sh(out),'sourceAudit':str(q/'source-audit.json'),'updatedAt':now()});wr(RESUME,d)
    update_progress(status='4k_candidate_assembled_pending_full_visual_review',candidate4kCount=1,lastCandidate=str(out),inFlight=False)
    print(json.dumps({'candidate':str(out),'sha256':sh(out),'qa':str(q),'sourceAudit':str(q/'source-audit.json')}))

if sys.argv[1] == 'prepare':
    prepare()
elif sys.argv[1] == 'ingest':
    ingest(*sys.argv[2:6])
elif sys.argv[1] == 'prepare-next':
    prepare_next(sys.argv[2],sys.argv[3],sys.argv[4:])
elif sys.argv[1] == 'select':
    select(*sys.argv[2:5])
elif sys.argv[1] == 'assemble':
    assemble(sys.argv[2])
elif sys.argv[1] == 'prepare-wall-joint':
    prepare_wall_joint()
elif sys.argv[1] == 'submitting':
    update_progress(status='builtin_generation_submitted', currentPatch=sys.argv[2], inFlight=True)
    d=rd(RESUME);d.update({'status':'builtin_generation_submitted','inFlight':True,'activeImageGenCalls':1,'currentPatch':sys.argv[2],'updatedAt':now()});wr(RESUME,d)
elif sys.argv[1] == 'qa-wall-joint':
    qa_wall_joint()
elif sys.argv[1] == 'select-wall-joint':
    select_wall_joint()
elif sys.argv[1] == 'qa-effective-patch':
    qa_effective_patch(sys.argv[2],sys.argv[3],sys.argv[4:])
elif sys.argv[1] == 'prepare-p32-repair':
    prepare_p32_repair()
elif sys.argv[1] == 'prepare-wall-left':
    prepare_wall_joint('r08_c11_wall_left_joint','v01',[1421,1933])
elif sys.argv[1] == 'prepare-wall-left-v02':
    prepare_wall_joint('r08_c11_wall_left_joint','v02',[1421,1933])
elif sys.argv[1] == 'prepare-wall-left-v03':
    prepare_wall_joint('r08_c11_wall_left_joint','v03',[1421,1933])
elif sys.argv[1] == 'prepare-upper-joint':
    prepare_upper_joint()
elif sys.argv[1] == 'prepare-post-joint':
    prepare_upper_joint(True)
elif sys.argv[1] == 'prepare-post-joint-v02':
    prepare_upper_joint('strong')
elif sys.argv[1] == 'prepare-post-joint-v03':
    prepare_upper_joint('strong3')
elif sys.argv[1] == 'prepare-post-coping':
    prepare_post_coping()
elif sys.argv[1] == 'prepare-p21-repair':
    prepare_p21_repair()
elif sys.argv[1] == 'prepare-p21-ground':
    prepare_p21_repair(True)
elif sys.argv[1] == 'prepare-p21-ground-preserve':
    prepare_p21_repair('preserve')
elif sys.argv[1] == 'qa-custom-wall':
    qa_custom_wall(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else None)
elif sys.argv[1] == 'select-custom-wall':
    select_custom_wall(*sys.argv[2:5])
