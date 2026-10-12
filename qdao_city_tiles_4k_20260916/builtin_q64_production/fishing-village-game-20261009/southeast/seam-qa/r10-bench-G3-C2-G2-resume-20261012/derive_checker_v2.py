from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'check_native_rect_generation_v1.py').read_text(encoding='utf-8')
s=s.replace("records={(r['tile'],r['patch']):r for r in guide['sourcePieces']}",
 """records={(r['tile'],r['patch']):r for r in guide['sourcePieces']}
baseRecords={}
if job.get('baseCandidateManifest'):
    baseMan=json.loads(Path(job['baseCandidateManifest']).read_text(encoding='utf-8'))
    baseRecords={(r['tile'],r['patch']):r for r in baseMan['patches']}""")
s=s.replace("art=Image.open(rec['file']).convert('RGB');old=np.asarray(art).copy()",
 """baseRec=baseRecords.get(key);basePath=baseRec['file'] if baseRec else rec['file']
    if baseRec:assert sha(basePath)==baseRec['sha256']
    art=Image.open(basePath).convert('RGB');old=np.asarray(art).copy()
    canonicalArray=np.asarray(Image.open(rec['file']).convert('RGB'))""")
s=s.replace("'nativeFrameWorld':nb,'worldAdoptBox':inter",
 "'baseCandidateFile':basePath,'baseCandidateSha256':sha(basePath),'cumulativeCoreChangedPixels':int(np.any(aa[115:1139,115:1139]!=canonicalArray[115:1139,115:1139],axis=2).sum()),'nativeFrameWorld':nb,'worldAdoptBox':inter")
s=s.replace("'outsideAdoptPixelsChanged':0","'outsideLocalAdoptPixelsChangedFromBase':0")
s=s.replace("for rec in patches:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']",
 """for key,rec in baseRecords.items():sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
for rec in patches:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']""")
s=s.replace("'beforeGuide':job['beforeGuide']","'baseCandidateManifest':job.get('baseCandidateManifest'),'beforeGuide':job['beforeGuide']")
out=D/'check_native_rect_generation_v2.py';assert not out.exists();out.write_text(s,encoding='utf-8')
