from pathlib import Path
from PIL import Image
import argparse,json,hashlib,shutil,sys,datetime
b=Path(__file__).resolve().parents[1]; sw=b.parent
sys.path.insert(0,str(sw))
import native_pipeline as n
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d): Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','select']);ap.add_argument('patch');ap.add_argument('version');ap.add_argument('--target');ap.add_argument('--content');ap.add_argument('--extra');ap.add_argument('--layout',action='store_true');args=ap.parse_args()
pid=args.patch;row=int(pid[1:3]);col=int(pid[4:6]);v=b/'refinement'/'versions'/args.version
if args.mode=='prepare':
    assert not v.exists();v.mkdir(parents=True)
    pipe=n.Pipeline(b.name);doc=pipe.coordinate_file();item=next(x for x in doc['patches'] if x['id']==pid)
    base=read(sorted((b/'pipeline'/'prompts').glob(pid+'.*.request.json'))[0])
    neighbors=[];corner={'priority':'upper','pasteOrder':['left when available','upper when available'],'bothSourcesPresent':False,'blendingOrResampling':False}
    if args.layout:
        im=Image.open(item['guide']).convert('RGB'); left=pipe.neighbor(row,col,'left'); upper=pipe.neighbor(row,col,'top')
        if left:
            im.paste(left[0],(0,0));left[1].update(targetBox=[0,0,230,1254],effectiveTargetBox=[0,230 if upper else 0,230,1254]);neighbors.append(left[1])
        if upper:
            im.paste(upper[0],(0,0));upper[1].update(targetBox=[0,0,1254,230],effectiveTargetBox=[0,0,1254,230]);neighbors.append(upper[1])
        corner['bothSourcesPresent']=bool(left and upper);im.save(v/'seed.png');target=v/'seed.png'
        write(v/'seed.derivation.json',{'layoutGuide':item['guide'],'layoutGuideSha256':h(item['guide']),'neighbors':neighbors,'operation':'exact crop/paste of existing guide and native overlap strips; no resampling','gameArt':False})
    else: target=Path(args.target)
    refs=[pipe.ref(target,'edit target; original native or guide seed as explicitly described')]+pipe.current_refs()
    if args.extra: refs.append(pipe.ref(args.extra,'approved source geometry/context for this correction; not final art'))
    prompt=Path(args.content).read_text(encoding='utf-8-sig');(v/'prompt.txt').write_text(prompt,encoding='utf-8')
    base.update(prompt=prompt,promptFile=str(v/'prompt.txt'),promptSha256=h(v/'prompt.txt'),referenced_image_paths=[r['file'] for r in refs],references=refs,neighborSources=neighbors,cornerTreatment=corner,preparedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),warnings=pipe.warnings,version=args.version,workflow='immutable native refinement')
    write(v/'request.json',base);print(str(v/'request.json'))
else:
    q=read(v/'request.json');receipt=v/'receipt.json';r=read(receipt);src=Path(r['sourceOutputPath']);dst=v/(pid+'.png');assert not dst.exists()
    im=Image.open(src);assert im.size==(1254,1254) and im.format=='PNG';assert im.mode in ('RGB','RGBA');assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
    shutil.copy2(src,dst)
    rec=read(b/'native'/(pid+'.png.generation.json'))
    rec.update(file=str(dst),sha256=h(dst),generatedAt=r['returnedAtUtc'],generatedAtEvidence='Observed builtin return timestamp; host generation time undisclosed',width=1254,height=1254,format='PNG',mode=im.mode,opaque=True,tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,evidence={'toolReceipt':str(receipt),'toolReceiptSha256':h(receipt),'pngMetadata':im.info},prompt=q['promptFile'],promptSha256=q['promptSha256'],request=str(v/'request.json'),requestSha256=h(v/'request.json'),references=q['references'],neighborSources=q['neighborSources'],cornerTreatment=q['cornerTreatment'],coordinates=q['coordinates'],sourceOutputPath=str(src),sourceOutputSha256=h(src),nativePixelsPreserved=True,resizedAfterGeneration=False,formalAccepted=False,sizeMatchesPlan=True,visualStatus='candidate_pending_macro_and_seam_QA')
    write(str(dst)+'.generation.json',rec)
    selpath=b/'refinement'/'selection.json';sel=read(selpath) if selpath.exists() else {};shutil.copy2(selpath,v/'selection.before.json') if selpath.exists() else None
    sel[pid]=str(Path('refinement')/'versions'/args.version/(pid+'.png.generation.json'));write(selpath,sel);write(v/'selection.after.json',sel)
    print(json.dumps({'native':str(dst),'sha256':h(dst),'formalAccepted':False}))
