from pathlib import Path
from PIL import Image
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('C:/Users/luyua/.codex/generated_images/01a10bcc-241b-7602-8038-bb41b9b643ed/exec-d214224b-3646-4b2f-867b-8401a1b06b8a.png')
OUT = ROOT / 'design/W.png'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

image = Image.open(SOURCE).convert('RGBA')
alpha = image.getchannel('A')
bbox = alpha.point(lambda p: 255 if p >= 8 else 0).getbbox()
scale = 1024 / 1254
size = (1024,1024)
offset = (0,0)
canvas = image.resize(size, Image.Resampling.LANCZOS)
canvas.save(OUT)

config = json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8'))
refs = [
 {'path':'D:/work/image/qdao_chibi_pets_v1/01_hu_tuan_tuan-transparent_1254.png','role':'Original exact identity and anatomy; viewed with view_image before generation'},
 {'path':'D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','role':'Approved primary painting and material style; viewed with view_image before generation'},
]
for ref in refs: ref['sha256'] = sha(Path(ref['path']))
receipt_path = ROOT / 'records/design-W.receipt.json'
save(receipt_path, {
 'returnedFields':['image_url','output_hint'],
 'image_url':'data URL returned; binary omitted from text receipt, source pixels identified by SHA256 in generation record',
 'output_hint':'Generated images are saved to C:\\Users\\luyua\\.codex\\generated_images\\01a10bcc-241b-7602-8038-bb41b9b643ed as C:\\Users\\luyua\\.codex\\generated_images\\01a10bcc-241b-7602-8038-bb41b9b643ed\\exec-d214224b-3646-4b2f-867b-8401a1b06b8a.png by default.\nIf you need to use a generated image at another path, copy it and leave the original in place unless the user explicitly asks you to delete it.\nThe generated image is already displayed to the user. There is no need to render it in the final response as a Markdown image or file link.',
 'callStartedAt':'2026-10-05T07:25:21.113-04:00', 'callReturnedAt':'2026-10-05T07:28:07.256-04:00',
 'callId':None, 'resultId':None, 'actualModel':None, 'actualQuality':None
})
native_record = ROOT / 'records/design-W.native.generation.json'
save(native_record, {
 'file':str(SOURCE).replace('\\','/'), 'sha256':sha(SOURCE),
 'generatedAt':'2026-10-05T07:28:07.256-04:00','generatedAtBasis':'tool-return timestamp; exact model completion timestamp not disclosed',
 'width':1254,'height':1254,'format':'PNG','mode':'RGBA',
 'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,
 'userOverride':{'modelTarget':'GPT Image 2.5','qualityTarget':'max'},
 'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[r['path'] for r in refs]},
 'actualModel':None,'actualQuality':None,
 'evidence':{'receipt':'records/design-W.receipt.json','returnedMetadataKeys':['image_url','output_hint'],'pngInfoKeys':[],
 'officialCapabilitySourcesCheckedOn':'2026-10-05','officialCapabilitySources':config['sources'],
 'officialCapabilityEvidenceIsActualRunEvidence':False},
 'unverifiedReason':'宿主管理，工具未披露 model/quality；本次PNG无Pillow可读元数据；配置目标与官方公告不证明实际调用版本。',
 'prompt':'prompts/design-W.txt','references':refs,
 'visualReview':{'trueRearView':True,'singleTail':True,'originalWhiteFoxIdentity':True,'goldBandKnotNearAnatomicalLeft':True,'gourdInFrontPartiallyOccluded':True,'seatedSupport':True,'noCroppedCoreSilhouette':True,'notes':'Rear head, back of cape and rump visible; near hind foot visible, far hind foot and far front paw naturally occluded. No extra limb or tail observed.'},
 'nativeAlpha':{'range':[0,255],'bboxAlphaAtLeast1':[0,21,1234,1254],'bboxAlphaAtLeast8':list(bbox)},
 'retention':'Builtin source outside delegated writable project directory; final design is design/W.png. Do not copy source as an extra backup.'
})
save(ROOT / 'design/W.png.generation.json', {
 'file':'design/W.png','sha256':sha(OUT),'width':1024,'height':1024,'format':'PNG','mode':'RGBA',
 'derivedFrom':{'path':str(SOURCE).replace('\\','/'),'sha256':sha(SOURCE),'generationRecord':'records/design-W.native.generation.json'},
 'operation':{'type':'static-design-export','alphaCleanup':None,
 'cropBox':None,'resize':list(size),'resampler':'Pillow LANCZOS','offset':list(offset),'canvas':[1024,1024],'noRedrawNoMirroringNoInterpolationOfMotion':True},
 'nominalPivotTopOrigin':[512,942],'pivotMeaning':'Prompt target only. Full 1254 square uniformly resized to 1024 with no crop, translation or alpha cleanup. Combat export should use the same full-canvas transform.',
 'actualSupportAssessment':{'method':'visual estimate from native pixels, approximate','nearHindPawNative':[311,1092],'rumpContactNative':[494,1125],'nearHindPawExport':[254,892],'rumpContactExport':[403,919],'notes':'Seated fox support is left of canvas center. Rump contact is approximately 109px left and 23px above nominal pivot; tail extends lower, visible alpha>=8 bottom is approximately y972. Do not correct each animation frame by bbox realignment.'},
 'supersededExport':{'sha256':'6f14824d9b56e00957f17a5a22b3a67ebec28b6822e1c725f712fa6f00c3ad69','reason':'Replaced before handoff per parent instruction: preserve full canvas and generated alpha; no bbox crop/recenter. No backup image retained.'},
 'actualModel':None,'actualQuality':None,'configSnapshot':config,
 'prompt':'prompts/design-W.txt','references':refs,
 'alpha':{'range':list(canvas.getchannel('A').getextrema()),'bbox':list(canvas.getchannel('A').getbbox()),'transparentPixels':canvas.getchannel('A').histogram()[0]},
 'status':'Final W direction identity anchor; static design only, not a combat frame or animation validation.'
})
print(json.dumps({'output':str(OUT),'size':canvas.size,'mode':canvas.mode,'sha256':sha(OUT),'alphaBBox':canvas.getchannel('A').getbbox(),'crop':bbox,'scale':scale,'offset':offset},ensure_ascii=False))
