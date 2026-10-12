from workflow import *
p=ROOT/'qa/r10_c11-neighborhood-v01/index.json';d=read(p)
for e in d['entries']:e.update({'status':'visual_major_geometry_pass','reviewer':'root'})
d.update({'reviewedAt':now(),'reviewer':'root','northEdge4096Pass':True,'eastEdge4096Pass':True,'centralFourTileJunctionPass':True,'neighborhoodFullyAccepted':False,'scopeLimit':'External borders and four-tile center only. r10c11 internal p22/p32/p33 repairs remain in flight; final revision must replay these border pixels or recheck changed regions.','observations':['North four native samples preserve wood table, gong contour and stone stair continuity.','East four native samples preserve paving joints, courtyard coping and wall-base grass continuity.','Four-tile center has continuous stairs with no visible hard step in contours.','2x2 overview confirms coherent residence/courtyard layout; current r10c11 internal duplicated small pillar and lower wall seam remain outstanding.']});write(p,d)
print('8 full border samples + center reviewed; no whole-neighborhood acceptance yet')

