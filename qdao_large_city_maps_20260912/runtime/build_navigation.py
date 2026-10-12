from pathlib import Path
import argparse, base64, hashlib, importlib.util, json, math
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
CLIENT=ROOT.parent.parent/'mmorpg-client'
SIZE=1254; GRID=150; CELL=SIZE/GRID

def rect(x0,y0,x1,y1): return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def poly(name,*points): return {'name':name,'vertices':points}
def box(name,x0,y0,x1,y1): return poly(name,*rect(x0,y0,x1,y1))
def circle(name,x,y,r):
 return poly(name,*[(round(x+r*math.cos(t*math.pi/24),2),round(y+r*math.sin(t*math.pi/24),2)) for t in range(48)])

MAPS={
'penglai':{
 'spawn':[220,0,170],
 'allow':[
  poly('central Taiji plaza',(490,414),(548,406),(587,423),(648,418),(807,420),(817,463),(852,479),(893,507),(904,544),(983,554),(997,625),(981,667),(937,685),(887,666),(833,674),(795,689),(769,740),(714,785),(652,817),(567,798),(501,751),(463,719),(478,668),(494,610),(483,567),(494,519)),
  poly('north processional road',(556,424),(607,423),(639,380),(639,350),(684,333),(689,310),(650,300),(647,324),(601,333),(598,377),(560,382)),
  poly('north bridge to peach garden',(642,327),(680,328),(711,298),(716,274),(743,245),(737,220),(707,239),(686,263),(682,287),(655,303)),
  poly('peach garden courts',(709,169),(695,128),(701,106),(738,100),(776,114),(794,143),(778,181),(746,190),(740,225),(705,225)),
  poly('west temple approach',(419,442),(453,432),(453,399),(427,377),(421,311),(396,291),(414,269),(385,249),(375,285),(351,303),(354,352),(405,376),(408,410)),
  poly('west road to central',(414,441),(465,443),(516,433),(515,410),(466,413),(421,412)),
  poly('temple staircase',(333,304),(366,289),(376,266),(350,224),(333,199),(306,200),(311,231),(326,270)),
  poly('temple forecourt',(263,206),(299,222),(334,217),(386,204),(416,208),(443,189),(427,165),(376,175),(350,172),(341,145),(290,146),(290,181),(253,183)),
  poly('west alchemy promenade',(279,440),(304,425),(348,426),(363,437),(412,438),(424,464),(411,490),(383,518),(345,549),(328,576),(313,610),(277,650),(252,648),(254,614),(284,578),(298,548),(306,520),(277,492)),
  poly('west district connector',(384,429),(384,451),(424,461),(467,449),(489,438),(486,412),(441,429)),
  poly('west lower crossing',(287,634),(309,613),(337,604),(349,621),(336,645),(331,678),(364,698),(399,687),(425,680),(454,677),(492,680),(484,716),(448,729),(415,719),(390,723),(359,746),(324,736),(291,711)),
  poly('moon pond upper promenade',(310,724),(340,725),(371,748),(400,768),(430,782),(451,776),(463,751),(481,754),(473,787),(448,812),(418,808),(393,792),(363,781),(335,752)),
  poly('south avenue',(559,796),(604,817),(655,811),(684,789),(689,825),(660,855),(649,887),(664,919),(656,971),(615,987),(584,963),(584,916),(570,887),(552,844)),
  box('south gate forecourt',588,977,668,1038),
  box('south gate stairs',603,1030,649,1170),
  poly('east residential connection',(819,422),(831,396),(850,386),(845,353),(831,340),(839,319),(865,313),(880,326),(891,352),(925,372),(977,389),(1000,420),(1031,432),(1038,463),(1017,475),(995,443),(963,427),(930,415),(903,405),(872,407),(853,430)),
  poly('east village main street',(854,326),(865,292),(913,283),(941,260),(949,226),(964,190),(955,154),(938,132),(936,105),(965,112),(987,146),(993,184),(979,220),(971,254),(953,289),(915,316),(882,323)),
  poly('village southern frontage',(928,313),(980,318),(998,342),(1015,359),(1042,351),(1068,365),(1081,391),(1067,411),(1035,412),(1003,389),(977,364),(931,344)),
  poly('harbor access bridge',(895,623),(919,644),(944,659),(960,687),(974,707),(1011,711),(1037,693),(1049,716),(1014,740),(981,744),(949,729),(930,701),(916,675),(891,657)),
  poly('harbor market promenade',(972,735),(1001,746),(1035,734),(1070,714),(1104,704),(1144,726),(1162,749),(1144,770),(1110,755),(1067,763),(1044,788),(1018,816),(995,843),(970,868),(941,880),(914,866),(937,836),(952,807),(963,772)),
 ],
 'block':[
  circle('plaza osmanthus tree',601,471,47),circle('plaza west lamp',465,520,22),
  poly('plaza northeast pavilion',(685,359),(737,359),(762,377),(798,364),(813,390),(799,422),(757,441),(706,426),(683,405)),
  poly('plaza southeast shop',(692,650),(744,626),(790,645),(809,681),(789,710),(726,717),(694,695)),
  poly('south garden pavilion',(533,674),(584,644),(625,662),(657,703),(642,756),(610,781),(559,766),(520,727)),
  circle('garden left planting',444,658,38),circle('garden tall lamp',820,634,17),
  poly('east plaza shrine',(875,573),(911,561),(941,579),(967,604),(951,635),(910,647),(886,625)),
  poly('plaza eastern tea kiosk',(843,491),(874,478),(913,480),(940,509),(927,541),(874,545),(849,529)),
  circle('central northmarket tree',547,410,34),
  box('upper temple roof',238,32,345,145),
  box('west alchemy tower',109,447,190,581),
  poly('west house',(260,397),(332,386),(373,417),(361,460),(306,468),(266,444)),
  poly('west left temple',(380,495),(425,486),(473,536),(483,583),(401,597),(379,568)),
  box('west lower buildings',75,552,230,632),
  box('moon pond water and pavilion',151,710,390,901),
  box('south gate roof',560,978,687,1028),
 ],
 'landmarks': [('Taiji plaza',(715,545)),('north bridge forecourt',(622,330)),('Daoist temple approach',(350,201)),('alchemy district promenade',(319,552)),('moon pond promenade',(419,782)),('eastern village street',(959,288)),('harbor market approach',(1008,733)),('southern avenue',(622,916)),('peach garden court',(745,160))],
 'blocked': [('main temple roof',(296,78)),('sea',(1110,1100)),('central waterfall',(584,200)),('moon pond',(300,837)),('west alchemy tower',(149,475)),('central osmanthus tree',(601,471)),('south garden pavilion',(588,708)),('east pavilion roof',(913,601)),('moored boat',(1138,854))]
},
'donghai':{
 'spawn':[200,0,180],
 'allow':[
  poly('central dragon plaza',(529,383),(591,371),(708,375),(781,403),(803,431),(820,478),(796,524),(777,558),(719,579),(638,588),(572,570),(531,536),(503,487),(505,438)),
  poly('north temple avenue',(594,373),(666,370),(674,335),(667,298),(676,277),(698,252),(712,222),(698,195),(670,183),(594,182),(578,204),(580,245),(589,283),(595,313)),
  poly('temple east bypass',(674,285),(695,292),(715,265),(739,256),(756,228),(736,206),(738,170),(724,145),(721,112),(698,110),(692,152),(703,183),(704,217),(690,244)),
  poly('temple front court',(595,149),(620,161),(676,160),(711,153),(709,120),(674,128),(596,128)),
  poly('north west crossroad',(303,173),(352,178),(393,188),(440,193),(489,192),(526,204),(584,213),(605,198),(594,178),(536,174),(481,171),(437,164),(386,163),(345,151)),
  poly('west village avenue',(312,197),(338,210),(336,247),(319,277),(315,314),(305,351),(282,367),(265,356),(279,324),(288,290),(292,255),(301,232)),
  poly('west upper alley',(192,267),(250,286),(289,294),(309,278),(310,255),(270,264),(223,250),(194,249)),
  poly('west bridge and plaza connection',(254,361),(279,358),(300,381),(318,401),(360,427),(392,441),(432,451),(498,459),(516,482),(499,505),(459,494),(414,481),(386,463),(348,457),(306,431),(280,416),(250,413),(219,425),(217,400),(225,378)),
  poly('west bank road',(275,418),(300,422),(315,453),(326,481),(348,499),(361,541),(382,562),(387,602),(364,635),(343,655),(315,674),(301,706),(284,740),(265,760),(255,738),(272,706),(279,674),(295,650),(316,624),(344,605),(346,574),(327,552),(322,523),(305,504),(290,477)),
  poly('moon festival court',(191,677),(216,667),(251,685),(281,685),(301,706),(287,732),(263,737),(229,720),(196,714)),
  poly('lower west street',(364,632),(390,646),(397,668),(383,691),(378,713),(404,747),(444,768),(479,766),(520,743),(574,723),(590,736),(579,760),(535,771),(504,798),(466,802),(426,798),(391,773),(356,749),(352,710),(361,683)),
  poly('central south street',(610,585),(661,588),(678,614),(679,645),(699,667),(699,688),(671,704),(670,744),(644,773),(637,805),(630,838),(656,874),(675,911),(698,944),(714,979),(740,1009),(755,1040),(751,1090),(715,1126),(683,1120),(686,1094),(680,1057),(664,1020),(654,978),(636,947),(606,925),(590,885),(583,847),(590,814),(598,781),(606,749),(609,708),(625,681),(617,653),(605,620)),
  poly('east central access',(792,488),(817,504),(853,517),(878,537),(899,566),(928,597),(959,607),(978,594),(979,535),(959,487),(951,451),(955,415),(969,393),(963,367),(942,368),(925,400),(919,441),(917,474),(889,485),(856,476),(822,459)),
  poly('north east neighborhood crossroad',(705,248),(752,251),(797,252),(832,266),(874,282),(917,301),(963,324),(1005,338),(1058,325),(1078,305),(1086,280),(1060,278),(1041,301),(1006,308),(978,297),(944,285),(912,274),(875,260),(842,246),(794,227),(751,223)),
  poly('east shrine side street',(774,235),(802,224),(810,193),(807,152),(803,119),(795,98),(817,88),(832,124),(831,166),(834,193),(829,229)),
  poly('eastern quayside promenade',(956,341),(1003,343),(1015,360),(987,391),(967,414),(967,455),(983,484),(1003,515),(1006,558),(1001,602),(1034,642),(1076,658),(1104,685),(1122,727),(1105,758),(1074,764),(1038,741),(1005,716),(989,682),(975,646),(945,625),(932,599),(935,551),(938,515),(925,477),(929,433),(936,392)),
  poly('south fishing workshop access',(672,631),(713,630),(760,631),(794,620),(832,620),(867,636),(901,644),(943,642),(984,654),(1004,680),(990,704),(949,691),(911,684),(875,671),(834,654),(795,654),(758,663),(718,665),(681,670)),
  poly('south boatyard perimeter',(657,886),(686,887),(710,914),(730,944),(759,981),(791,1007),(836,1024),(883,1032),(934,1031),(973,1012),(1005,993),(1027,1008),(1006,1031),(975,1055),(933,1063),(882,1071),(833,1056),(779,1042),(744,1021),(714,985),(690,949),(670,927)),
  poly('upper east pier entry',(1016,343),(1051,331),(1090,317),(1133,302),(1171,291),(1199,285),(1208,301),(1164,317),(1123,328),(1084,343),(1046,361)),
  poly('middle east pier entry',(1000,519),(1032,524),(1073,516),(1114,503),(1150,492),(1157,510),(1116,523),(1078,537),(1038,548),(1000,544)),
 ],
 'block':[
  poly('festival dragon lantern',(591,191),(623,170),(666,167),(693,186),(700,225),(690,265),(648,280),(606,267),(585,236)),
  poly('festival west fish lantern',(436,431),(475,416),(512,436),(532,462),(522,500),(483,510),(450,499),(431,472)),
  poly('festival east fish lantern',(775,426),(815,420),(855,442),(862,479),(842,511),(804,505),(774,483)),
  poly('west plaza stall',(491,510),(540,500),(588,524),(620,539),(609,579),(564,602),(522,580),(493,547)),
  poly('south plaza stall',(677,555),(717,550),(753,560),(778,587),(765,624),(714,640),(681,617)),
  poly('east plaza temple',(798,534),(841,516),(879,530),(905,564),(891,605),(847,631),(809,610),(790,576)),
  circle('west village tree',362,322,47),
  box('main temple roof',576,38,692,135),
  box('northwest large house',366,182,493,298),
  box('west bank house',249,446,370,545),
  box('west moon-tree',168,578,285,691),
  box('western river water',383,922,425,1071),
  poly('eastern fishing racks',(704,642),(844,621),(942,638),(952,694),(862,728),(737,733),(697,702)),
  poly('south boat',(756,878),(819,862),(895,892),(927,947),(917,1005),(866,1017),(790,985),(745,931)),
 ],
 'landmarks':[('dragon plaza',(635,487)),('temple east forecourt',(706,151)),('west village street',(308,305)),('western bridge',(267,395)),('west bank promenade',(366,590)),('moon gathering courtyard',(256,714)),('east quayside',(970,462)),('southern avenue',(617,793)),('harbor frontage',(1073,716)),('boatyard perimeter',(756,1004))],
 'blocked':[('temple roof',(630,88)),('sea',(1150,590)),('western river',(213,462)),('boat hull',(840,943)),('festival dragon lantern',(645,221)),('festival left fish lantern',(484,468)),('festival right fish lantern',(822,469)),('west village roof',(451,236)),('south racks',(825,670))]
},
'lanxian':{
 'spawn':[200,0,180],
 'allow':[
  poly('Taiji central plaza',(492,422),(539,406),(572,398),(679,396),(735,405),(772,426),(793,470),(803,524),(785,581),(767,632),(731,671),(692,689),(625,700),(569,682),(528,653),(503,613),(497,568),(480,532)),
  poly('temple central avenue',(589,84),(662,83),(666,143),(656,190),(656,261),(688,286),(687,340),(679,388),(654,418),(597,416),(580,385),(577,336),(579,288),(601,263),(601,204),(593,159)),
  poly('west central connection',(312,420),(339,421),(364,441),(393,457),(433,467),(471,465),(511,449),(532,470),(507,493),(470,495),(432,491),(402,484),(365,476),(336,459),(307,457)),
  poly('west market avenue',(280,300),(307,305),(309,348),(307,391),(311,434),(307,477),(303,522),(305,565),(302,610),(310,653),(303,702),(284,739),(259,736),(270,700),(278,662),(274,621),(279,578),(277,534),(279,491),(277,446),(279,409),(277,369)),
  poly('northwestern court staircase',(243,226),(275,224),(289,251),(293,288),(308,310),(291,324),(269,301),(261,276),(243,258)),
  poly('northwest yin-yang courtyard',(216,177),(246,167),(280,168),(305,180),(308,205),(279,220),(247,230),(221,221),(211,204)),
  poly('west southern market crossstreet',(304,668),(342,679),(383,692),(426,702),(469,709),(514,707),(551,722),(547,746),(511,743),(467,739),(427,728),(382,719),(339,707),(300,697)),
  poly('west garden main street',(287,733),(308,744),(298,782),(297,818),(308,854),(312,898),(315,941),(304,981),(293,1022),(300,1053),(326,1072),(341,1095),(316,1110),(290,1090),(276,1060),(265,1027),(276,987),(282,945),(281,904),(283,868),(275,832),(279,793)),
  poly('west fountain court',(239,839),(275,822),(313,834),(346,853),(359,882),(350,912),(322,930),(282,926),(251,910),(236,881)),
  poly('west south avenue connector',(334,868),(380,859),(418,846),(451,831),(475,807),(489,783),(503,755),(527,738),(548,753),(525,778),(515,811),(492,840),(461,858),(420,871),(380,886),(341,893)),
  poly('south processional avenue',(571,689),(621,702),(685,685),(696,715),(696,759),(676,793),(661,826),(659,867),(673,900),(682,941),(679,979),(650,1008),(596,1006),(575,977),(577,941),(581,901),(588,868),(589,829),(581,795),(569,760),(566,727)),
  poly('south gate passage',(599,996),(654,996),(653,1050),(653,1092),(677,1136),(677,1180),(578,1180),(578,1135),(602,1093),(602,1055)),
  poly('north east stone bridge',(674,293),(710,290),(746,277),(775,261),(793,256),(820,276),(843,293),(875,297),(899,291),(917,303),(905,320),(875,324),(840,318),(813,307),(786,283),(769,287),(737,300),(708,315),(680,316)),
  poly('central east stone bridge',(747,412),(780,398),(808,386),(825,384),(848,392),(872,407),(901,414),(927,409),(952,421),(947,441),(924,440),(897,442),(866,431),(844,415),(822,406),(804,410),(776,428),(754,435)),
  poly('east main avenue',(908,190),(929,199),(936,238),(945,270),(949,301),(942,329),(940,365),(949,397),(958,432),(951,466),(961,500),(981,526),(1004,548),(1004,578),(980,589),(949,561),(929,533),(922,505),(925,470),(931,440),(922,403),(920,368),(921,331),(924,300),(921,268),(909,237)),
  poly('north east court',(911,182),(910,157),(939,158),(974,178),(1006,183),(1039,174),(1071,169),(1090,188),(1075,208),(1040,208),(1006,212),(971,211),(939,208)),
  poly('east residential crossstreet',(936,284),(980,293),(1016,290),(1054,293),(1095,283),(1130,265),(1154,248),(1171,257),(1153,284),(1122,304),(1091,317),(1050,320),(1018,314),(981,321),(945,314)),
  poly('east lower stone bridge',(746,654),(771,638),(792,639),(821,657),(849,682),(866,690),(886,672),(912,644),(937,630),(962,620),(977,639),(954,654),(931,664),(909,683),(889,708),(865,713),(842,706),(822,686),(795,666),(778,659),(758,673)),
  poly('east southern residential street',(901,671),(924,674),(936,700),(932,730),(953,756),(983,773),(1005,788),(1035,793),(1057,779),(1080,786),(1072,807),(1040,821),(1004,817),(973,806),(940,786),(914,762),(907,730)),
  poly('east moon garden south connection',(1020,808),(1054,809),(1057,841),(1039,864),(1028,889),(1033,916),(1045,939),(1070,958),(1090,969),(1110,970),(1127,957),(1140,967),(1125,989),(1096,995),(1060,986),(1037,967),(1015,946),(1004,913),(1006,880),(1019,855)),
  poly('south east river bridge',(674,875),(719,873),(755,861),(783,854),(806,855),(827,870),(849,882),(876,882),(902,874),(931,862),(957,861),(981,870),(1006,877),(1024,890),(1016,909),(993,899),(969,888),(947,886),(924,887),(904,898),(875,906),(845,903),(817,889),(799,876),(781,877),(755,885),(724,898),(682,902)),
 ],
 'block':[
  box('north temple roof',553,13,699,106),
  circle('northwest Taiji planter',568,347,18),circle('northeast Taiji planter',667,347,18),
  circle('plaza northern center planter',626,442,27),circle('plaza northwest planter',550,453,23),circle('plaza northeast planter',707,457,23),
  circle('plaza west planter',501,488,20),circle('plaza east planter',748,493,21),
  circle('plaza southwest planter',504,584,22),circle('plaza southeast planter',747,582,22),
  circle('plaza southern west planter',570,625,25),circle('plaza southern east planter',683,625,25),
  poly('west market main buildings',(322,471),(383,466),(425,493),(427,550),(395,598),(348,593),(303,549),(304,501)),
  poly('west southern pavilion',(381,589),(419,574),(453,600),(477,637),(458,668),(416,664),(389,638)),
  box('west garden fountain',257,851,306,901),
  poly('southeast willow tree',(716,708),(750,700),(767,724),(761,776),(738,808),(706,784),(704,739)),
  poly('east bridge north willow',(775,458),(805,437),(845,456),(854,500),(826,539),(783,524),(763,486)),
  box('southern gate roof',535,990,719,1067),
  poly('southwest town wall',(414,1022),(558,1022),(574,1087),(551,1123),(476,1147),(411,1107)),
  poly('southeast town wall',(697,1023),(812,1027),(827,1097),(780,1134),(717,1119),(689,1080)),
 ],
 'landmarks':[('Taiji plaza',(627,535)),('Daoist temple courtyard',(628,147)),('western market avenue',(294,485)),('western residential crossroad',(397,715)),('fountain garden promenade',(331,895)),('northeast village street',(942,273)),('east residential court',(982,793)),('moon garden promenade',(1022,906)),('south avenue',(627,938)),('northwest practice courtyard',(259,196))],
 'blocked':[('main temple roof',(620,63)),('western shop roof',(370,517)),('eastern river',(835,818)),('central river pavilion',(864,535)),('north planter',(627,442)),('south left planter',(570,625)),('garden fountain',(285,872)),('moon lantern decoration',(1119,871)),('west stream',(148,1060))]
}
}

# Manually reviewed route strips join curved stairs/bridges after 2 m rasterization.
# These are ground geometry, not image modifications.
def revise(region, name, shape):
    MAPS[region]['allow']=[x for x in MAPS[region]['allow'] if x['name']!=name]
    if shape: MAPS[region]['allow'].append(shape)

def obstacle(region,name,shape):
    MAPS[region]['block']=[x for x in MAPS[region]['block'] if x['name']!=name]
    if shape:MAPS[region]['block'].append(shape)

def route(region,name,width,*points):
    MAPS[region].setdefault('route_strips',[]).append({'name':name,'width_pixels':width,'centerline':points})

revise('penglai','village southern frontage',None)
revise('penglai','harbor market promenade',poly('harbor inner stone deck',(855,824),(893,799),(933,779),(972,755),(1013,732),(1052,711),(1082,702),(1107,711),(1108,729),(1075,738),(1045,750),(1008,771),(975,791),(940,813),(909,838),(879,860),(855,849)))
route('penglai','north stairs join',30,(620,438),(620,402),(622,374),(623,341),(654,322),(678,319),(698,290),(702,269),(723,243),(721,219),(724,185),(735,163))
route('penglai','west temple stairs join',27,(358,338),(351,309),(359,283),(349,255),(333,229),(325,205))
route('penglai','east stone bridge floor',26,(795,443),(819,421),(844,408),(873,398),(863,375),(853,351),(857,329),(870,305),(912,299),(940,282),(955,264))
route('penglai','moon pond east stairs',26,(488,704),(458,719),(438,739),(431,764),(419,787))
route('penglai','harbor inner deck',28,(944,694),(967,716),(989,728),(1025,720),(1060,706))
obstacle('penglai','garden upper planting',circle('garden upper planting',588,630,37))
MAPS['penglai']['landmarks']=[(n,((329,204) if n=='Daoist temple approach' else (981,729) if n=='harbor market approach' else p)) for n,p in MAPS['penglai']['landmarks']]

revise('lanxian','west central connection',None)
revise('lanxian','west southern market crossstreet',None)
route('lanxian','west market north connection',25,(296,401),(322,413),(355,423),(387,438),(423,457),(456,461),(486,450),(509,435))
route('lanxian','north east bridge surface',25,(679,299),(714,299),(752,285),(782,273),(804,280),(832,300),(866,311),(922,309))
route('lanxian','central east bridge surface',25,(750,419),(776,405),(806,397),(828,404),(852,417),(879,428),(919,427),(939,438))
route('lanxian','lower east bridge surface',26,(745,651),(773,649),(797,658),(821,679),(848,699),(867,700),(891,681),(916,660),(950,642))
route('lanxian','west garden staircase',25,(600,749),(571,749),(539,748),(513,758),(498,786),(481,815),(455,830),(414,847),(372,866),(333,891))
route('lanxian','west garden fountain east',25,(291,826),(314,840),(328,865),(329,894),(308,928))
route('lanxian','west market to garden street',26,(294,682),(294,720),(295,759),(288,789),(289,822),(290,837))
route('lanxian','east homes to lower bridge',27,(950,642),(927,662),(921,689),(920,726),(931,752),(953,771),(980,787),(1025,805))
route('lanxian','moon garden river bridge',25,(673,885),(718,885),(752,874),(782,865),(807,868),(829,884),(854,894),(879,896),(905,886),(934,876),(960,875),(990,886),(1017,901))
obstacle('lanxian','west small pavilion',poly('west small pavilion',(314,447),(337,432),(365,440),(390,451),(394,478),(374,489),(336,486),(311,469)))
MAPS['lanxian']['landmarks']=[(n,((294,707) if n=='western residential crossroad' else (979,777) if n=='east residential court' else p)) for n,p in MAPS['lanxian']['landmarks']]

route('donghai','western neighborhood lower connection',28,(623,740),(595,743),(565,752),(531,769),(493,784),(456,785),(423,777),(395,759),(374,729),(372,700),(379,673),(378,648),(365,625))
route('donghai','temple east bypass pavement',23,(646,306),(659,291),(678,285),(700,275),(719,258),(734,245),(722,213),(714,182),(709,153))
route('donghai','east district junction',26,(724,252),(755,242),(791,239),(823,257),(854,267),(889,281),(926,299),(964,321),(996,328),(1006,350),(983,382),(952,411),(947,452),(962,486),(987,524),(989,563),(987,596),(1000,628),(1023,651),(1049,666),(1078,694),(1092,723))
route('donghai','west bridge floor',26,(308,330),(292,357),(276,380),(261,400),(284,411),(313,431),(348,447),(378,459),(403,469))
route('donghai','west bank village lane',25,(310,449),(321,476),(346,504),(361,543),(371,575),(371,606),(351,632),(325,651),(299,677),(281,711),(269,736))
obstacle('donghai','west bank house',poly('west bank house',(224,499),(256,473),(294,474),(310,500),(311,533),(281,552),(242,543),(222,524)))
MAPS['donghai']['landmarks']=[(n,((704,153) if n=='temple east forecourt' else (308,305) if n=='west village street' else p)) for n,p in MAPS['donghai']['landmarks']]

route('penglai','north stairs southern join around tree',34,(671,445),(654,418),(646,397),(623,388),(622,368),(622,340))
route('penglai','moon pond broad stone stairs',34,(488,704),(458,719),(438,739),(431,764),(419,787))
MAPS['penglai']['landmarks']=[(n,((949,280) if n=='eastern village street' else p)) for n,p in MAPS['penglai']['landmarks']]
MAPS['donghai']['landmarks']=[(n,((948,452) if n=='east quayside' else p)) for n,p in MAPS['donghai']['landmarks']]
MAPS['lanxian']['landmarks']=[(n,((940,280) if n=='northeast village street' else (982,782) if n=='east residential court' else p)) for n,p in MAPS['lanxian']['landmarks']]
# Final visual review: keep Penglai movement on the inner harbor approach,
# and route Donghai west-bank travel around the house through the upper village.
revise('penglai','harbor inner stone deck',poly('harbor inner stone deck',(951,712),(974,706),(993,711),(1015,703),(1037,693),(1048,706),(1029,718),(1006,731),(983,742),(960,734)))
MAPS['penglai']['route_strips']=[x for x in MAPS['penglai']['route_strips'] if x['name']!='harbor inner deck']
route('penglai','harbor gate ground',24,(944,694),(960,714),(980,726),(1001,718),(1026,704))
obstacle('donghai','west riverbank lower house',poly('west riverbank lower house',(267,554),(315,527),(351,530),(378,561),(382,592),(356,611),(293,610),(268,585)))
obstacle('donghai','west riverbank willow',poly('west riverbank willow',(300,469),(345,460),(373,486),(371,544),(344,563),(298,532)))
obstacle('donghai','boatyard storage crates',poly('boatyard storage crates',(758,1009),(791,998),(814,1016),(842,1035),(824,1071),(794,1080),(764,1058)))
route('donghai','temple forecourt west exit',26,(706,153),(684,165),(649,169),(615,169),(580,169),(550,179),(521,184))
MAPS['donghai']['landmarks']=[(n,((350,637) if n=='west bank promenade' else (746,994) if n=='boatyard perimeter' else p)) for n,p in MAPS['donghai']['landmarks']]
MAPS['donghai']['blocked'] += [('west riverbank lower house',(331,565)),('west riverbank willow',(337,496)),('storage crates',(800,1040))]
MAPS['penglai']['blocked'] += [('harbor water beside stone pier',(1035,814))]
obstacle('donghai','northwest large house',poly('northwest large house',(399,227),(430,205),(461,198),(484,225),(488,255),(471,289),(425,294),(396,270)))
route('donghai','northwest village crossroad',28,(520,185),(483,185),(442,182),(402,180),(369,175),(340,178),(320,197),(317,233),(306,274),(308,307),(292,349))
# Final native-resolution floor review, 2026-09-13. These polygons open broad
# visible pavement; each shared day/festival stall, crate and rack remains solid.
MAPS['penglai']['allow'].append(poly('harbor broad stone market floor',
 (815,794),(848,770),(883,752),(908,740),(950,722),(977,695),(1003,680),
 (1035,682),(1062,694),(1080,704),(1080,719),(1055,737),(1020,756),
 (994,772),(976,797),(979,819),(971,834),(948,849),(922,867),
 (893,885),(855,906),(827,910),(812,890)))
obstacle('penglai','harbor upper awning',poly('harbor upper awning',
 (897,688),(932,676),(961,693),(975,717),(966,734),(928,750),(896,733)))
obstacle('penglai','harbor western stall',poly('harbor western stall',
 (838,738),(868,721),(901,740),(905,767),(879,794),(848,786),(832,764)))
obstacle('penglai','harbor middle blue stall',poly('harbor middle blue stall',
 (925,769),(949,753),(976,748),(989,771),(989,793),(966,814),(938,805),(920,789)))
obstacle('penglai','harbor red stall',poly('harbor red stall',
 (867,801),(889,781),(916,799),(931,821),(919,842),(893,853),(864,835)))
obstacle('penglai','harbor lower west stall',poly('harbor lower west stall',
 (790,800),(818,783),(852,798),(858,825),(840,847),(804,856),(787,835)))
obstacle('penglai','harbor north cargo',poly('harbor north cargo',
 (973,723),(1008,711),(1025,727),(1025,743),(990,763),(970,752)))
obstacle('penglai','harbor middle cargo',poly('harbor middle cargo',
 (931,818),(950,805),(966,816),(966,838),(937,855),(921,841)))
obstacle('penglai','harbor south cargo',poly('harbor south cargo',
 (875,857),(896,842),(915,853),(915,876),(882,891),(870,879)))
obstacle('penglai','harbor southwest bollard',circle('harbor southwest bollard',831,880,14))
obstacle('penglai','harbor south bollard',circle('harbor south bollard',866,894,13))
# The southern harbor court remains intentionally disconnected: its passage
# between the awning/stall silhouettes does not fit a complete safe 2 m cell.
MAPS['penglai']['blocked'] += [('harbor middle blue stall',(958,785)),('harbor red stall',(897,824)),('harbor north cargo',(999,737)),('harbor south cargo',(891,867))]

MAPS['lanxian']['allow'].append(poly('central plaza broad paved perimeter',
 (478,435),(529,405),(565,389),(686,389),(736,408),(774,433),
 (795,472),(799,531),(789,578),(771,624),(747,659),(721,684),
 (681,707),(571,707),(538,678),(510,646),(491,611),(479,569),(471,525),(474,482)))
# Keep the large decorative planters and the roof/vegetation at the perimeter
# excluded rather than treating every light pixel as pavement.
MAPS['lanxian']['landmarks'] += [('plaza northwest open pavement',(531,481)),('plaza southeast open pavement',(716,641))]

obstacle('donghai','eastern fishing racks',None)
obstacle('donghai','western drying rack',poly('western drying rack',
 (716,642),(748,632),(801,630),(812,662),(799,683),(751,694),(709,673)))
obstacle('donghai','eastern drying rack',poly('eastern drying rack',
 (832,627),(869,621),(917,615),(929,640),(928,661),(902,676),(880,691),(827,685)))
obstacle('donghai','racks southern storage and roofs',poly('racks southern storage and roofs',
 (700,680),(756,675),(806,681),(842,685),(881,681),(910,674),(950,668),
 (955,715),(865,744),(739,744),(695,711)))
MAPS['donghai']['allow'].append(poly('drying-rack northern paved forecourt',
 (668,624),(707,625),(753,620),(785,618),(815,618),(844,607),
 (875,601),(899,606),(923,606),(948,611),(959,635),(936,641),
 (904,638),(863,640),(819,644),(778,647),(735,650),(682,650)))
# The inner drying-rack court remains excluded where the complete safe cell
# cannot pass between the building/rack silhouettes. Do not bridge the obstacle.
MAPS['donghai']['blocked'] += [('western drying rack',(768,657)),('eastern drying rack',(879,651))]

MAPS['penglai']['allow'].append(poly('harbor actual descending staircase',
 (939,648),(965,648),(983,661),(1006,676),(1024,690),(1012,710),
 (992,703),(977,686),(961,675),(939,669)))
MAPS['penglai']['landmarks']=[(n,((1033,711) if n=='harbor market approach' else p)) for n,p in MAPS['penglai']['landmarks']]
obstacle('donghai','south plaza stall',poly('south plaza stall',
 (677,555),(717,550),(753,560),(778,587),(765,611),(738,624),(710,625),(681,611)))
obstacle('donghai','east plaza temple',poly('east plaza temple',
 (798,534),(841,516),(879,530),(905,564),(893,588),(871,603),(845,617),(809,604),(790,576)))

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def world_to_pixel(w):return ((w[0]-50)*SIZE/300,(300-w[2])*SIZE/300)
def pixel_to_world(p):return [round(50+p[0]*300/SIZE,6),0,round(300-p[1]*300/SIZE,6)]
def cell_of(p):return (min(GRID-1,max(0,int(p[0]/CELL))),min(GRID-1,max(0,int(p[1]/CELL))))
def center(c):return ((c[0]+.5)*CELL,(c[1]+.5)*CELL)
def flood(mask,start):
 seen={start};q=deque([start]);parents={start:None}
 while q:
  x,y=q.popleft()
  for dx,dy in [(0,-1),(-1,0),(1,0),(0,1)]:
   n=(x+dx,y+dy)
   if 0<=n[0]<GRID and 0<=n[1]<GRID and mask[n[1],n[0]] and n not in seen:
    seen.add(n);parents[n]=(x,y);q.append(n)
 return seen,parents

def main():
 p=argparse.ArgumentParser();p.add_argument('--region',choices=list(MAPS));p.add_argument('--diagnose',action='store_true');a=p.parse_args()
 spec=importlib.util.spec_from_file_location('prepare_import',ROOT/'runtime/prepare_import.py');prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
 summaries=[]
 for key,cfg in MAPS.items():
  if a.region and key!=a.region:continue
  raster=Image.new('L',(SIZE,SIZE));d=ImageDraw.Draw(raster)
  for shape in cfg['allow']:d.polygon(shape['vertices'],fill=255)
  for strip in cfg.get('route_strips',[]):
   pts=strip['centerline']; w=strip['width_pixels']; d.line(pts,fill=255,width=w,joint='curve')
   for x,y in pts:d.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=255)
  for shape in cfg['block']:d.polygon(shape['vertices'],fill=0)
  pixels=np.asarray(raster.filter(ImageFilter.MinFilter(3)))==255
  mask=np.zeros((GRID,GRID),dtype=bool)
  for y in range(GRID):
   for x in range(GRID):
    x0,y0=math.floor(x*CELL),math.floor(y*CELL)
    x1,y1=math.ceil((x+1)*CELL),math.ceil((y+1)*CELL)
    mask[y,x]=bool(pixels[y0:y1,x0:x1].all())
  spawncell=cell_of(world_to_pixel(cfg['spawn']))
  assert mask[spawncell[1],spawncell[0]],f'{key} spawn is blocked'
  reachable,parents=flood(mask,spawncell)
  before=int(mask.sum());clean=np.zeros_like(mask)
  for x,y in reachable:clean[y,x]=True
  raw_mask=mask.copy();mask=clean
  packed=np.packbits(mask.flatten(),bitorder='big').tobytes();assert len(packed)==2813
  records=[];fail=[]
  for name,point in cfg['landmarks']:
   c=cell_of(point); reachable_now=c in reachable
   near=min(reachable,key=lambda n:(center(n)[0]-point[0])**2+(center(n)[1]-point[1])**2)
   rec={'name':name,'pixel':point,'world':pixel_to_world(point),'cell':c,'walkable_and_reachable':reachable_now,'nearest_walkable_pixel':center(near),'nearest_distance_pixels':round(math.dist(center(near),point),2)}
   if reachable_now:
    path=[];n=c
    while n is not None:path.append(n);n=parents[n]
    path.reverse();nodes=[center(n) for n in path]
    edges_valid=all(abs(c1[0]-c2[0])+abs(c1[1]-c2[1])==1 and mask[c1[1],c1[0]] and mask[c2[1],c2[0]] for c1,c2 in zip(path,path[1:]))
    sampled_edges=True; sampled_count=0
    full_pixels=[world_to_pixel(cfg['spawn'])]+nodes+[point]
    for p0,p1 in zip(full_pixels,full_pixels[1:]):
     for step in range(max(1,math.ceil(math.dist(p0,p1)/.5))+1):
      steps=max(1,math.ceil(math.dist(p0,p1)/.5)); t=step/steps; sc=cell_of((p0[0]+(p1[0]-p0[0])*t,p0[1]+(p1[1]-p0[1])*t)); sampled_count+=1
      sampled_edges=sampled_edges and bool(mask[sc[1],sc[0]])
    if not sampled_edges:fail.append('SEGMENT:'+name)
    rec.update({'sampled_path_points':sampled_count,'complete_route_segments_walkable':sampled_edges,'path_cells':path,'path_world':[pixel_to_world(n) for n in nodes],'path_nodes':len(path),'path_edges_valid':edges_valid})
   else:fail.append(name)
   records.append(rec)
  probes=[]
  for name,point in cfg['blocked']:
   c=cell_of(point);blocked=not bool(mask[c[1],c[0]])
   probes.append({'name':name,'pixel':point,'world':pixel_to_world(point),'cell':c,'blocked':blocked})
   if not blocked:fail.append('BLOCKED PROBE:'+name)
  document={
   'schema_version':1,'region':key,'status':'passed' if not fail else 'needs_review','visual_source_pixels':[SIZE,SIZE],
   'visual_mode':'existing baked artwork plus independent explicit navigation',
   'geometry_policy':'Conservative manually traced shared day/festival ground regions; opaque roofs, water, walls, vegetation and festival props are excluded. Entire grid cell plus one source pixel margin must fit allowed floor. Keep only the four-neighbor component containing the exact spawn.',
   'walkable_grid':[GRID,GRID],'cell_size_world':2,'world_rect':{'x_min':50,'x_max':350,'z_min':0,'z_max':300},
   'pixel_to_world':{'x':'50 + pixel_x / 1254 * 300','y':0,'z':'300 - pixel_y / 1254 * 300'},
   'packing':'row 0 = north; index row*150+column; MSB-first; 22500 bits padded with 4 zero bits; 2813 bytes',
   'spawnWorld':cfg['spawn'],'spawnPixel':world_to_pixel(cfg['spawn']),'spawn_cell':spawncell,
   'walkable_cells':int(mask.sum()),'walkable_percent':round(float(mask.mean()*100),4),'removed_disconnected_cells':before-int(mask.sum()),
   'decoded_mask_sha256':sha_bytes(packed),'base64_text_sha256':sha_bytes((base64.b64encode(packed).decode()+'\n').encode()),
   'source_maps':[{ 'asset':f'Assets/Resources/World/FestivalRegions/{key}/{atm}.png','sha256':prep.sha(CLIENT/f'Assets/Resources/World/FestivalRegions/{key}/{atm}.png')} for atm in ['day','festival']],
   'allowed_floor_polygons':cfg['allow'],'manually_traced_route_strips':cfg.get('route_strips',[]),'excluded_obstacle_polygons':cfg['block'],
   'landmarks':records,'blocked_probes':probes,'failed_checks':fail,
   'validation':{'spawn_exact_cell_walkable':True,'single_four_neighbor_component':True,'all_landmark_paths_reachable':not fail,'all_path_edges_axis_adjacent_and_walkable':all(r.get('path_edges_valid',False) for r in records),'all_route_segments_sampled_every_half_pixel':all(r.get('complete_route_segments_walkable',False) for r in records),'all_blocked_probes_blocked':all(p['blocked'] for p in probes),'decoded_byte_count':len(packed),'tail_padding_zero':(packed[-1]&15)==0}
  }
  (ROOT/f'runtime/{key}-navigation.json').write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  overlayalpha=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0));od=ImageDraw.Draw(overlayalpha)
  for y,x in zip(*((raw_mask & ~mask) if a.diagnose else np.zeros_like(mask)).nonzero()):od.rectangle([math.ceil(x*CELL),math.ceil(y*CELL),math.floor((x+1)*CELL)-1,math.floor((y+1)*CELL)-1],fill=(255,145,0,100))
  for y,x in zip(*mask.nonzero()):od.rectangle([math.ceil(x*CELL),math.ceil(y*CELL),math.floor((x+1)*CELL)-1,math.floor((y+1)*CELL)-1],fill=(0,255,90,86))
  for atmosphere in ['day','festival']:
   background=Image.open(CLIENT/f'Assets/Resources/World/FestivalRegions/{key}/{atmosphere}.png').convert('RGBA')
   combined=Image.alpha_composite(background,overlayalpha);dd=ImageDraw.Draw(combined)
   for n in range(0,SIZE,100):
    dd.line([(n,0),(n,SIZE)],fill=(190,0,220,150),width=1);dd.line([(0,n),(SIZE,n)],fill=(190,0,220,150),width=1)
    dd.text((n+3,4),str(n),fill='white',stroke_width=1,stroke_fill='black');dd.text((4,n+3),str(n),fill='white',stroke_width=1,stroke_fill='black')
   for i,r in enumerate(records):
    x,y=r['pixel'];fill='white' if r['walkable_and_reachable'] else 'red';dd.ellipse([x-6,y-6,x+6,y+6],fill=fill,outline='black',width=2);dd.text((x+8,y-8),f'{i+1}',fill=fill,stroke_width=2,stroke_fill='black')
   for r in probes:
    x,y=r['pixel'];dd.line([(x-6,y-6),(x+6,y+6)],fill='red',width=3);dd.line([(x+6,y-6),(x-6,y+6)],fill='red',width=3)
   x,y=world_to_pixel(cfg['spawn']);dd.ellipse([x-9,y-9,x+9,y+9],outline='yellow',width=3)
   combined.convert('RGB').save(ROOT/f'runtime/{key}-{atmosphere}-walkmask-overlay.png')
  if not fail and not a.diagnose:
   target=CLIENT/f'Assets/Resources/World/FestivalRegions/{key}/walkmask.txt'
   target.write_text(base64.b64encode(packed).decode()+'\n',encoding='ascii',newline='\n')
   textmeta='fileFormatVersion: 2\nguid: '+prep.guid(target.relative_to(CLIENT).as_posix())+'\nTextScriptImporter:\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
   prep.write_new_or_same(Path(str(target)+'.meta'),textmeta,False)
  summaries.append({'region':key,'walkable_percent':document['walkable_percent'],'removed_disconnected':before-int(mask.sum()),'failed':fail,'landmark_diagnostics':[{'name':r['name'],'reachable':r['walkable_and_reachable'],'near':r['nearest_walkable_pixel'],'distance':r['nearest_distance_pixels']} for r in records]})
 print(json.dumps(summaries,ensure_ascii=False,indent=2))
 if any(s['failed'] for s in summaries):raise SystemExit(1)

if __name__=='__main__':main()