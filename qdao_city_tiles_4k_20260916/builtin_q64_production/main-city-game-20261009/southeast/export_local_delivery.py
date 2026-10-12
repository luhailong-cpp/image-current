"""Verify current native coverage and export byte-identical 4K candidates.

No model calls, artwork creation, resampling, or visual acceptance decisions.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, csv, os, uuid, sys
from PIL import Image

ZONE=Path(__file__).resolve().parent
DAY=sys.argv[1] if len(sys.argv)>1 else '20261012'
assert DAY.isdigit() and len(DAY)==8
OUT=ZONE/('delivery-'+DAY)
OLD='r13_c13'
OLD_SHA='db5f956694c700b16094eb532ad9097e8a54f4a19d14797325f6fbd0ca18971f'
PATCHES=[f'p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5)]

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temp,p)

def main():
    OUT.mkdir(exist_ok=True); (OUT/'candidates').mkdir(exist_ok=True)
    rows=[]; audit=[]; generated=[]; local_changes=[]
    for r in range(9,17):
        for c in range(9,17):
            name=f'r{r:02d}_c{c:02d}'; td=ZONE/name
            mapping=read(td/'active-native-map.json') if (td/'active-native-map.json').exists() else {}
            p=read(td/'progress.json') if (td/'progress.json').exists() else {}
            native_sources=[]
            for logical,version in sorted(mapping.items()):
                path=td/'native'/(version+'.png'); gp=Path(str(path)+'.generation.json')
                assert path.exists() and gp.exists(),(name,logical,'missing source or record')
                gen=read(gp); digest=sha(path)
                assert digest==gen['sha256'],(name,logical,'source hash')
                with Image.open(path) as im:
                    assert im.size==(1254,1254),(name,logical,'native dimensions')
                    assert im.mode in ('RGB','RGBA')
                    if im.mode=='RGBA': assert im.getchannel('A').getextrema()==(255,255)
                native_sources.append({'logicalPatch':logical,'version':version,'path':str(path),'sha256':digest,'generationRecord':str(gp),'recordSha256':sha(gp)})
            for gp in td.rglob('*generation.json') if td.exists() else []:
                generated.append({'tile':name,'record':str(gp),'recordSha256':sha(gp)})
            candidate=None; context=None; manifest=None
            if name==OLD:
                candidate=td/'candidate'/f'{OLD}-4k-candidate-repaired.png'
                context=td/'candidate'/f'{OLD}-context-4326-repaired.png'
                manifest=td/'candidate'/'replay-verification.json'
                assert sha(candidate)==OLD_SHA,'Historical core modified'
                p={'internalArtQA':'passed','internalSeamQA':'passed','externalNeighborSeamQA':'pending_external_joint_QA','formalAccepted':False}
            elif p.get('candidate'):
                candidate=Path(p['candidate']); context=Path(p['context'])
                manifest=Path(p['assemblyManifest']) if p.get('assemblyManifest') else None
            row={'tile':name,'coreBox':[(c-1)*4096,(r-1)*4096,c*4096,r*4096],
                 'activeNativeCount':len(mapping),'missingNativeCoordinates':[x for x in PATCHES if x not in mapping],
                 'candidate':None,'internalArtQA':p.get('internalArtQA','not_started'),
                 'internalSeamQA':p.get('internalSeamQA','not_reviewed'),
                 'externalNeighborSeamQA':p.get('externalNeighborSeamQA','unavailable'),
                 'formalAccepted':False,'status':'not_started' if not mapping else 'partial_native_coverage'}
            if candidate:
                digest=sha(candidate)
                with Image.open(candidate) as im:
                    assert im.size==(4096,4096); core=im.convert('RGB').tobytes()
                with Image.open(context) as im:
                    assert im.size==(4326,4326)
                    assert im.convert('RGB').crop((115,115,4211,4211)).tobytes()==core,'Context crop does not match'
                export=OUT/'candidates'/f'{name}-{digest[:12]}.png'
                if not export.exists(): shutil.copyfile(candidate,export)
                assert sha(export)==digest
                row.update(status='4k_candidate_pending_external_or_internal_QA',candidate={'path':str(candidate),'export':str(export),'sha256':digest,'pixels':[4096,4096]},context={'path':str(context),'sha256':sha(context)},manifest={'path':str(manifest),'sha256':sha(manifest)} if manifest and manifest.exists() else None)
            for side,dr,dc in [('north',-1,0),('east',0,1),('south',1,0),('west',0,-1)]:
                if candidate:
                    nr,nc=r+dr,c+dc
                    row.setdefault('externalEdges',[]).append({'direction':side,'neighbor':f'r{nr:02d}_c{nc:02d}' if 1<=nr<=16 and 1<=nc<=16 else None,'status':'not_formally_accepted'})
            lp=td/('production-resume-'+DAY+'.json')
            if not lp.exists():lp=td/'local-continuation-20261011.json'
            if lp.exists(): local_changes.append({'tile':name,'path':str(lp),'sha256':sha(lp),'report':read(lp)})
            audit.append({'tile':name,'verifiedActiveNativeSources':native_sources})
            rows.append(row)
    candidates=[r for r in rows if r['candidate']]
    corner_records=[{'tile':'joint_corner','record':str(g),'recordSha256':sha(g)} for d in ZONE.glob('corner-repair-*') for g in d.rglob('*generation.json')]
    generated.extend(corner_records)
    report={'schemaVersion':1,'updatedAtUtc':datetime.now(timezone.utc).isoformat(),
            'scope':'southeast rows9..16 columns9..16; 64 formal tiles','networkPermission':'user_confirmed_restored; success must be established by an actual saved builtin output',
            'plannedTileCount':64,'currentCandidateCount':len(candidates),'activeNativeCount':sum(x['activeNativeCount'] for x in rows),
            'fullyCovered4kCount':len(candidates),'notStartedTileCount':sum(x['activeNativeCount']==0 for x in rows),
            'partialNativeTileCount':sum(0<x['activeNativeCount']<16 for x in rows),
            'internalFullArtPassedCount':sum(x['internalArtQA']=='passed' for x in candidates),
            'internalSeamPassedCount':sum(x['internalSeamQA']=='passed' for x in candidates),
            'externalPendingTileCount':len(candidates),'externalPendingDirectedEdgeCount':4*len(candidates),
            'formalAcceptedCount':0,'allMapComplete':False,'recordedGenerationVersionCount':len(generated),
            'generationCountBasis':'Existing provenance records include superseded/rejected native versions; not an acceptance count.',
            'localSourceAudit':str(OUT/'active-native-audit.json'),'tileReports':local_changes,
            'tilesNeedingNewNativeCoordinates':[{'tile':x['tile'],'patches':x['missingNativeCoordinates']} for x in rows if x['missingNativeCoordinates']],
            'knownStructuralRepairQueue':[{'tile':'r13_c14','edge':'west','issue':'umbrella geometry and remaining paving/wood transitions; see current tile QA'},
             {'tile':'r14_c13','edge':'east','issue':'neighbor r14_c14 old candidate differs at multiple grout crossings; recheck latest neighbor'},
             {'tile':'r14_c14','edge':'internal, north, west','issue':'Several native grout repairs published; remaining transitions require current-version native-scale review'},
             {'tile':'r13_c15','edge':'north, east, south','issue':'Unified native repairs published; internal and west geometry locally reviewed, remaining neighbor joints pending'},
             {'tile':'r15_c13','edge':'east, south, west','issue':'Verified native halo24 north continuation independently reviewed with texture watch; remaining neighbor joints pending'},
             {'tile':'r14_c15','edge':'internal, north, west','issue':'Native 4K candidate assembled; duplicate stone railing and neighbor joints under full-scale review'},
             {'tile':'r15_c14','edge':'internal, north, west','issue':'Native 4K candidate assembled; local stone-grout ends and old/new border continuations under repair'},
             {'tile':'four_tile_corner','edge':'joint','issue':'first native source saved but broad trial rejected for texture/tone seam and perimeter ghosts; not promoted'}],
            'blockedOn':[],'workRemaining':'Generate missing native coordinates and repair/review existing structural seams. Exported candidates are not finished map tiles.',
            'artworkOperationsThisScript':'read, hash, integer crop comparison, byte-identical file copy only',
            'builtinOnly':True,'paidApiAllowed':False,'resizedFinalArt':False,'runtimeTestingPerformed':False,
            'deliveryIndex':str(OUT/'index.json'),'firstSuccessfulOutputAfterLatestNetworkRecovery':None}
    existing=ZONE/('local-continuation-'+DAY+'.json')
    round_path=ZONE/('production-resume-'+DAY+'.json')
    round_report=read(round_path) if round_path.exists() else {}
    if round_report.get('firstNewOutput'):
        report['firstSuccessfulOutputAfterLatestNetworkRecovery']=round_report['firstNewOutput']
    elif existing.exists():
        report['firstSuccessfulOutputAfterLatestNetworkRecovery']=read(existing).get('firstSuccessfulOutputAfterLatestNetworkRecovery')
    if round_report.get('networkStatus') in ('builtin_imagegen_succeeded_this_round','builtin_imagegen_succeeded_after_resume'):
        report['networkPermission']='builtin output successfully saved and hashed this round; no network blocker currently recorded'
    write(OUT/'active-native-audit.json',{'checkedAtUtc':report['updatedAtUtc'],'allActiveSourcesHashAndNativeDimensionsVerified':True,'tiles':audit})
    write(OUT/'generation-record-index.json',generated)
    write(OUT/'index.json',{'updatedAtUtc':report['updatedAtUtc'],'purpose':'True-coverage 4K candidate index; not formal delivery acceptance','tiles':rows})
    with (OUT/'index.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f); writer.writerow(['tile','status','active_native_count','missing_native_count','candidate_export','sha256','internal_art_qa','internal_seam_qa','external_qa','formal_accepted'])
        for row in rows: writer.writerow([row['tile'],row['status'],row['activeNativeCount'],len(row['missingNativeCoordinates']),(row['candidate'] or {}).get('export',''),(row['candidate'] or {}).get('sha256',''),row['internalArtQA'],row['internalSeamQA'],row['externalNeighborSeamQA'],False])
    write(existing,report)
    progress_path=ZONE/'progress.json'
    previous=read(progress_path) if progress_path.exists() else {}
    if previous:
        history=OUT/'status-history'; history.mkdir(exist_ok=True)
        backup=history/f'progress-{sha(progress_path)[:16]}.json'
        if not backup.exists(): shutil.copyfile(progress_path,backup)
    counts={name:sum(x['tile']==name for x in generated) for name in [x['tile'] for x in rows]}
    progress={**previous,'schemaVersion':3,'zone':'southeast','updatedAt':report['updatedAtUtc'],
       'status':'native_candidates_and_structural_seam_repairs_in_progress','generationStopped':False,
       'productionResume':str(round_path),
       'plannedTileCount':64,'startedTileCount':64-report['notStartedTileCount'],
       'notStartedTileCount':report['notStartedTileCount'],
       'generatedNativeCount':report['recordedGenerationVersionCount'],
       'generationCountBasis':report['generationCountBasis'],
       'jointRepairNativeCount':len(corner_records),'activeNativePatchCount':report['activeNativeCount'],
       'complete4kCandidateCount':len(candidates),'fullyCovered4kCount':len(candidates),
       'missingFullyCoveredTileCount':64-len(candidates),'internalPassed4kCount':report['internalFullArtPassedCount'],
       'internalSeamPassed4kCount':report['internalSeamPassedCount'],
       'internalPassCountBasis':'Only explicit full-art passed status counts; partial/local seam passes are not full tile approval.',
       'externalPassed4kCount':0,'formalAcceptedCount':0,'missingFormalTileCount':64,'underlyingTaskComplete':False,
       'builtinOnly':True,'paidApiAllowed':False,'resizeFinalArtAllowed':False,
       'tiles':[dict(x,recordedGeneratedNativeCount=counts[x['tile']],tileProgress=str(ZONE/x['tile']/'progress.json')) for x in rows if x['activeNativeCount']],
       'deliveryIndex':str(OUT/'index.json'),'localContinuationReport':str(existing),
       'nextStep':report['workRemaining']}
    write(progress_path,progress)
    if round_report:
        round_report.update(updatedAt=report['updatedAtUtc'],candidateCount=len(candidates),
           internalFullArtPassedCount=report['internalFullArtPassedCount'],formalAcceptedCount=0,
           currentTileActiveNativeCount=next((x['activeNativeCount'] for x in rows if x['tile']==str(round_report.get('currentRootCoordinate',round_report.get('currentCoordinate',''))).split('/')[0]),0),
           complete4kCandidateCount=len(candidates),remainingUnstartedTileCount=report['notStartedTileCount'],
           activeNativeCount=report['activeNativeCount'],notStartedTileCount=report['notStartedTileCount'],
           selectedCandidates=[{'tile':x['tile'],'candidate':x['candidate']['path'],'sha256':x['candidate']['sha256'],'internalArtQA':x['internalArtQA'],'externalQA':x['externalNeighborSeamQA'],'formalAccepted':False} for x in candidates],
           nextStep=report['workRemaining'],deliveryIndex=str(OUT/'index.json'),gitOperationsPerformed=False,sourceDeletionPerformed=False)
        write(round_path,round_report)
    print(json.dumps({k:report[k] for k in ['currentCandidateCount','activeNativeCount','notStartedTileCount','partialNativeTileCount','internalFullArtPassedCount','internalSeamPassedCount','formalAcceptedCount','deliveryIndex']}))

if __name__=='__main__': main()
