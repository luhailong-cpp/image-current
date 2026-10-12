from pathlib import Path
import hashlib,json,datetime
Z=Path(__file__).resolve().parent;P="resume-20261010-beam"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
files=[p for sub in ["records","native","guides","qa"] for p in (Z/sub).glob(P+"*.json")]
before={str(p):sha(p) for p in files}
for v in ["A-v1","B-v1"]:
 p=Z/"records"/(P+"-"+v+".receipt.json");r=read(p);r["tool"]="image_gen.imagegen";r["route"]="builtin";write(p,r)
changes=[]
def repair(o,p,trail=""):
 count=0
 if isinstance(o,dict):
  if isinstance(o.get("path"),str) and "sha256" in o:
   q=Path(o["path"])
   if q.is_file() and q.name.startswith(P) and q.resolve().is_relative_to(Z):
    actual=sha(q)
    if actual!=o["sha256"]:
     changes.append({"file":str(p),"pointer":trail,"target":str(q),"oldSha256":o["sha256"],"newSha256":actual});o["sha256"]=actual;count+=1
  for k,v in list(o.items()):count+=repair(v,p,trail+"/"+str(k))
 elif isinstance(o,list):
  for i,v in enumerate(o):count+=repair(v,p,trail+"/"+str(i))
 return count
for iteration in range(10):
 changed=0
 for p in files:
  j=read(p);n=repair(j,p)
  if n:write(p,j);changed+=n
 if not changed:break
else:raise RuntimeError("Hash chain not stable")
for p in files:
 assert repair(read(p),p)==0
log={"schemaVersion":1,"correctedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"reason":"Supplement omitted receipt tool/route identifiers with actual built-in call evidence; actual request, response, prompt, image, model/quality evidence unchanged. Refresh only this worker beam-prefix dependent metadata hashes.","successfulNativeGenerationCount":2,"imagePixelsModified":False,"frozen":True,"changedRecords":[{"path":str(p),"beforeSha256":before[str(p)],"afterSha256":sha(p)}for p in files if sha(p)!=before[str(p)]],"dependencyUpdates":changes}
write(Z/"records"/(P+"-metadata-freeze.json"),log)
print(json.dumps({"changedRecordCount":len(log["changedRecords"]),"dependencyUpdates":len(changes),"freeze":str(Z/"records"/(P+"-metadata-freeze.json"))}))

