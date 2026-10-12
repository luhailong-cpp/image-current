import numpy as np,json
import build_next_connected_preserving_prior as w
c=w.c
c.CORE=64;c.HALO=7;c.PADDED=78;c.OVERLAP=14;c.CLUSTER=128;c.PADDED_CLUSTER=142
c.assembly.OVERLAP=14
rng=np.random.default_rng(443)
arrays=[rng.integers(0,256,size=(78,78,3),dtype=np.uint8) for _ in range(4)]
c.join_pair=w.preserve_first_join
pixels,labels,joins=c.compose(arrays)
proof=c.verify_pixels(pixels,labels,arrays)
assert joins[0]["overlapPath"]==[7]*78
assert np.array_equal(pixels[:57,:64],arrays[0][7:64,7:71])
assert np.array_equal(pixels[:57,64:],arrays[1][7:64,7:71])
for index in range(4):
 x0,y0,x1,y1=c.projection_box(index)
 ids=c.projection_labels(joins,index)
 assert np.array_equal(ids,labels[y0:y1,x0:x1])
 c.verify_projection_pixels(pixels[y0:y1,x0:x1],ids,arrays,index)
print(json.dumps({"passed":True,"verifiedSyntheticPixels":proof["pixelCount"],"topRowPriorBoundaryPreserved":True,"fourProjectionProofsPassed":True,"scope":"small integration test of exact coordinate selection and existing projection replay; not art acceptance"}))

