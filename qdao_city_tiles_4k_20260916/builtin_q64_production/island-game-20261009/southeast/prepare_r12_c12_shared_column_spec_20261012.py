from workflow import *
old=read(ROOT/'r12_c12-native-spec-20261012-v01.json')
old['overlayManifests']=[str(ROOT/'adopted-overlay-r12_c12-deck-20261012-v02.json'),str(ROOT/'adopted-overlay-r12_c12-lower-deck-20261012-v01.json'),str(ROOT/'adopted-overlay-r12_c12-board-end-20261012-v01.json'),str(ROOT/'proposed-overlay-r12_c12-shared-column-upper-20261012-v01.json')]
target=ROOT/'r12_c12-native-spec-20261012-v02.json';assert not target.exists();write(target,old)
