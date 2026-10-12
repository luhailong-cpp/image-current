from repair import *
ns=base();old=ns['pair'].copy();old[:,4096:]=np.array(Image.open(R/'tiles/r03_c03.candidate-repair-v5.png').convert('RGB'))
b=[8010,9360,8370,9920];a=old[b[1]-8192:b[3]-8192,b[0]-4096:b[2]-4096];Image.fromarray(a).save(Q/'qa-v09-lamp-boundary-before.100pct.png')
