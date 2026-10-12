from workflow import *
tid='r12_c12';rev='sol-20261012-v01';q=ROOT/'qa'/f'{tid}-{rev}';f=ROOT/'tiles'/f'{tid}.candidate-{rev}.png'
h='afc8b32555ff1d7b19de32c2e54e446245d62867f6b7ed5490d0ed2dbe0189fc'
assert sha(f)==h
independent=q/'root-candidate-independent-review.json';ir=read(independent)
print(json.dumps({'independentReportKeys':list(ir.keys()),'independentReport':ir},ensure_ascii=False))
