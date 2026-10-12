from pathlib import Path
import json,numpy as np
import run_cross_with_strict_memo as m
P=Path(__file__).resolve().parent/"strict_memo_test_inputs";P.mkdir(exist_ok=True)
im=P/"synthetic.bin";rec=P/"record.json";dep=P/"dependency.bin"
im.write_bytes(b"test");rec.write_text('{"test":true}');dep.write_bytes(b"a")
calls=[]
def fake(image,record,seen):
 calls.append(1);m.r.file_info(image);m.r.read_json(record);m.r.file_info(dep)
 return np.array([list(dep.read_bytes())],dtype=np.uint8),dict(verified=True)
m.orig_validate=fake
a,_=m.validate(im,rec);b,_=m.validate(im,rec)
assert len(calls)==1 and np.array_equal(a,b)
b[0,0]=0;c,_=m.validate(im,rec);assert c[0,0]==97
dep.write_bytes(b"b");d,_=m.validate(im,rec);assert len(calls)==2 and d[0,0]==98
rec.write_text('{"test":false}');m.validate(im,rec);assert len(calls)==3
try:m.validate(im,rec,{rec.resolve()})
except ValueError:pass
else:raise AssertionError("cycle bypassed")
m.validate(im,rec,{dep.resolve()});assert len(calls)==4
print(json.dumps(dict(passed=6,stats=m.stats,scope="memo invalidation and copy/cycle behavior; not artwork acceptance")))

