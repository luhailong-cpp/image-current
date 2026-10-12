from pathlib import Path
import production_v2 as p
b=p.ZONE/"r05_c05"
report=b/"qa/subagent-internal-review-32393a518a6a.json"
candidate=b/"candidate/r05_c05-candidate-minimum-error-32393a518a6a.png"
e={"schemaVersion":1,"tile":"r05_c05","candidate":{"file":str(candidate),"sha256":p.sha(candidate)},"internalQA":{"status":"passed","actuallyViewed":True,"seamSegments":24,"junctions":9,"reviewer":"assemble_2x2_tooling independent actual-pixel review with root spot review","reviewBasis":"Initial 33 crops viewed; current 9 changed crops re-viewed, 24 SHA-identical inherited.","nonblockingObservations":["Minor material variation at y2048 segment02","Natural right-side wall corner and faint cap texture change retained"],"evidence":{"file":str(report),"sha256":p.sha(report)}},"externalQA":{"status":"pending","actuallyViewed":False,"reviewedSides":[],"worldBoundarySides":[]},"formalAccepted":False,"actualModel":None,"actualQuality":None,"clientMappingValidated":False,"capacity5000Validated":False,"updatedAt":p.now()}
p.write_json(b/"qa/acceptance.json",e,replace=True)
print("r05_c05 internal QA accepted; external pending")
