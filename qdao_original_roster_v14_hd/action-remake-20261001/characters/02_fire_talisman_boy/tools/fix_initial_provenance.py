from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'records/attack-E-06-20261002-attempt-01.json'
r=json.loads(p.read_text(encoding='utf-8-sig'))
r['evidence']['hostOutputPath']='C:/Users/luyua/.codex/generated_images/01a0fcf5-e5d7-7461-80df-79c90391ec08/exec-b28fbc70-a49f-4082-a823-69202c29cf4e.png'
r['evidence']['importSourcePath']=r['native']['sourceFile']
r['evidence']['correctionNote']='恢复工具回执的真实宿主路径；项目 work 路径是其导入副本，SHA不变。'
for ref,role in zip(r['references'],['本地已提交角色身份与解剖持手','本地已提交E向idle，仅用于朝向；持手歧义不继承','designs已确认画法']): ref['role']=role
r['subsequentVisualReview']={'status':'rejected_requires_arm_connection_repair','date':'2026-10-02','reason':'整组复核推翻初次静态关键帧判断：E向前击时近侧可见肩袖连向铜铃，符扇接在远侧臂，解剖持手连接有误。旧初评留存用于审计，不代表当前验收。','replacement':'records/attack-E-06-20261002-attempt-03.json'}
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('initial provenance and subsequent review recorded')
