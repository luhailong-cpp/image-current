"""Refresh this zone only, applying the current reassigned coordinate exclusions."""
from pathlib import Path
import argparse
import production_v2 as p

def current_joint_delivery(tiles):
    """Count reviewed joint splits only while their selected sources are current."""
    candidates = sorted((p.ZONE / "joint-2x2-r05_c04-r06_c05").glob("*/delivery-summary.json"),
                        key=lambda f: f.stat().st_mtime, reverse=True)
    for summary_path in candidates:
        summary = p.read(summary_path)
        if summary.get("status") != "joint_milestone_internal_visual_qa_passed":
            continue
        manifest_path = Path(summary["assemblyManifest"]["file"])
        if p.sha(manifest_path) != summary["assemblyManifest"]["sha256"]:
            continue
        manifest = p.read(manifest_path)
        current = True
        for source in manifest["nativeSources"]:
            selected = p.selected_path(p.ZONE / source["tile"], source["id"])
            if not selected.is_file() or p.sha(selected) != source["sha256"]:
                current = False
                break
        if not current:
            continue
        by_tile = {tile["tile"]: tile for tile in tiles}
        for split in summary["tiles"]:
            path = Path(split["file"])
            if not path.is_file() or p.sha(path) != split["sha256"]:
                raise ValueError("Reviewed joint split changed: " + str(path))
            entry = by_tile[split["tile"]]
            entry.update({"completeCandidate": True, "currentCompleteCandidate": True,
                          "internalQAPassed": True, "formalAccepted": False,
                          "jointCandidate": split,
                          "jointReview": {"file": str(summary_path), "sha256": p.sha(summary_path)},
                          "outerBoundaryStatus": summary["outerBoundaryStatus"]})
        return {"file": str(summary_path), "sha256": p.sha(summary_path),
                "tileCount": len(summary["tiles"]), "blockingCount": summary["blockingCount"],
                "jointImage": summary["jointImage"],
                "packageFile": str(summary_path.parent / "northwest-2x2-4k-tiles.zip"),
                "wholeZoneComplete": False}
    return None

def current_bridge_deliveries(tiles):
    """Recognize reviewed native bridge assemblies without treating 19 as 16 sources."""
    deliveries = []
    by_tile = {tile['tile']: tile for tile in tiles}
    for summary_path in sorted(p.ZONE.glob('r??_c??/delivery-summary.json')):
        summary = p.read(summary_path)
        if not summary.get('additionalNativeBridgeCount'):
            continue
        tile = summary['tile']
        if tile not in by_tile or summary.get('internalQA', {}).get('status') != 'passed':
            continue
        if summary.get('bridgeBoundaryQA', {}).get('status') != 'passed':
            continue
        proof = summary.get('pixelProof', {})
        if proof.get('status') != 'passed' or proof.get('checkedPixels') != 4096 * 4096:
            continue
        refs = [summary['candidate'], summary['assemblyManifest'], summary['sourceIndex'], summary['config']]
        refs.extend(summary['evidence'].values())
        if not all(Path(r['file']).is_file() and p.sha(r['file']) == r['sha256'] for r in refs):
            continue
        manifest = p.read(summary['assemblyManifest']['file'])
        fixed = [s for s in manifest['nativeSources'] if s['id'].startswith('s') and 'row' in s]
        if len(fixed) != 16:
            continue
        if not all(p.sha(p.selected_path(p.ZONE / tile, s['id'])) == s['sha256'] for s in fixed):
            continue
        if not all(p.sha(s['file']) == s['sha256'] for s in manifest['nativeSources']):
            continue
        delivery = {'file': str(summary_path), 'sha256': p.sha(summary_path), 'tile': tile,
                    'candidate': summary['candidate'], 'wholeZoneComplete': False}
        by_tile[tile].update({'completeCandidate': True, 'currentCompleteCandidate': True,
                             'internalQAPassed': True, 'formalAccepted': False,
                             'bridgeCandidate': summary['candidate'], 'bridgeReview': delivery,
                             'outerBoundaryStatus': summary['externalQA']})
        deliveries.append(delivery)
    return deliveries

def current_native_deliveries(tiles):
    by_tile = {t['tile']:t for t in tiles}
    delivered = []
    for tile in ('r07_c05','r06_c07'):
        path = p.ZONE / tile / 'delivery-summary-20261012.json'
        if not path.is_file():
            continue
        summary = p.read(path)
        if not summary.get('internalQAPassed') or summary.get('verifiedPixels') != 4096 * 4096 or summary.get('unresolvedInternalBlockers'):
            continue
        refs = [summary['candidate'],summary['assemblyManifest'],summary['qaEvidence'],summary['acceptance']]
        if not all(Path(r['file']).is_file() and p.sha(r['file']) == r['sha256'] for r in refs):
            continue
        sources = summary['nativeSources']
        if not all(p.sha(s['file']) == s['sha256'] for s in sources):
            continue
        if not all(p.sha(p.selected_path(p.ZONE / tile,s['id'])) == s['sha256'] for s in sources[:16]):
            continue
        item = {'file':str(path),'sha256':p.sha(path),'tile':tile,'candidate':summary['candidate'],'wholeZoneComplete':False}
        by_tile[tile].update(completeCandidate=True,currentCompleteCandidate=True,internalQAPassed=True,formalAccepted=False,currentNativeDelivery=item)
        delivered.append(item)
    pending = p.ZONE / 'r07_c06/current-continuation-checkpoint-20261013.json'
    if pending.is_file():
        checkpoint = p.read(pending)
        registry_ref = checkpoint['registry']
        registry = p.read(registry_ref['file'])
        sources = registry['nativeSources']
        hashes = {s['sha256'] for s in sources}
        valid = p.sha(registry_ref['file']) == registry_ref['sha256'] and p.sha(checkpoint['candidate']['file']) == checkpoint['candidate']['sha256']
        valid = valid and all(p.sha(s['file']) == s['sha256'] for s in sources)
        valid = valid and all(p.sha(p.selected_path(p.ZONE / 'r07_c06',f's{r:02}_{c:02}')) in hashes for r in range(1,5) for c in range(1,5))
        if valid:
            by_tile['r07_c06'].update(completeCandidate=True,currentCompleteCandidate=True,internalQAPassed=False,formalAccepted=False,currentPendingCandidate={'file':str(pending),'sha256':p.sha(pending),'candidate':checkpoint['candidate'],'status':'needs_repair'})
    return delivered

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--active-tile", default="r06_c05")
    cli.add_argument("--next-step", default="Finish the connected 2x2 sources, review full native joints, then continue the remaining owned coordinates.")
    args = cli.parse_args()
    assignment_file = p.ZONE.parents[1] / "acceleration-20261010" / "assignments.json"
    data = p.read(assignment_file)
    assignment = next(a for a in data["assignments"] if a["id"] == "city_yamen_north" and a["previousZone"] == "northwest")
    excluded = set(assignment["coordinates"])
    parallel_file = p.ZONE.parents[3] / "docs/MAP_PARALLEL_SPLIT_20261013.json"
    parallel = p.read(parallel_file)
    reserved_batches = [b for b in parallel["batches"]
                        if b["owner"] == "01a12075-f5cf-7c30-9edc-ceb79ed8cfbd"
                        and b["status"] == "allocated_root_reserved"]
    for batch in reserved_batches:
        excluded.update(batch["tiles"])
    if args.active_tile in excluded:
        raise ValueError("Active tile belongs to another production worker: " + args.active_tile)
    result = p.aggregate_progress(args.active_tile, args.next_step)
    all_tiles = result["tiles"]
    tiles = [t for t in all_tiles if t["tile"] not in excluded]
    count = len(tiles)
    expected = count * 16
    joint_delivery = current_joint_delivery(tiles)
    bridge_deliveries = current_bridge_deliveries(tiles)
    native_deliveries = current_native_deliveries(tiles)
    result.update({
        "originalTileCount": len(all_tiles),
        "originalExpectedNativeCoreCount": len(all_tiles) * 16,
        "scopeAssignmentFile": str(assignment_file),
        "scopeAssignmentSHA256": p.sha(assignment_file),
        "parallelScopeAssignment": {"file": str(parallel_file), "sha256": p.sha(parallel_file),
                                    "reservedBatches": reserved_batches},
        "excludedCoordinates": sorted(excluded),
        "excludedCoordinateOwner": assignment["outputDirectory"],
        "effectiveOwnedTileCount": count,
        "tileCount": count,
        "expectedNativeCoreCount": expected,
        "tiles": tiles,
        "selectedNativeCount": sum(t["selectedAvailable"] for t in tiles),
        "selectedAvailableNativeCount": sum(t["selectedAvailable"] for t in tiles),
        "selectedUsableNativeCount": sum(t["selectedUsable"] for t in tiles),
        "selectedSourceProvenanceValidatedCount": sum(t["selectedUsable"] for t in tiles),
        "missingNativePatchCount": expected-sum(t["selectedUsable"] for t in tiles),
        "complete4kCandidateCount": sum(t["completeCandidate"] for t in tiles),
        "currentComplete4kCandidateCount": sum(t["currentCompleteCandidate"] for t in tiles),
        "internalQAPassedCount": sum(t["internalQAPassed"] for t in tiles),
        "formalAcceptedCount": sum(t["formalAccepted"] for t in tiles),
        "remainingTileCountWithoutCompleteCandidate": sum(not t["completeCandidate"] for t in tiles),
        "remainingTileCountWithoutCurrentCompleteCandidate": sum(not t["currentCompleteCandidate"] for t in tiles),
        "remainingTileCountWithoutFormalAcceptance": sum(not t["formalAccepted"] for t in tiles),
        "remainingTileCountWithoutFullUsableSourceCoverage": sum(t["selectedUsable"] != 16 for t in tiles),
        "generationOnHold": False,
        "runtimeWorkRequested": False,
        "worldSize": None,
        "capacity5000Validated": False,
        "currentJointDelivery": joint_delivery,
        "currentBridgeDeliveries": bridge_deliveries,
        "currentNativeDeliveries": native_deliveries,
    })
    result["status"] = "complete" if all(t["formalAccepted"] for t in tiles) else "in_progress"
    expanded = p.ZONE / 'joint-six-tile-review/ac2031be4f9bb37b/delivery-summary.json'
    if expanded.is_file():
        summary = p.read(expanded)
        audit = p.read(summary['sourceAudit']['file'])
        current = p.sha(summary['sourceAudit']['file']) == summary['sourceAudit']['sha256']
        current = current and all(p.sha(p.selected_path(p.ZONE / s['tile'], s['id'])) == s['sha256'] for s in audit['sources'])
        current = current and all(p.sha(s['file']) == s['sha256'] for s in summary['tiles'])
        if current:
            result['currentConnectedDelivery'] = {'file':str(expanded),'sha256':p.sha(expanded),'tileCount':6,'blockingCount':0,'packageFile':str(expanded.parent/'northwest-six-4k-tiles.zip'),'wholeZoneComplete':False}
    eight = p.ZONE / 'verified-eight-tiles-20261012/34b29d9d5291760f/delivery-summary.json'
    if eight.is_file():
        summary = p.read(eight)
        audit_path = eight.parent / 'source-validation.json'
        audit = p.read(audit_path)
        current = all(p.sha(s['file']) == s['sha256'] for s in audit['sources'])
        current = current and all(p.sha(p.selected_path(p.ZONE / s['tile'], s['id'])) == s['sha256'] for s in audit['sources'] if s.get('kind') == 'fixed_grid')
        current = current and all(p.sha(s['file']) == s['sha256'] for s in summary['tiles'])
        package = eight.parent / 'northwest-eight-4k-tiles.zip'
        current = current and p.sha(package) == '97ef050976cd234cd237e8d560b08199bc40772dd8ca4a3d96c69b232d5c415b'
        if current:
            result['currentVerifiedDelivery'] = {'file':str(eight),'sha256':p.sha(eight),'sourceAudit':{'file':str(audit_path),'sha256':p.sha(audit_path)},'tileCount':8,'blockingCount':0,'packageFile':str(package),'packageSHA256':p.sha(package),'wholeZoneComplete':False,'outerUnfinishedNeighborsPending':True}
    nine = p.ZONE / 'verified-nine-tiles-20261012-v2/9195bae2e10f72ba/delivery-summary.json'
    if nine.is_file():
        summary = p.read(nine)
        audit_path = Path(summary['sourceValidation']['file'])
        audit = p.read(audit_path)
        sources = audit['previousSources'] + audit['newSources']
        current = p.sha(audit_path) == summary['sourceValidation']['sha256']
        current = current and all(p.sha(s['file']) == s['sha256'] for s in sources)
        current = current and all(p.sha(p.selected_path(p.ZONE / s['tile'], s['id'])) == s['sha256'] for s in sources if s.get('kind') == 'fixed_grid' or s in audit['newSources'])
        current = current and all(p.sha(s['file']) == s['sha256'] for s in summary['tiles'])
        package = nine.parent / 'northwest-nine-4k-tiles.zip'
        current = current and p.sha(package) == '7af0f0f710740dbb19be01f861a8ab5e71660a9033f707e2404e402aa072c9b5'
        if current:
            result['currentVerifiedDelivery'] = {'file':str(nine),'sha256':p.sha(nine),'sourceAudit':{'file':str(audit_path),'sha256':p.sha(audit_path)},'tileCount':9,'blockingCount':0,'packageFile':str(package),'packageSHA256':p.sha(package),'wholeZoneComplete':False,'outerUnfinishedNeighborsPending':True,'allArchivedJsonStrictlyParsed':True}
    eleven = p.ZONE / 'verified-eleven-tiles-20261012/2f0946e391eb1655/package.json'
    if eleven.is_file():
        package = p.read(eleven)
        summary = p.read(package['summary']['file'])
        audit = p.read(package['sourceValidation']['file'])
        inherited_ref = audit['inheritedNineSourceAudit']
        inherited = p.read(inherited_ref['file'])
        sources = inherited['previousSources'] + inherited['newSources'] + audit['newSources']
        current = p.sha(package['summary']['file']) == package['summary']['sha256'] and p.sha(package['sourceValidation']['file']) == package['sourceValidation']['sha256'] and p.sha(inherited_ref['file']) == inherited_ref['sha256']
        current = current and all(p.sha(s['file']) == s['sha256'] for s in sources) and all(p.sha(s['file']) == s['sha256'] for s in summary['tiles'])
        current = current and p.sha(package['file']) == package['sha256']
        if current:
            result['currentVerifiedDelivery'] = {'file':package['summary']['file'],'sha256':package['summary']['sha256'],'sourceAudit':package['sourceValidation'],'tileCount':11,'blockingCountWithinDeliveredTiles':0,'packageFile':package['file'],'packageSHA256':package['sha256'],'pngOnlyPackageFile':str(p.ZONE/'verified-eleven-png-only-20261013/northwest-eleven-4k-pngs.zip'),'wholeZoneComplete':False,'outerUnfinishedNeighborsPending':True,'allArchivedJsonStrictlyParsed':True}
    result['currentScopeCounts'] = {'deduplicatedTargetTiles':count,'tilesWithAll16NativePatches':sum(t['selectedUsable']==16 for t in tiles),'internallyPassedTiles':result['internalQAPassedCount'],'tilesStillMissingNativePatches':sum(t['selectedUsable']!=16 for t in tiles),'fullSourceTilesPendingInternalRepairOrReview':sum(t['selectedUsable']==16 and not t['internalQAPassed'] for t in tiles),'missingNativePatches':result['missingNativePatchCount'],'externalPerimeterPendingDoesNotCountAsUndrawn':True}
    hold = p.ZONE / 'generation-hold-current-model-requirement-20261012.json'
    if hold.is_file():
        result['generationOnHold'] = True
        result['generationHold'] = {'file':str(hold),'sha256':p.sha(hold)}
        result['status'] = 'local_work_in_progress_new_generation_paused'
    policy = p.ZONE / 'generation-policy-current-20261013.json'
    if policy.is_file():
        policy_data = p.read(policy)
        if policy_data.get('strictMandatory25HoldRevoked') and policy_data.get('newGenerationAllowed'):
            result['generationOnHold'] = False
            result['historicalGenerationHold'] = result.pop('generationHold',None)
            result['currentGenerationPolicy'] = {'file':str(policy),'sha256':p.sha(policy)}
            result['status'] = 'in_progress'
    tool_status = p.ZONE / 'generation-tool-status-current.json'
    if tool_status.is_file():
        observed = p.read(tool_status)
        result['currentGenerationToolStatus'] = {'file':str(tool_status),'sha256':p.sha(tool_status)}
        if observed.get('networkPermissionRevoked'):
            result['status'] = 'incomplete_native_generation_blocked_by_application_network_permission'
            result['generationToolBlocked'] = True
            result['generationToolBlocker'] = observed['error']
    p.write_json(p.ZONE / "progress.json", result, replace=True)
    print({k: result[k] for k in ("tileCount","generatedNativeCount","selectedUsableNativeCount","complete4kCandidateCount","internalQAPassedCount","formalAcceptedCount","missingNativePatchCount")})

if __name__ == "__main__":
    main()
