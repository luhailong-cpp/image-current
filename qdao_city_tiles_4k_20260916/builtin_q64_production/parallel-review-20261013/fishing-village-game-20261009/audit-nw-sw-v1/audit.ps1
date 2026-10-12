$ErrorActionPreference = 'Stop'
$base = 'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\fishing-village-game-20261009'
$out = 'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-review-20261013\fishing-village-game-20261009\audit-nw-sw-v1'
$observed = @{}
$jsonCache = @{}
function Observe([string]$path, [string]$expected = '') {
    $full = [IO.Path]::GetFullPath($path)
    if (-not $full.StartsWith($base + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Read outside audit scope: $full" }
    if (-not $observed.ContainsKey($full)) {
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { $observed[$full] = [ordered]@{path=$full;exists=$false}; return $observed[$full] }
        $info = Get-Item -LiteralPath $full
        $rec = [ordered]@{path=$full;exists=$true;bytes=$info.Length;lastWriteUtc=$info.LastWriteTimeUtc.ToString('o');sha256=(Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()}
        if ($full.EndsWith('.png', [StringComparison]::OrdinalIgnoreCase)) {
            $stream=[IO.File]::OpenRead($full)
            try { $head = New-Object byte[] 24; $null=$stream.Read($head,0,24) } finally { $stream.Dispose() }
            $w=[uint32]$head[16]*16777216+[uint32]$head[17]*65536+[uint32]$head[18]*256+[uint32]$head[19]
            $h=[uint32]$head[20]*16777216+[uint32]$head[21]*65536+[uint32]$head[22]*256+[uint32]$head[23]
            $rec.dimensions=@($w,$h)
        }
        $observed[$full]=$rec
    }
    $result=[ordered]@{}
    foreach ($key in $observed[$full].Keys) { $result[$key]=$observed[$full][$key] }
    if ($expected) { $result.expectedSha256=$expected.ToLowerInvariant(); $result.hashMatchesExpected=($result.sha256 -eq $result.expectedSha256) }
    return $result
}
function ReadJson([string]$path) {
    $full=[IO.Path]::GetFullPath($path)
    if (-not $jsonCache.ContainsKey($full)) { $null=Observe $full; $jsonCache[$full]=Get-Content -LiteralPath $full -Raw | ConvertFrom-Json }
    return $jsonCache[$full]
}
function NativeRefs($node, $refs) {
    if ($null -eq $node -or $node -is [string] -or $node -is [ValueType]) { return }
    if ($node -is [Array]) { foreach ($item in $node) { NativeRefs $item $refs }; return }
    $p=$null
    if ($node.path -is [string]) { $p=$node.path } elseif ($node.file -is [string]) { $p=$node.file }
    if ($p -and $p -match '[/\\]native[/\\].+\.png$' -and [IO.Path]::GetFullPath($p).StartsWith($base, [StringComparison]::OrdinalIgnoreCase)) {
        $refs[$p]=[ordered]@{path=$p;expected=$node.sha256}
    }
    foreach ($prop in $node.PSObject.Properties) { NativeRefs $prop.Value $refs }
}
$nwIndex=ReadJson "$base\northwest\current-artifacts.json"
$nwInventory=ReadJson "$base\northwest\coordinate-inventory-current.json"
$nwProgress=ReadJson "$base\northwest\progress.json"
$contract=ReadJson "$base\production-contract.json"
$nwCandidates=@()
$nativeRefs=@{}
foreach($prop in $nwIndex.PSObject.Properties) {
    if($prop.Name -notmatch '^r\d{2}_c\d{2}$') { continue }
    $item=$prop.Value
    $qaPath=Join-Path "$base\northwest" $item.qa
    $assemblyPath=Join-Path "$base\northwest" $item.assembly
    $qa=ReadJson $qaPath
    $assembly=ReadJson $assemblyPath
    NativeRefs $assembly $nativeRefs
    $expected=''
    if($qa.candidate.sha256) { $expected=$qa.candidate.sha256 }
    elseif($nwProgress.currentCandidates.($prop.Name).candidateSha256) { $expected=$nwProgress.currentCandidates.($prop.Name).candidateSha256 }
    $nwCandidates += [ordered]@{
        coordinate=$prop.Name;adopted=$true;internalAccepted=$qa.internalAccepted;formalAccepted=$false;
        candidate=(Observe (Join-Path "$base\northwest" $item.candidate) $expected);
        assembly=(Observe $assemblyPath);qa=(Observe $qaPath);status=$item.status;
        boundaries=$qa.boundaries;northBoundaryAccepted=$qa.northBoundaryAccepted;southBoundaryAccepted=$qa.southBoundaryAccepted;
        eastBoundaryAccepted=$qa.eastBoundaryAccepted;westBoundaryAccepted=$qa.westBoundaryAccepted;
        sourceProof=$qa.sourceProof;nativeProof=$qa.nativeProof;
        reusePolicy='Existing root QA evidence only; this metadata audit did not repeat visual acceptance.'
    }
}
$nwPending=@()
foreach($rel in @('work-r02_c02/fixed-v2/r02_c02.assembly.json','work-r02_c02/patch-v3/r02_c02.assembly.json')) {
    $a=ReadJson (Join-Path "$base\northwest" $rel)
    NativeRefs $a $nativeRefs
    $candidatePath=$a.candidate.file
    if(-not $candidatePath) { $candidatePath=$a.candidate.path }
    $nwPending += [ordered]@{coordinate='r02_c02';adopted=$false;internalAccepted=$false;assembly=(Observe (Join-Path "$base\northwest" $rel));candidate=(Observe $candidatePath $a.candidate.sha256);status=$a.status}
}
$swLedger=ReadJson "$base\southwest\current-tile-ledger.json"
$swIndex=ReadJson "$base\southwest\art-delivery-index.json"
$swProgress=ReadJson "$base\southwest\progress.json"
$swCandidates=@()
foreach($t in $swLedger.tiles) {
    if(-not $t.current4096) { continue }
    $qa=$null
    if($t.artAudit.path) { $qa=ReadJson $t.artAudit.path }
    $trace=ReadJson $t.sourceTrace.path
    NativeRefs $trace $nativeRefs
    $swCandidates += [ordered]@{coordinate=$t.tile;nativeSlots=$t.nativeSlots;internalQa=$t.internalQa;artExport=$t.artExport;
        candidate=(Observe $t.current4096.path $t.current4096.sha256);sourceTrace=(Observe $t.sourceTrace.path $t.sourceTrace.sha256);
        artAudit=$(if($t.artAudit.path) { Observe $t.artAudit.path $t.artAudit.sha256 } else { $null });
        rootAuditStatus=$qa.status;rootAuditScope=$qa.scope;knownSharedEdgesQa=$t.knownSharedEdgesQa;outerEdgesPending=$t.outerEdgesPending;
        latestAdopted=$t.artExport;reusePolicy='Only recorded internal/shared edges; no cross-zone pass inferred.'}
}
$swRepairPath="$base\southwest\qa\repair-r11_c07-internal-v1-trace.json"
$swRepair=ReadJson $swRepairPath
NativeRefs $swRepair $nativeRefs
$swPendingRepair=[ordered]@{coordinate='r11_c07';adopted=$false;internalAccepted=$false;status=$swRepair.status;
    candidate=(Observe $swRepair.candidate.path $swRepair.candidate.sha256);trace=(Observe $swRepairPath);externalJoinsVerified=$swRepair.externalJoinsVerified;
    note='Later repair attempt exists; current ledger still explicitly selects base candidate. Preserve both.'}
$sourceChecks=@()
foreach($ref in $nativeRefs.Values) { $sourceChecks += Observe $ref.path $ref.expected }
$nwFull=@($nwInventory.fullyCoveredCoordinates | Sort-Object)
$nwInternal=@($nwCandidates | Where-Object {$_.internalAccepted} | ForEach-Object {$_.coordinate} | Sort-Object)
$swFull=@($swLedger.tiles | Where-Object {$_.coverage -eq 'full'} | ForEach-Object {$_.tile} | Sort-Object)
$swInternal=@($swLedger.tiles | Where-Object {$_.internalQa -eq 'passed'} | ForEach-Object {$_.tile} | Sort-Object)
$report=[ordered]@{
    createdAtUtc=[DateTime]::UtcNow.ToString('o');purpose='Read-only NW/SW coordinate/provenance audit for independent fishing-village review';
    auditScope=$base;writeScope=$out;imagesDecoded=$false;imagesGenerated=$false;gitUsed=$false;
    sourceChangePolicy='Invalidate this audit if any observed input hash changes. Current source hashes are snapshot evidence, not a lock.';
    geometry=[ordered]@{canvas=@(57344,57344);tile=@(4096,4096);rows=14;columns=14;tileCoreOrigin='[(column-1)*4096,(row-1)*4096]';
      core=1024;haloPerSide=115;adjacentNativeOverlap=230;expectedNative=@(1254,1254);expectedTileContext=@(4326,4326);
      noFinalResize=$true;assembly='Use each selected current candidate as native raster at 4096 integer offsets; do not substitute base pieces for repaired candidates.'};
    northwest=[ordered]@{targetCoordinates=49;fullyCoveredCoordinates=$nwFull;internallyPassedCoordinates=$nwInternal;coveredCount=$nwFull.Count;internalPassedCount=$nwInternal.Count;
      missingWholeCoordinates=$nwInventory.missingNativeWholeCoordinates;missingWholeCount=$nwInventory.missingNativeWholeCoordinates.Count;
      completePendingQaCoordinates=@('r02_c02');formalAcceptedCount=0;adoptedCandidates=$nwCandidates;unadoptedCandidates=$nwPending;
      staleLedgerNote='progress and coordinate-inventory at 03:09 UTC predate adopted r06_c04 final-v2 root QA at 04:20 UTC: inventory 11 internal is stale; actual latest root evidence supports 12.';
      partialCoordinateNote='r02_c05 has 8 native PNG versions covering only 6 unique core slots (s03_s01,s03_s02,s04_s01,s04_s02,s04_s03,s04_s04), with no fully covered candidate. r06_c02 has preparation only; no native PNG in its local work directory. No r07 or c07 fully covered coordinate.'};
    southwest=[ordered]@{targetCoordinates=49;fullyCoveredCoordinates=$swFull;internallyPassedCoordinates=$swInternal;coveredCount=$swFull.Count;internalPassedCount=$swInternal.Count;
      missingWholeCoordinates=@($swLedger.tiles|Where-Object {$_.coverage -ne 'full'}|ForEach-Object {$_.tile});
      missingWholeCount=@($swLedger.tiles|Where-Object {$_.coverage -ne 'full'}).Count;
      partialCoordinates=@($swLedger.tiles|Where-Object {$_.coverage -eq 'partial'}|Select-Object tile,nativeSlots);
      completePendingQaCoordinates=@('r11_c03','r11_c07');formalAcceptedCount=0;currentCandidates=$swCandidates;latestUnadoptedRepair=$swPendingRepair;
      knownRecordedPassedSharedEdges=$swProgress.sharedArtEdgesPassed;
      staleResumeNotes='README and some resumeBreakpoint notes are historical; use current files plus adoption audits. In particular r10_c07 v2 block audit and r11_c06 final-v5 adoption supersede old pending descriptions.'};
    crossZone=[ordered]@{
      nwNe='No NW c07 complete candidate; shared boundary cannot be checked from NW side.';
      nwSw='No NW r07 complete candidate; north side missing for every potential SW r08 boundary. SW r08_c06 complete alone; no pass claimed.';
      swSe=[ordered]@{bestExistingBoundaryCoordinates=@('r09_c07','r10_c07','r11_c07');missingWesternNativeCoordinates=@('r08_c07','r12_c07','r13_c07','r14_c07');
        priorCrossC08Evidence='Targeted rg in southwest/qa JSON and MD found no r10_c08/r11_c08/r12_c08/r13_c08 reference; southeast labels in old 2x2 manifests are local quadrants.';
        priority='Check adopted r10_c07 vs current SE r10_c08 and ledger base r11_c07 vs current SE r11_c08, plus row10/11 four-way junction. Keep r11_c07 repair separately pending owner adoption.'}
    };
    nativeSourceHeaderAndHashChecks=$sourceChecks;
    verificationSummary=[ordered]@{currentCandidateCount=$nwCandidates.Count+$swCandidates.Count;nativeSourceRefsChecked=$sourceChecks.Count;
      sourceHashMismatchCount=@($sourceChecks|Where-Object {$_.hashMatchesExpected -eq $false}).Count;
      nativeDimensionsHistogram=@($sourceChecks|Group-Object {$_.dimensions -join 'x'}|ForEach-Object {[ordered]@{dimensions=$_.Name;count=$_.Count}});
      limitation='No pixels compared or visual decisions made in this metadata-only audit. Existing reliable root QA is identified for reuse, with candidate hashes verified. 306 source checks cover directly referenced native PNGs in read assembly/trace JSON, not every historical source in the zone.'};
    observedInputs=@($observed.Values|Sort-Object path)
}
$changed=@()
foreach($inputRecord in $report.observedInputs) {
    if(-not $inputRecord.exists) { continue }
    $nowInfo=Get-Item -LiteralPath $inputRecord.path -ErrorAction SilentlyContinue
    if(-not $nowInfo -or $nowInfo.Length -ne $inputRecord.bytes -or $nowInfo.LastWriteTimeUtc.ToString('o') -ne $inputRecord.lastWriteUtc) {
        $changed += [ordered]@{path=$inputRecord.path;observedSha256=$inputRecord.sha256;reason='Input size/mtime changed or disappeared during audit';currentSha256=$(if($nowInfo){(Get-FileHash -LiteralPath $inputRecord.path -Algorithm SHA256).Hash.ToLowerInvariant()}else{$null})}
    }
}
$report.freshness=[ordered]@{checkedAtUtc=[DateTime]::UtcNow.ToString('o');method='Restat every observed input after hashing; recompute hash for changed size/mtime';stale=($changed.Count -gt 0);changedInputs=$changed}
New-Item -ItemType Directory -Path $out -Force | Out-Null
$report|ConvertTo-Json -Depth 30|Set-Content -LiteralPath "$out\audit-report.json" -Encoding utf8
@($nwCandidates+$swCandidates)|ForEach-Object {[pscustomobject]@{coordinate=$_.coordinate;zone=$(if($_.coordinate -match '^r0[1-7]_'){'northwest'}else{'southwest'});path=$_.candidate.path;sha256=$_.candidate.sha256;width=$_.candidate.dimensions[0];height=$_.candidate.dimensions[1];internalPassed=$(if($null -ne $_.internalAccepted){$_.internalAccepted}else{$_.internalQa -eq 'passed'})}}|Export-Csv -LiteralPath "$out\current-candidates.csv" -NoTypeInformation -Encoding utf8
[ordered]@{report="$out\audit-report.json";northwestCovered=$nwFull.Count;northwestInternal=$nwInternal.Count;southwestCovered=$swFull.Count;southwestInternal=$swInternal.Count;observedInputs=$observed.Count;nativeChecks=$sourceChecks.Count;nativeHashMismatches=$report.verificationSummary.sourceHashMismatchCount}|ConvertTo-Json -Compress
