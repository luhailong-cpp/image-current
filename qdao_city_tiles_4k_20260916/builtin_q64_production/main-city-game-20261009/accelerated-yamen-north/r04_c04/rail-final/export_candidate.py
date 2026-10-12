from pathlib import Path
import sys, json, hashlib, importlib.util
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

O = Path(__file__).resolve().parent
T = O.parent
ROOT = T.parent
PROJECT = ROOT.parent
E = O / 'exported-native-v1'
Q = O / 'qa-native'
E.mkdir(exist_ok=True)
Q.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location('rail_pipeline_readonly', ROOT/'pipeline.py')
pipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipe)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save_json(p, v):
    Path(p).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def ref(p):
    p = Path(p).resolve()
    v = {'file': str(p), 'sha256': sha(p)}
    if p.suffix.lower() == '.png':
        with Image.open(p) as im:
            v.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
    return v

def rgb(p):
    with Image.open(p) as im:
        return np.array(im.convert('RGB'))

NFILE = T/'qa-repair-native/exported-native-v1/s04_01-internal4-derived.png'
SFILE = PROJECT/'northwest/r05_c04/native/s01_01.png'
N = rgb(NFILE)
S = rgb(SFILE)
D = rgb(O/'alternative7-native.png')
assert sha(NFILE) == '1b6d718bad8c34a10cb0dcbc0161d0d1e59adc82bb05adec41c6740c4d123b0a'
assert sha(SFILE) == '7919f7f22ce30a0b79704adec2f6932b9c4a46c7677b526b8c4670d8a831fe8a'
assert np.array_equal(D[120:326,709:775], N[120:326,709:775]), 'Existing F2 must remain exact'
assert np.array_equal(D[1139:], S[115:230]), 'South halo must be actual immutable south source'
change = np.any(D != N, axis=2)
Image.fromarray((change*255).astype(np.uint8)).save(O/'alternative7-changed-mask.png')

attempts = []
for k in range(1,8):
    raw = O/f'raw-v{k}.png'
    params = O/f'parameters-v{k}.json'
    receipt_file = O/f'receipt-v{k}.json'
    receipt = json.loads(receipt_file.read_text(encoding='utf-8-sig'))
    args = json.loads(params.read_text(encoding='utf-8-sig'))
    host = Path(receipt['hostSourceFile'])
    assert raw.read_bytes() == host.read_bytes(), 'Host output bytes must be preserved'
    receipt.update(raw=ref(raw), rawHost=ref(host), parameters=ref(params),
                   prompt=ref(O/f'prompt-v{k}.txt'),
                   references=[ref(p) for p in args['referenced_image_paths']],
                   contextWorldBox=[12173,15245,13427,16499] if k==4 else [12173,15757,13427,17011],
                   hostBytesCopiedWithoutModification=True, actualModel=None, actualQuality=None,
                   transparencyRequested=args.get('transparent_background',False))
    save_json(receipt_file,receipt)
    attempts.append(ref(receipt_file))

design = ('Local design alternative: a new horizontal beveled stone connector joins the vertical rail to the existing wall coping near worldY 16269..16372. '
          'The broad rail direction and immutable true southern artwork are retained. This is a disclosed design change, not an assertion of original-design identity; root must review and choose.')
alpha_rule = {'coordinates':'pixel-center coordinates x+0.5,y+0.5 in each native 1254 image',
              'ramp':'s(v,a,b)=t*t*(3-2*t); t=clip((v-a)/(b-a),0,1)',
              'scale':255, 'quantization':'alpha=floor(255*w+0.5)',
              'blend':'uint8((base*(255-alpha)+raw*alpha+127)//255), independently per RGB channel',
              'spatialResampling':False, 'filtering':False, 'codedArtwork':False}
steps = [
 {'name':'stage4 rail taper','base':ref(NFILE),'raw':ref(O/'raw-v4.png'),'alpha':ref(O/'stage4-raw-alpha.png'),
  'worldBox':[12173,15245,13427,16499],
  'weight':'(s(y,420,484)*(1-s(x,810,870))+s(y,0,80)*s(x,810,870))*s(x,610,660)*(1-s(x,1090,1135))'},
 {'name':'stage4 true south restoration','base':'previous step','source':ref(SFILE),'alpha':ref(O/'stage4-south-alpha.png'),
  'sourceWorldBox':[12173,16269,13427,17523], 'destinationWorldBox':[12173,15245,13427,16499],
  'weight':'s(y,1024,1104); where active, source pixel is south[x,y-1024] at identical world coordinate',
  'derived':ref(O/'stage4-derived-native.png')},
 {'name':'stage5 intermediate joint surface','base':ref(O/'left-join-guide-v5.png'), 'raw':ref(O/'raw-v5.png'),
  'alpha':ref(O/'stage5-alpha.png'), 'worldBox':[12173,15757,13427,17011],
  'weight':'s(x,610,660)*(1-s(x,1200,1254))*s(y,380,440)*(1-s(y,552,620))',
  'derived':ref(O/'stage5-derived-context.png'), 'note':'Visible left ghosting in this intermediate is covered by the following generated connector.'},
 {'name':'alternative7 generated stone connector','base':ref(O/'stage5-derived-context.png'), 'raw':ref(O/'raw-v7.png'),
  'alpha':ref(O/'alternative7-alpha.png'), 'worldBox':[12173,15757,13427,17011],
  'weight':'s(x,600,640)*(1-s(x,1040,1100))*s(y,400,440)*(1-s(y,619,627))',
  'derived':ref(O/'alternative7-context.png'), 'copyToNative':'context rows [0,627) replace native rows [512,1139); other native pixels retained from stage5-derived-native',
  'designChange':design}
]
prov = {'schemaVersion':1,'kind':'native_multi_source_alpha_derivation', 'tile':'r04_c04',
        'designChange':design,'formalAccepted':False,'alphaRule':alpha_rule,'steps':steps,'generationReceipts':attempts,
        'finalNative':ref(O/'alternative7-native.png'),'nativeWorldBox':[12173,15245,13427,16499],
        'changedMask':ref(O/'alternative7-changed-mask.png'),
        'unchangedTrueSouth':ref(SFILE),'verifiedSouthNativeHaloEqualsTrueSource':True,
        'verifiedExistingF2PixelsUnchanged':True,'southFormalBoundaryWorldY':16384,
        'operations':'Same-world-coordinate source copying and recorded alpha compositing only. No resize, warp, blur, color adjustment, or code-painted image content.',
        'scripts':[ref(O/'derive_stage4.py'),ref(O/'derive_stage5.py'),ref(O/'derive_alternative7.py')]}
PROV = O/'derivation-manifest.json'
save_json(PROV,prov)

arrays = {}
baseline = {}
sources = []
exports = []
world = [12173,15245,13427,16499]
selection = json.loads((T/'pipeline-selection.json').read_text(encoding='utf-8-sig'))
save_json(O/'selection-snapshot-readonly.json',selection)
for patch in pipe.patch_ids():
    p = pipe.selected(T,patch)
    info = pipe.native_info(p)
    coordinate = pipe.coords('r04_c04',patch)
    b = coordinate['worldBoxWithHalo']
    a = rgb(p)
    r,c = int(patch[1:3])-1,int(patch[4:6])-1
    baseline[r,c] = a.copy()
    mask = np.zeros((1254,1254),bool)
    inter = pipe.intersect(world,b)
    if inter:
        l,t,rr,bb = inter
        sy,sx = slice(t-world[1],bb-world[1]),slice(l-world[0],rr-world[0])
        dy,dx = slice(t-b[1],bb-b[1]),slice(l-b[0],rr-b[0])
        mask[dy,dx] = change[sy,sx]
        a[dy,dx] = np.where(change[sy,sx,None],D[sy,sx],a[dy,dx])
    changed = np.any(a != baseline[r,c],axis=2)
    if changed.any():
        f = E/f'{patch}-rail-connector-derived.png'
        idx = E/f'{patch}-source-index.png'
        Image.fromarray(a).save(f)
        Image.fromarray(mask.astype(np.uint8)).save(idx)
        ys,xs = np.where(changed)
        record = {'schemaVersion':1,'kind':'native_multi_source_alpha_derivation','tile':'r04_c04','patch':patch,
                  **ref(f),'opaque':True,'resizedAfterGeneration':False,'finalArtUpscaled':False,'actualModel':None,'actualQuality':None,
                  'baseNative':info,'coordinates':coordinate,'derivationManifest':ref(PROV),
                  'derivedSource':ref(O/'alternative7-native.png'),'derivedSourceWorldBox':world,
                  'sourceIndexFile':str(idx),'sourceIndexSha256':sha(idx),
                  'sourceIndexMeaning':'0=unchanged latest selected native; 1=already alpha-composited alternative7-native copied at identical world coordinates. Do not reapply alpha.',
                  'changedPixels':int(changed.sum()),'copiedPixels':int(mask.sum()),
                  'changedNativeBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
                  'verifiedOutsideRepairMaskUnchanged':bool(np.array_equal(a[~mask],baseline[r,c][~mask])),
                  'retainedLatestInternal4Repairs':True,'designChange':design,'formalAccepted':False,
                  'operation':'Same-world-coordinate copy from recorded multi-source alpha derivation; no geometric or scale adjustment.'}
        save_json(f.with_suffix('.png.generation.json'),record)
        pipe.native_info(f)
        exports.append(record)
        info = pipe.native_info(f)
    arrays[r,c] = a
    sources.append({'patch':patch,**info,'coordinates':coordinate})

im,paths = pipe.assemble_arrays(arrays,'minimum-error')
old,oldpaths = pipe.assemble_arrays(baseline,'minimum-error')
im.save(Q/'candidate-minimum-error.png')
old.save(Q/'baseline-minimum-error.png')
out = np.array(im)
oldout = np.array(old)
diff = np.any(out != oldout,axis=2)
Image.fromarray((diff*255).astype(np.uint8)).save(Q/'candidate-change-mask.png')
qa = []
def crop(name,box):
    f=Q/(name+'.png'); im.crop(box).save(f)
    qa.append({**ref(f),'tileBox':list(box),'worldBox':[box[0]+12288,box[1]+12288,box[2]+12288,box[3]+12288],
               'kind':'native 1:1 crop of full minimum-error assembly','visualVerdict':'requires actual view'})
crop('rail-full-join-native',(450,2900,1100,4096))
crop('internal-y3072-segment01-native',(0,2912,1024,3232))
crop('internal-y3072-segment02-native',(1024,2912,2048,3232))
crop('internal-x1024-bottom-native',(864,3072,1184,4096))
external = np.concatenate([out[-320:,:1024],S[115:435,115:1139]],axis=0)
f=Q/'external-south-segment01-native.png'; Image.fromarray(external).save(f)
qa.append({**ref(f),'worldBox':[12288,16064,13312,16704],'formalBoundaryY':320,'worldBoundaryY':16384,
           'upperSource':ref(Q/'candidate-minimum-error.png'),'lowerSource':ref(SFILE),
           'lowerNativeCrop':[115,115,1139,435],'lowerSourcePixelsUnmodified':True,'visualVerdict':'requires actual view'})
ys,xs = np.where(diff)
report={'schemaVersion':1,'status':'candidate_for_root_review','formalAccepted':False,'designChange':design,
        'derivationManifest':ref(PROV),'exports':[{'patch':v['patch'],'file':v['file'],'sha256':v['sha256'],
                    'record':v['file']+'.generation.json','changedNativeBox':v['changedNativeBox']} for v in exports],
        'sources':sources,'candidate':ref(Q/'candidate-minimum-error.png'),'baseline':ref(Q/'baseline-minimum-error.png'),
        'assemblyMethod':'pipeline.assemble_arrays minimum-error; exact source pixels only',
        'assemblyPaths':paths,'baselineAssemblyPaths':oldpaths,'qaImages':qa,
        'changedTileBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedTilePixels':int(diff.sum()),
        'selectionOrProgressModified':False,'oldSouthSha256Still':sha(SFILE),
        'localVisualVerdict':'pending inspection of exported full assembly and true-south join'}
save_json(O/'candidate-manifest.json',report)
print(json.dumps({'exports':report['exports'],'changedTileBox':report['changedTileBox'],
                  'changedTilePixels':report['changedTilePixels'],'manifest':str(O/'candidate-manifest.json')},ensure_ascii=False))
