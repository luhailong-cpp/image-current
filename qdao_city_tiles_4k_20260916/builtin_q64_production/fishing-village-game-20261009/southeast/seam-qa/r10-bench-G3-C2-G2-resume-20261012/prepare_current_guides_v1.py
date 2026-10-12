"""Current native core guide extraction; no canonical writes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
D=Path(__file__).resolve().parent;BASE=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=m.Sources()
guides=[]
for name,frame,focus in [
 ('bench-G3-left',[30550,40200,31804,41454],[31097,40760,31137,41000]),
 ('bench-C2-right',[31750,40200,33004,41454],[32330,40700,32410,41100]),
 ('eastdeck-G2',[32141,37925,33395,39179],[32600,38190,32950,39027])]:
    im,pieces,missing=s.extract(frame);assert not missing,missing;assert im.size==(1254,1254)
    guide=D/(name+'-conditioned-v1-guide-native1254.png');assert not guide.exists();im.save(guide)
    local=[focus[0]-frame[0],focus[1]-frame[1],focus[2]-frame[0],focus[3]-frame[1]]
    fp=D/(name+'-current-focus-native.png');assert not fp.exists();im.crop(local).save(fp)
    rec={'name':name,'frameWorld':frame,'focusWorldBox':focus,'focusGuideBox':local,
         'guide':str(guide),'guideSha256':sha(guide),'focus':str(fp),'focusSha256':sha(fp),
         'sourcePieces':pieces,'nativeSize':[1254,1254],'resampling':False,'canonicalModified':False}
    guides.append(rec)
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'exact_current_core_guides_pending_visual_scope','guides':guides,'paidApiUsed':False,
 'canonicalSelectionsModified':False,'zoneProgressModified':False,'historicalAuditModified':False}
out=D/'current-native-guide-manifest-v1.json';assert not out.exists()
out.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':str(out),'guides':[{'name':r['name'],'guide':r['guide']} for r in guides]}))
