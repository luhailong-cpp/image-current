from pathlib import Path
Z=Path(__file__).resolve().parent
s=(Z/'inspect_connected_2x2.py').read_text(encoding='utf-8')
s=s.replace("OUT=ZONE/'qa/connected-2x2-20261010'\nIDS=['r05_c13','r05_c14','r06_c13','r06_c14']\nparser=argparse.ArgumentParser()","parser=argparse.ArgumentParser()\nparser.add_argument('--top-row',type=int,required=True)\nparser.add_argument('--left-col',type=int,required=True)")
s=s.replace("args=parser.parse_args()","args=parser.parse_args()\nassert 1<=args.top_row<=7 and 9<=args.left_col<=15, 'Group must stay in northeast ownership'\nIDS=[f'r{r:02}_c{c:02}' for r in (args.top_row,args.top_row+1) for c in (args.left_col,args.left_col+1)]\nOUT=ZONE/f'qa/connected-group-{IDS[0]}-{IDS[3]}'")
s=s.replace("[('r05_c13','r05_c14','north-west-east'),('r06_c13','r06_c14','south-west-east')]","[(IDS[0],IDS[1],'north-west-east'),(IDS[2],IDS[3],'south-west-east')]")
s=s.replace("[('r05_c13','r06_c13','west-north-south'),('r05_c14','r06_c14','east-north-south')]","[(IDS[0],IDS[2],'west-north-south'),(IDS[1],IDS[3],'east-north-south')]")
s=s.replace("[('r05_c13',(3469,3469,4096,4096),(0,0)),('r05_c14',(0,3469,627,4096),(627,0)),('r06_c13',(3469,0,4096,627),(0,627)),('r06_c14',(0,0,627,627),(627,627))]","[(IDS[0],(3469,3469,4096,4096),(0,0)),(IDS[1],(0,3469,627,4096),(627,0)),(IDS[2],(3469,0,4096,627),(0,627)),(IDS[3],(0,0,627,627),(627,627))]")
s=s.replace("'worldBox':[49152,16384,57344,24576]","'worldBox':[(args.left_col-1)*4096,(args.top_row-1)*4096,(args.left_col+1)*4096,(args.top_row+1)*4096]")
s=s.replace("[('r05_c13','r05_c14'),('r06_c13','r06_c14'),('r05_c13','r06_c13'),('r05_c14','r06_c14')]","[(IDS[0],IDS[1]),(IDS[2],IDS[3]),(IDS[0],IDS[2]),(IDS[1],IDS[3])]")
assert "'r05_c13'" not in s and "'r06_c14'" not in s
out=Z/'inspect_connected_group.py';assert not out.exists();out.write_text(s,encoding='utf-8')
print(str(out))

