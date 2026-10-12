import sys,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));import west_sol as w
items=[]
for p,v in [('r06_c11_p24','v2'),('r06_c11_p34','v2')]+[('r06_c11_p44','v'+str(i)) for i in range(2,6)]:
 rp=w.R/f'{p}-{v}.receipt.json';receipt=w.read(rp);np=w.Z/f'native/{p}-{v}-west_sol.png';genp=Path(str(np)+'.generation.json');gen=w.read(genp)
 host=gen['source']['path'];assert w.sha(host)==w.sha(np)==gen['sha256']
 assert host.replace(chr(92),'/') in receipt['output_hint'].replace(chr(92),'/')
 assert w.sha(rp)==gen['receipt']['sha256']
 req=receipt.get('request',receipt.get('actualRequest'));args=w.read(w.R/f'{p}-{v}.actual-arguments.json');assert req==args
 items.append(dict(patchId=p,version=v,tool='image_gen.imagegen',route='builtin',outcome='returned image_url and output_hint; PNG saved byte-for-byte',actualModel=None,actualQuality=None,receipt=w.ref(rp),requestField='actualRequest' if 'actualRequest' in receipt else 'request',actualReturnedTextField='output_hint',actualReturnedText=receipt['output_hint'],returnedKeys=receipt['returnedKeys'],sourceHost=w.ref(host),workspaceNative=w.ref(np),generation=w.ref(genp),verification='Original receipt and generation receipt hash unchanged. Arguments match receipt; host and workspace PNG SHA256 equal.'))
out=w.R/'receipt-route-evidence-20261012-v1.json';w.write(out,dict(schemaVersion=1,checkedAtUtc=w.now(),preservesOriginalReceiptAndGenerationHashes=True,items=items));print(json.dumps(w.ref(out)))
