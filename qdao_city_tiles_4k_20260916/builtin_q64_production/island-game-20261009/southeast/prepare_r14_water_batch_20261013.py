from workflow import *
import sys,subprocess,os
tid='r14_c12'
d=read(ROOT/f'progress-{tid}.json')
for rc in ['11','12','13','14','21','22','24','23','31','32','33','34','41','42','43','44']:
    p=ROOT/'native'/f'{tid}_p{rc}_v01.png'
    if p.exists():
        assert Image.open(p).size==(1254,1254)
        d.setdefault('workingVersions',{})[rc]='v01'
d.update(updatedAt=now(),generatedNativeCount=len(d['workingVersions']),status='native_received',inFlight=False,inFlightRequests=[],nextStep='Continue native open-water patches and inspect actual 4K joins')
write(ROOT/f'progress-{tid}.json',d)
neighbors={'23':['r14_c12_p22_v01.png','r14_c12_p24_v01.png','r14_c12_p13_v01.png'],'31':['r14_c12_p21_v01.png'],'32':['r14_c12_p22_v01.png'],'34':['r14_c12_p24_v01.png'],'33':['r14_c12_p32_v01.png','r14_c12_p34_v01.png','r14_c12_p23_v01.png'],'41':['r14_c12_p31_v01.png'],'42':['r14_c12_p32_v01.png'],'44':['r14_c12_p34_v01.png'],'43':['r14_c12_p42_v01.png','r14_c12_p44_v01.png','r14_c12_p33_v01.png']}
env=dict(os.environ,ISLAND_PROGRESS_FILE=f'progress-{tid}.json')
desc='Entire native crop is uninterrupted bright clear turquoise-blue sea with softly painted flowing wave facets and restrained white caustics. Existing sharp neighbor strips in the guide are registered anchors; continue their scale, color and light smoothly through the blurry interior. This crop contains NO dock, wood, pillar, rock, island, boat, solid object or vegetation. Do not copy an entire previous tile into this crop. Natural open water only; faint gold reflection only where actually present in a sharp anchor, fading softly with distance.'
for rc in sys.argv[1:]:
    pid=f'{tid}_p{rc}'
    assert not (ROOT/'native'/f'{pid}_v01.png').exists()
    guide=ROOT/'guides'/f'{pid}.native-context-v01.png'
    if not guide.exists():subprocess.run([sys.executable,str(ROOT/'r12_context.py'),pid,'v01',*neighbors[rc]],check=True,env=env,capture_output=True,text=True)
    af=ROOT/'prompts'/f'{pid}_v01.args.json'
    if not af.exists():
        result=subprocess.run([sys.executable,str(ROOT/'request.py'),pid,'v01',desc],check=True,env=env,capture_output=True,text=True)
        write(af,json.loads(result.stdout))
    print(json.dumps({'patch':pid,'guide':str(guide),'args':str(af)}))
