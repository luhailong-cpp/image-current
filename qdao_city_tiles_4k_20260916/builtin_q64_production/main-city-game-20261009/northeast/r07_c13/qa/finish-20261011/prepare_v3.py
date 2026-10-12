from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'apply-v2.py').read_text(encoding='utf-8')
s=s.replace("('m03-ridge',[1550,1500],[(478,577),(551,586),(576,691),(516,744),(477,718)])","('m03-ridge',[1550,1500],[(478,577),(551,586),(576,691),(516,744),(477,718)]),\n('m04-upper-pipe',[2445,-300],[(566,322),(786,322),(839,343),(839,464),(579,489),(551,444)])")
s=s.replace("name+'-v2.png'","name+'-v3.png'").replace("name+'-v2-integrated-100pct.png'","name+'-v3-integrated-100pct.png'")
s=s.replace("D/'replay-v2.json'","D/'replay-v3.json'").replace("D/'verification-v2.json'","D/'verification-v3.json'")
s=s.replace("b935db8e1e765a866c2a295d7e57b177f68f331ee4093331a2bb7c450c65b6a5","a01d4042c9c80ce0b7a757383128db2d8678fb71ac0984993716d765fd2fc1f0")
s=s.replace("D/'before-v2.candidate.png'","D/'before-v3.candidate.png'").replace("D/'before-v2.generation.json'","D/'before-v3.generation.json'")
q=D/'apply-v3.py';assert not q.exists();q.write_text(s,encoding='utf-8')

