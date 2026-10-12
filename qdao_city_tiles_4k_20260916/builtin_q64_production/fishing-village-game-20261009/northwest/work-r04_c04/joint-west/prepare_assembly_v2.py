from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'assemble_lower_bridge.py').read_text(encoding='utf-8')
s=s.replace("O=D/'lower-v1'","O=D/'lower-v2'")
s=s.replace("add(R/'native/r04_c03_c04_lower_net_transition_bridge_v01.png','global-lower-net-bridge',58)","add(R/'native/r04_c03_c04_lower_net_transition_bridge_v01.png','global-lower-net-bridge',58)\nadd(R/'native/r04_c03_c04_net_hem_bridge_v01.png','global-net-hem-bridge',59)")
tag="# Support bridge core remains byte exact."
add="""# Complete hem patch, one shared mask spanning two tiles and existing lower partial.
hb=[11648,15950,12902,17204];hx=hb[0]-8192;hy=hb[1]-12288;ha=arrays[59]
hbase=a[hy:hy+1254,hx:hx+1254].copy();hknown=ids[hy:hy+1254,hx:hx+1254]!=0
hc=hbase.copy();hc[~hknown]=ha[~hknown]
hm,hpaths=rep.overlay_mask(hc,ha,[{'xStart':250,'xEndExclusive':1050,'minY':1190,'reason':'Preserve full naturally rounded hem, place south cut in clean sand below every rope strand.'}])
hm|=~hknown
hr=a[hy:hy+1254,hx:hx+1254];hr[hm]=ha[hm];ids[hy:hy+1254,hx:hx+1254][hm]=59
save(O/'hem-bridge-mask.png',hm.astype(np.uint8)*255)
save(O/'hem-bridge-applied.png',hr)
"""
s=s.replace(tag,add+tag)
s=s.replace("for k in range(8):diag.append(crop('west-final-segment-'","for side,b in [('north',[11648,15750,12902,16180]),('west',[11448,15950,11878,17204]),('east',[12672,15950,13102,17204]),('south',[11648,16974,12902,17404])]:\n diag.append(crop('hem-'+side+'-100pct',b))\nfor k in range(8):diag.append(crop('west-final-segment-'")
s=s.replace("write(O/'joint-paths.json',path)","path['hemBridge']={'globalBox':hb,'sourceId':59,'mask':art(O/'hem-bridge-mask.png'),'paths':hpaths,'nativePixels':int(hm.sum())}\nwrite(O/'joint-paths.json',path)")
s=s.replace("'previousFailedLowerCutsSupersededByNative58':True","'previousFailedLowerCutsSupersededByNative58And59':True")
(D/'assemble_lower_bridge_v2.py').write_text(s,encoding='utf-8')

