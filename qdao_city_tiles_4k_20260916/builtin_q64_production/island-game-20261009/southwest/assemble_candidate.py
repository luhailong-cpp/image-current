import production as p
from PIL import Image
SOURCES=[
['r09_c03_s01_01_resolved','r09_c03_s01_02_resolved','r09_c03_s01_03_v01','r09_c03_s01_04_v01'],
['r09_c03_s02_01_v01','r09_c03_s02_02_resolved','r09_c03_s02_03_resolved_v2','r09_c03_s02_04_v01'],
['r09_c03_s03_01_v01','r09_c03_s03_02_v01','r09_c03_s03_03_v01','r09_c03_s03_04_v01'],
['r09_c03_s04_01_v01','r09_c03_s04_02_v01','r09_c03_s04_03_resolved','r09_c03_s04_04_v01']]
def assemble(sources,version):
    canvas=Image.new('RGB',(4096,4096)); parents=[]
    for row,names in enumerate(sources):
        for col,stem in enumerate(names):
            path=p.ROOT/'native'/f'{stem}.png'; rec=p.load(str(path)+'.generation.json')
            assert rec['coordinates']['coreGlobalBox']==[8192+col*1024,32768+row*1024,9216+col*1024,33792+row*1024]
            with Image.open(path) as im:
                assert im.size==(1254,1254)
                canvas.paste(im.crop((115,115,1139,1139)),(col*1024,row*1024))
            parents.append({**p.metadata(path,'native source core'),'crop':[115,115,1139,1139],'destinationTopLeft':[col*1024,row*1024],'generationRecord':str(path)+'.generation.json'})
    out=p.ROOT/'output'/f'r09_c03-native-candidate-{version}.png'; canvas.save(out)
    p.dump(str(out)+'.derivation.json',{'file':str(out),'sha256':p.hashfile(out),'dimensions':[4096,4096],'operation':'16 native1024 cores hard pasted; no resampling, feather or color adjustment','globalBox':[8192,32768,12288,36864],'derivedFrom':parents,'status':'candidate_pending_internal_repairs_and_external_seams','formalAccepted':False})
    prev=p.ROOT/'qa'/f'r09_c03-native-candidate-{version}-preview.png'; canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(prev)
    p.dump(str(prev)+'.derivation.json',{'operation':'downsampled visual QA preview only','source':str(out),'sha256':p.hashfile(prev),'finalArt':False})
    for y in (1024,2048,3072):
        for x in (1024,2048,3072):
            box=[x-250,y-250,x+250,y+250]; dest=p.ROOT/'qa'/f'{version}-cross-{y}-{x}.png'; canvas.crop(box).save(dest)
            p.dump(str(dest)+'.derivation.json',{'operation':'native crop only','source':str(out),'crop':box,'sha256':p.hashfile(dest)})
    p.dump(p.ROOT/'current-native-map.json',{'r09_c03':sources,'rowsAvailable':4,'status':'candidate_pending_QA','formalAccepted':False})
    records=[p.load(f) for f in (p.ROOT/'native').glob('*.generation.json')]
    ai=[r for r in records if r.get('tool')=='image_gen.imagegen']
    p.update(generatedNativeCount=len(ai),corePositionsGenerated=16,corePositionsCovered=16,selectedCandidateCoreCount=16,usableNativeCount=None,usableNativeCountDefinition='Deprecated ambiguous metric; selectedCandidateCoreCount counts selected core positions, generatedNativeCount counts all AI outputs including retries/repairs.',complete4kCount=1,formalAcceptedCount=0,currentCandidate=str(out),status='candidate_4k_pending_repairs',nextStep='Repair lower-left horizontal join geometry; inspect every internal seam and external tile boundaries',pendingRepairs=['s04_01 to s04_02 wood plinth beam and stone frame vertical step','Native tone steps across wall, beam, lantern and stone joins'])
    print(str(out))
if __name__=='__main__': assemble(SOURCES,'v01')

