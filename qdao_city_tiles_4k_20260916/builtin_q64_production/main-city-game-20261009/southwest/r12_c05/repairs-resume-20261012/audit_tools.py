from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, sys, datetime

B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05')
D=B/'repairs-resume-20261012'
D.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def describe(p):
    p=Path(p)
    with Image.open(p) as im: size=list(im.size)
    return {'file':str(p),'sha256':sha(p),'dimensions':size}
def savej(p,obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def register_request(name):
    t=D/name
    contract=json.loads((B.parent.parent/'production-contract.json').read_text())
    refs=[t/'input.png',Path(contract['layoutReference']),Path(contract['detailStyleReference']),Path(contract['primaryStyleReference'])]
    savej(t/'request.json',{'tool':'image_gen.imagegen','prompt':(t/'prompt.txt').read_text(encoding='utf-8'),'references':[describe(p) for p in refs],'transparent_background':False,'actualModel':None,'actualQuality':None,'requestedSize':list(Image.open(t/'input.png').size),'maximumFeatherPixels':2,'preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    print(t/'request.json')
def record_native(name,filename):
    t=D/name;p=t/'native.png'
    savej(t/'receipt.json',{'tool':'image_gen.imagegen','outcome':'success','generatedSourcePath':r'C:/Users/luyua/.codex/generated_images/01a1301a-c454-7b20-abf6-17f6ef73b906/'+filename,'native':describe(p),'request':str(t/'request.json'),'actualModel':None,'actualQuality':None,'savedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    print(json.dumps(describe(p)))

def prepare():
    a=B/'repairs-audit-line-20261011/integrated-local-v06/assembly.json'
    A=json.loads(a.read_text()); src=Path(A['contextOutput']['file'])
    im=Image.open(src).convert('RGB')
    assert im.size==(4326,4326) and sha(src)=='7217476a67e3f26ace57938baf737cc3e028f853a964287882585659b3cc76e2'
    Q=D/'qa-baseline-v06';Q.mkdir(exist_ok=True)
    im.resize((1082,1082)).save(Q/'context-preview-resized.png')
    entries=[]
    for direction in ['H','V']:
        contact=Image.new('RGB',(3*512,4*512),'white');draw=ImageDraw.Draw(contact)
        for n in range(1,4):
            for k in range(1,5):
                p=115+1024*n;t=115+1024*(k-1)
                box=(t,p-180,t+1024,p+180) if direction=='H' else (p-180,t,p+180,t+1024)
                crop=im.crop(box);name=f'{direction}{n}-{k}'
                out=Q/(name+'.png');crop.save(out)
                preview=crop.copy();preview.thumbnail((480,456))
                x=(n-1)*512;y=(k-1)*512;contact.paste(preview,(x,y+32));draw.text((x+8,y+8),name,fill='black')
                entries.append({'id':name,'box':list(box),**describe(out),'resampled':False})
        contact.save(Q/(direction+'-contact-resized.png'))
    savej(Q/'manifest.json',{'sourceAssembly':str(a),'source':describe(src),'seams':entries,'formalAccepted':False})
    T=D/'V1-row1-quiet-v01';T.mkdir(exist_ok=True)
    box=(512,0,1766,1254);im.crop(box).save(T/'input.png')
    savej(T/'input-derivation.json',{'source':describe(src),'cropContextBox':list(box),'resampled':False,'targetSeamContextX':1139,'targetSeamLocalX':627})
    print(json.dumps({'qa':str(Q),'input':describe(T/'input.png')},ensure_ascii=False))

def integrate():
    import numpy as np
    T=D/'V1-row1-quiet-v01';O=D/'integrated-local-v07';O.mkdir(exist_ok=True)
    A=json.loads((B/'repairs-audit-line-20261011/integrated-local-v06/assembly.json').read_text())
    base=Image.open(A['contextOutput']['file']).convert('RGB');orig=Image.open(T/'input.png').convert('RGB');native=Image.open(T/'native.png').convert('RGB')
    assert native.size==orig.size==(1254,1254)
    # Mechanical copy of only the reviewed local strip; no synthetic painting or resampling.
    roi=[467,0,807,1254];mask=np.zeros((1254,1254),np.uint8);mask[roi[1]:roi[3],roi[0]:roi[2]]=255
    alpha=mask.copy();alpha[:,467]=85;alpha[:,468]=170;alpha[:,805]=170;alpha[:,806]=85
    mixed=Image.composite(native,orig,Image.fromarray(alpha))
    ma=np.asarray(mask)>0;delta=np.any(np.asarray(mixed)!=np.asarray(orig),axis=2)
    assert int((delta&~ma).sum())==0
    mixed.save(T/'applied-crop.png');Image.fromarray(mask).save(T/'copy-mask.png');Image.fromarray(alpha).save(T/'alpha.png')
    result=base.copy();result.paste(mixed,(512,0));result.save(O/'r12_c05.candidate.context.png');result.crop((115,115,4211,4211)).save(O/'r12_c05.candidate.png')
    result.resize((1082,1082)).save(O/'context-preview-resized.png')
    globalmask=np.zeros((4326,4326),bool);globalmask[0:1254,512+467:512+807]=True
    outside=int((np.any(np.asarray(result)!=np.asarray(base),axis=2)&~globalmask).sum());assert outside==0
    core=Image.open(O/'r12_c05.candidate.png');assert core.size==(4096,4096)
    savej(T/'receipt.json',{'tool':'image_gen.imagegen','outcome':'success','generatedSourcePath':r'C:/Users/luyua/.codex/generated_images/01a1301a-c454-7b20-abf6-17f6ef73b906/exec-45ad1bca-0e97-4042-9c4d-57810f165993.png','native':describe(T/'native.png'),'actualModel':None,'actualQuality':None,'savedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    proposal={'attempt':'V1-row1-quiet-v01','input':describe(T/'input.png'),'native':describe(T/'native.png'),'sourceCropContextBox':[512,0,1766,1254],'copyMask':describe(T/'copy-mask.png'),'alpha':describe(T/'alpha.png'),'appliedCrop':describe(T/'applied-crop.png'),'maskLocalBox':roi,'maximumFeatherPixels':2,'outsideMaskChangedPixels':int((delta&~ma).sum()),'sourceResampling':False,'actualModel':None,'actualQuality':None,'formalAccepted':False,'internalAccepted':False,'localVisualAssessment':'Generated central strip material quieter; both ROI boundaries and crossing grout alignment still require original-size visual review.'}
    savej(T/'proposal.json',proposal)
    savej(O/'assembly.json',{'sourceAssembly':str(B/'repairs-audit-line-20261011/integrated-local-v06/assembly.json'),'appliedProposals':[str(T/'proposal.json')],'output':describe(O/'r12_c05.candidate.png'),'contextOutput':describe(O/'r12_c05.candidate.context.png'),'outsideUnionChangedPixels':outside,'maximumFeatherPixels':2,'coreEqualsContextCrop':True,'sourceResampling':False,'formalAccepted':False,'internalAccepted':False})
    savej(B/'production-resume-20261012.json',{'tile':'r12_c05','status':'active_local_repair','currentAssembly':str(O/'assembly.json'),'baselineAssembly':str(B/'repairs-audit-line-20261011/integrated-local-v06/assembly.json'),'generationSuccessCount':1,'firstNative':describe(T/'native.png'),'openIssues':['Review central-strip mask boundaries and diagonal seam alignment','24 internal seams complete visual review pending','Quiet material continuity and topology review pending','Roof small color discontinuities pending'],'formalAccepted':False,'internalAccepted':False,'actualModel':None,'actualQuality':None})
    print(json.dumps({'assembly':str(O/'assembly.json'),'core':describe(O/'r12_c05.candidate.png'),'context':describe(O/'r12_c05.candidate.context.png'),'outsideUnionChangedPixels':outside},ensure_ascii=False))

if __name__=='__main__':
    if sys.argv[1]=='prepare': prepare()
    elif sys.argv[1]=='integrate': integrate()
    elif sys.argv[1]=='register_request': register_request(sys.argv[2])
    elif sys.argv[1]=='record_native': record_native(sys.argv[2],sys.argv[3])
