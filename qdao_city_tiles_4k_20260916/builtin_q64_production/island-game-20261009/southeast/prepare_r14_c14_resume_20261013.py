from workflow import *
import subprocess,sys,os
tid='r14_c14'
pf=ROOT/f'progress-{tid}.json'
if not pf.exists():write(pf,{'tile':tid,'status':'prepared','workingVersions':{},'generatedNativeCount':0,'actualModel':None})
env=dict(os.environ,ISLAND_PROGRESS_FILE=pf.name)
neighbors={'11':[],'14':[],'12':['11'],'13':['12','14'],'21':['11'],'24':['14'],'22':['21','12'],'23':['22','24','13'],'31':['21'],'34':['24'],'32':['31','22'],'33':['32','34','23'],'41':['31'],'44':['34'],'42':['41','32'],'43':['42','44','33']}
desc='Only continuous bright clear turquoise-blue sea, flowing hand-painted water facets and restrained pale caustics, same native detail scale and color as the supplemental water-material image. No solid object, shore, boat, dock, wood, land or vegetation. Where yellow appears at the extreme left of the first-column layout guide it is soft gold reflection on water from the off-crop sail; render reflected light only, never a solid yellow surface. Any black strip at the extreme right/bottom is OUTSIDE-MAP padding in the guide, not artwork: fill it with continued water. Guide is not final detail. Preserve the exact registered sharp water overlap in subsequent patches.'
for rc in sys.argv[1:]:
    pid=f'{tid}_p{rc}'
    assert not (ROOT/'native'/f'{pid}_v01.png').exists()
    ns=[f'{tid}_p{n}_{"v02" if n=="14" and (ROOT/"native"/f"{tid}_p14_v02.png").exists() else "v01"}.png' for n in neighbors[rc]]
    guide=ROOT/'guides'/f'{pid}.native-context-v01.png'
    if ns and not guide.exists():subprocess.run([sys.executable,str(ROOT/'r12_context.py'),pid,'v01',*ns],check=True,env=env,capture_output=True,text=True)
    argsfile=ROOT/'prompts'/f'{pid}_v01.args.json'
    if not argsfile.exists():
        r=subprocess.run([sys.executable,str(ROOT/'request.py'),pid,'v01',desc],check=True,env=env,capture_output=True,text=True)
        a=json.loads(r.stdout)
        water=ROOT/'native'/'r14_c12_p14_v01.png'
        reqfile=ROOT/'prompts'/f'{pid}_v01.request.json';req=read(reqfile)
        if not ns:
            a['referenced_image_paths'].insert(1,water.as_posix())
            a['prompt'] += '\nSupplemental attached image 2 is accepted nearby WATER MATERIAL only. It is not an adjacent coordinate crop. Match its painted wave size, crispness and blue/turquoise palette; do not copy its entire composition. Last three references keep their described roles.\n'
            req['references'].insert(1,{'file':water.as_posix(),'sha256':sha(water),'role':'WATER MATERIAL ONLY; not an adjacent coordinate reference'})
        else:
            a['prompt']=a['prompt'].replace('same native detail scale and color as the supplemental water-material image.','same native detail scale and color as the sharp registered overlap.')
            a['prompt']+='\nThe sharp strip defines water scale and palette; continue it smoothly across the blurry interior without retaining a straight source/guide edge. Yellow reflected light only at the leftmost boundary when the coordinate guide explicitly shows it.\n'
        Path(req['promptPath']).write_text(a['prompt'],encoding='utf-8')
        write(reqfile,req);write(argsfile,a)
    print(json.dumps({'patch':pid,'args':str(argsfile)}))
