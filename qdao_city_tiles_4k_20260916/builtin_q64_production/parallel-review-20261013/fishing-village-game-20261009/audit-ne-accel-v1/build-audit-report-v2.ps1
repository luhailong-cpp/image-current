$ErrorActionPreference='Stop'
$map='D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\fishing-village-game-20261009'
$out='D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-review-20261013\fishing-village-game-20261009\audit-ne-accel-v1'
function Audit-Json([string]$p){Get-Content -LiteralPath $p -Raw|ConvertFrom-Json}
function Audit-Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function Audit-Ref([string]$p){$f=Get-Item -LiteralPath $p;[ordered]@{path=$f.FullName;sha256=(Audit-Hash $p);bytes=$f.Length;lastWriteTimeUtc=$f.LastWriteTimeUtc.ToString('o')}}
function Audit-Dim([string]$p){$s=[System.IO.File]::OpenRead($p);try{$b=New-Object byte[] 24;[void]$s.Read($b,0,24)}finally{$s.Dispose()};@(([uint32]$b[16]*16777216+[uint32]$b[17]*65536+[uint32]$b[18]*256+[uint32]$b[19]),([uint32]$b[20]*16777216+[uint32]$b[21]*65536+[uint32]$b[22]*256+[uint32]$b[23]))}
$contract=Audit-Json (Join-Path $map 'production-contract.json')
$assignmentPath='D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\acceleration-20261010\assignments.json'
$assignment=(Audit-Json $assignmentPath).assignments|Where-Object {$_.id -eq 'village_jewelry_approach'}
$handoff=@($assignment.coordinates)
$all=@(for($tr=1;$tr -le 7;$tr++){for($tc=8;$tc -le 14;$tc++){'r{0:d2}_c{1:d2}' -f $tr,$tc}})
$owned=@($all|Where-Object {$_ -notin $handoff})
$raw=@{}
$nativeInventory=@()
foreach($f in (Get-ChildItem -LiteralPath (Join-Path $map 'northeast\native') -File -Filter '*.png')){
 if($f.Name -match '^(r\d{2}_c\d{2})_p([1-4][1-4])(?:-|\.)'){
  $tile=$Matches[1];$co=$Matches[2]
  if(-not $raw.ContainsKey($tile)){$raw[$tile]=@{}}
  if(-not $raw[$tile].ContainsKey($co)){$raw[$tile][$co]=@()}
  $raw[$tile][$co]+=$f.FullName
  $nativeInventory+=[ordered]@{tile=$tile;coordinate=$co;path=$f.FullName;bytes=$f.Length;lastWriteTimeUtc=$f.LastWriteTimeUtc.ToString('o')}
 }
}
$selectionMap=[ordered]@{
'r05_c12'='r05_c12.selection-root-v2.json';'r05_c13'='r05_c13.selection-sol-v3.json';'r05_c14'='r05_c14.selection-proposed-v4.json';'r06_c12'='r06_c12.selection-closure-v5.json';'r06_c13'='r06_c13.selection-proposed-v1.json';'r06_c14'='r06_c14.selection-proposed-v1.json';'r07_c12'='r07_c12.selection-closure-v5.json';'r07_c13'='r07_c13.selection-west-v4.json';'r07_c14'='r07_c14.selection-v1.json';'r04_c12'='r04_c12.working-selection.json';'r04_c14'='r04_c14.working-selection.json';'r06_c11'='west_sol\r06_c11.selected.json'
}
$selected=@{}
$selectionRecords=@()
$selectedNatives=@()
foreach($entry in $selectionMap.GetEnumerator()){
 $sp=Join-Path $map ('northeast\records\'+$entry.Value);$s=Audit-Json $sp;$selectionRecords+=Audit-Ref $sp
 $items=if($s.patches){$s.patches}else{$s}
 $selected[$entry.Key]=@()
 foreach($p in $items.PSObject.Properties){
  if($p.Name -notmatch '_p([1-4][1-4])$'){continue}
  $co=$Matches[1];$selected[$entry.Key]+=$co
  $value=$p.Value;$expected=$null
  if($value -is [string]){$path=if($value.StartsWith('native/')){Join-Path $map ('northeast\'+$value)}else{Join-Path $map ('northeast\native\'+$value)}}else{$path=$value.path;$expected=$value.sha256}
  $f=Get-Item -LiteralPath $path
  $actual=Audit-Hash $path
  $selectedNatives+=[ordered]@{patchId=$p.Name;path=$f.FullName;sha256=$actual;expectedSha256=$expected;hashMatches=if($expected){$actual -eq $expected}else{$null};dimensions=(Audit-Dim $path);selectionPath=$sp}
 }
}
$coverage=@()
foreach($t in $all){
 $rawCoords=if($raw.ContainsKey($t)){@($raw[$t].Keys|Sort-Object)}else{@()}
 $selCoords=if($selected.ContainsKey($t)){@($selected[$t]|Sort-Object)}else{@()}
 if($t -in $handoff){$rawCoords=@('11','12','13','14','21','22','23','24','31','32','33','34','41','42','43','44');$selCoords=$rawCoords}
 $missing=@(for($sr=1;$sr -le 4;$sr++){for($sc=1;$sc -le 4;$sc++){$co="$sr$sc";if($co -notin $rawCoords){'p'+$co}}})
 $notSelected=@(for($sr=1;$sr -le 4;$sr++){for($sc=1;$sc -le 4;$sc++){$co="$sr$sc";if($co -notin $selCoords){'p'+$co}}})
 $coverage+=[ordered]@{tile=$t;owner=if($t -in $handoff){'accelerated-jewelry-approach'}else{'northeast'};rawAvailableCoordinates=$rawCoords;selectedCoordinates=$selCoords;rawCount=$rawCoords.Count;selectedCount=$selCoords.Count;missingRawCoordinates=$missing;unselectedCoordinates=$notSelected;formalAccepted=$false}
}
$v=Audit-Json (Join-Path $out 'verified-sources-v1.json')
$privateCandidatePath=Join-Path $map 'northeast\tiles\r05_c14.candidate-v4.png'
$private=Audit-Ref $privateCandidatePath;$private.tile='r05_c14';$private.dimensions=Audit-Dim $privateCandidatePath;$private.owner='northeast';$private.explicitActiveSelection=$false;$private.generatorSelfReviewPassed=$true;$private.independentReviewPassed=$false
$qaPaths=@(
'northeast\qa\r06_c12-closure-v5\internal-review-summary.json',
'northeast\qa\r06_c13-v1\internal-review-summary.json',
'northeast\qa\r07_c12-closure-v5\internal-review-summary.json',
'northeast\qa\r07_c13-west-v4\internal-review-summary.json',
'northeast\qa\r06_c14-v1\root-internal-review-complete-20261012.json',
'northeast\qa\r05_c12-root-v2\internal-review-summary.json',
'northeast\qa\r05_c13-sol-v3\internal-review-summary.json',
'northeast\qa\r05_c12-root-v2\west-neighbor-QA\root-initial-review.json',
'northeast\qa\r05_c12-root-v2\external-neighbor-QA\root-review-summary.json',
'northeast\qa\first-block-closure-v5\root-shared-edge-review.json',
'northeast\qa\r05_c14-v4\self-review.json',
'accelerated-jewelry-approach\resume-20261012\root-final-review.json',
'accelerated-jewelry-approach\resume-20261012\provenance-audit.json',
'accelerated-jewelry-approach\resume-20261012\production-summary.json')
$qa=@()
foreach($p in $qaPaths){$path=Join-Path $map $p;$j=Audit-Json $path;$q=Audit-Ref $path;$q.summary=[ordered]@{candidate=$j.candidate;candidateSha256=$j.candidateSha256;internalNativeQAPassed=$j.internalNativeQAPassed;status=$j.status;scope=$j.scope;counts=$j.counts;formalAccepted=$j.formalAccepted;repairRequired=$j.repairRequired;westPassed=$j.westPassed;regionNativeReviewCount=$j.regionNativeReviewCount;blockingFindings=$j.blockingFindings};$qa+=$q}
$cross=@()
$am=Audit-Json (Join-Path $map 'accelerated-jewelry-approach\resume-20261012\candidate-manifest.json')
foreach($pair in $am.exteriorSeamsPending){$near=$coverage|Where-Object{$_.tile -eq $pair.neighbor};$edge=if($pair.edge -eq 'east'){'west'}elseif($pair.edge -eq 'west'){'east'}elseif($pair.edge -eq 'north'){'south'}else{'north'}
 $needed=if($edge -eq 'west'){@('11','21','31','41')}elseif($edge -eq 'east'){@('14','24','34','44')}elseif($edge -eq 'north'){@('11','12','13','14')}else{@('41','42','43','44')}
 $have=@($needed|Where-Object {$_ -in $near.selectedCoordinates})
 $cross+=[ordered]@{tile=$pair.tile;edge=$pair.edge;neighbor=$pair.neighbor;neighborEdge=$edge;neighborSelectedBoundaryCoordinates=$have;completeNeighborBoundary=($have.Count -eq 4);fullNeighborCandidateAvailable=($near.rawCount -eq 16);status=if($pair.neighbor -eq 'r05_c12'){'known_roof_material_transition_requires_review_and_AI_repair'}elseif($have.Count){'partial_native_boundary_available_unreviewed_by_this_auditor'}else{'neighbor_sources_missing'}}
}
$ownedCoverage=@($coverage|Where-Object {$_.owner -eq 'northeast'})
$complete=@($coverage|Where-Object {$_.rawCount -eq 16})
$report=[ordered]@{
schemaVersion=1;auditedAtUtc=[datetime]::UtcNow.ToString('o');scope='Northeast 49-tile sector including 6 exclusive accelerated coordinates; metadata/hash audit only';inputs=@((Audit-Ref (Join-Path $map 'production-contract.json')),(Audit-Ref $assignmentPath),(Audit-Ref (Join-Path $map 'northeast\records\active-candidates.json')),(Audit-Ref (Join-Path $map 'northeast\progress.json')),(Audit-Ref (Join-Path $map 'northeast\records\production-census-20261010.json')),(Audit-Ref (Join-Path $map 'accelerated-jewelry-approach\resume-20261012\candidate-manifest.json')));ownership=[ordered]@{sectorTileCount=49;northeastOwnedTarget=43;exclusiveAcceleratedCoordinates=$handoff;countHandoffOnlyOnce=$true};coverageDefinition='Available raw coordinate files include retained rejected variants; existence is not acceptance. Selected base coordinates may have additional documented native repair contributions.';coverage=$coverage;counts=[ordered]@{neOwnedRawCoordinates=($ownedCoverage|Measure-Object rawCount -Sum).Sum;neOwnedSelectedBaseCoordinates=($ownedCoverage|Measure-Object selectedCount -Sum).Sum;neOwnedMissingRawCoordinates=($ownedCoverage|ForEach-Object{$_.missingRawCoordinates.Count}|Measure-Object -Sum).Sum;neOwnedRawFullyCoveredTiles=@($ownedCoverage|Where-Object{$_.rawCount -eq 16}).Count;sectorCompleteCandidateTileCount=$complete.Count;neExplicitActiveCandidateCount=8;nePrivateCompleteCandidateCount=1;acceleratedCompleteCandidateCount=6;rootIndependentInternalPassedNeTileCount=7;formalAcceptedCount=0};explicitVerifiedCandidates=$v.candidates;privateCompleteCandidate=$private;selectedNatives=$selectedNatives;selectionRecords=$selectionRecords;rawNativeInventory=$nativeInventory;qaEvidence=$qa;crossAccelerationBoundaries=$cross;assemblyGeometry=[ordered]@{formalTilePixels=@(4096,4096);corePixels=1024;patchGrid=@(4,4);nativePixels=@(1254,1254);haloPixels=115;nativeCoreCrop=@(115,115,1139,1139);nativeCoreStep=1024;adjacentNativeOverlap=230;origin='top-left; 1-based tile indices';tileOrigin='[(column-1)*4096,(row-1)*4096]';sourceFinalAssembly='1:1 integer crop and opaque paste; retain recorded local native repairs; no resize or filling';sixTileRegion=$v.existingSixTileRegion};recordedReferenceHashes=[ordered]@{layout=$contract.layoutSha256;detail=$contract.detailSha256;style=$contract.primaryStyleSha256;verification='Contract hashes match inspected recent generation metadata; external reference files not re-opened due audit read scope.'};reliableReuse=[ordered]@{acceleratedRegion='8192x12288 exact-paste region matches current manifest SHA and six source SHA checks; existing root native intertile QA30 passed,13 fresh/17 exact inherited';northeastFirstBlock='r06c12/c13+r07c12/c13 has source-pinned internal summaries and17 shared-edge/junction checks;12 equal reused/5 fresh';r05c13='Latest independent49 native QA pass is newer than progress summary';r06c14='49 internal checks passed; external final closure remains pending'};knownIssues=@([ordered]@{location='r05_c11 east / r05_c12 west, segment r2 and junction r1';issue='straight blue-roof highlight/material change after p21-v4; roof arcs align';status='requires AI repair after verified GPT Image2.5 route becomes available';evidence='northeast/qa/r05_c12-root-v2/west-neighbor-QA/root-initial-review.json'},[ordered]@{location='r05_c14-v4 internal p13-p23 and south segment/junction c4';issue='generator identifies minor rock facet/highlight watch points; independent review pending';status='do not promote self-review to independent acceptance'},[ordered]@{location='r07_c13-west-v4 worldX49037 worldY26624..27648';issue='independent delta review finds minor texture/tone and a few pixels printed-fish/rim offset, judged nonblocking';status='record retained; not silently removed'});staleRecordFindings=@('NE progress/census timestamp02:33UTC predates r04c12 p32/p22/p12/p43 raw arrivals and latest r05c13 independent review','r04c12 p43 exists but is pending visual review and absent from working selection; do not auto-select','accelerated manifest fullNeighborCandidatesAvailable0 checkpoint is historical; r05c12 now exists and partial r04c12/r06c11 boundaries exist','accelerated tile-level r05c11 status/remainingWork still mentions old shared-west repair; currentCandidateQA final-v4 and current region manifest supersede that text');stalenessPolicy='If any pinned input/candidate/native hash changes, conclusions for dependent boundaries expire; retained raw inventory is a time-stamped snapshot, not a live production index.';limits=@('No image visual QA performed by this metadata auditor; parent handles native boundary viewing','No generation, AI edits, Git, credential or original-production writes','Actual image model and quality remain unconfirmed; old outputs are not re-labeled GPT Image2.5','No whole-map completion or formal acceptance is granted')}
$report|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $out 'audit-report-v1.json') -Encoding utf8
[ordered]@{report=(Join-Path $out 'audit-report-v1.json');counts=$report.counts;selectedNativeHashMismatchCount=@($selectedNatives|Where-Object{$_.hashMatches -eq $false}).Count;selectedNativeDimensionsOtherThan1254=@($selectedNatives|Where-Object{$_.dimensions[0] -ne 1254 -or $_.dimensions[1] -ne 1254}).Count;partialTiles=@($coverage|Where-Object{$_.rawCount -gt 0 -and $_.rawCount -lt 16}|Select-Object tile,rawCount,selectedCount);privateCandidateHash=$private.sha256;cross=$cross}|ConvertTo-Json -Depth 6

