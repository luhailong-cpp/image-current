from pathlib import Path
R=Path(__file__).resolve().parent
s=(R.parent/'color_match_selected.py').read_text(encoding='utf-8')
s=s.replace("ZONE = Path(__file__).resolve().parent\nSEL = ZONE / 'selected-patches.json'\nSELECTED = json.loads(SEL.read_text(encoding='utf-8-sig'))\nTILE = ZONE / SELECTED['tile']","ZONE = Path(__file__).resolve().parent\nTILE = ZONE\nSEL = TILE / 'processed/jointpass/selected-patches.json'\nSELECTED = json.loads(SEL.read_text(encoding='utf-8-sig'))")
start=s.index("            dif = (bb[:, 95:135]")
end=s.index("            half = np.clip(profile",start)
new="""            da,db=(aa[:,1119:1159],bb[:,95:135]) if dc else (aa[1119:1159],bb[95:135])
            dif=db-da
            def gradient(x):
                return np.maximum(np.max(np.abs(np.gradient(x,axis=0)),axis=2),np.max(np.abs(np.gradient(x,axis=1)),axis=2))
            mask=(gradient(da)<6)&(gradient(db)<6)&(np.max(np.abs(dif),axis=2)<65)
            # Estimate only reliable same-coordinate smooth surfaces; reject structure and shadow edges.
            dd=dif if dc else np.swapaxes(dif,0,1)
            mm=mask if dc else mask.T
            valid=mm.sum(axis=1)>=8
            rows=np.zeros((1254,3),dtype=np.float32)
            for ii in np.flatnonzero(valid):rows[ii]=np.median(dd[ii][mm[ii]],axis=0)
            kernel=np.exp(-.5*(np.arange(-96,97)/24)**2);kernel/=kernel.sum()
            den=np.convolve(np.pad(valid.astype(np.float32),(96,96),mode='edge'),kernel,mode='valid')
            num=np.stack([np.convolve(np.pad(rows[:,ch]*valid,(96,96),mode='edge'),kernel,mode='valid') for ch in range(3)],axis=1)
            profile=num/np.maximum(den[:,None],1e-8)
            profile[den<.15]=0
            maskpath=OUT/f'{a}-{b}-sampling-mask.npz'
            np.savez_compressed(maskpath,acceptedPixels=mm,acceptedRows=valid,validWeight=den,rawMedianRgb=rows)
            sampling_evidence.append(dict(seam=f'{a}-{b}-{axis}',maskFile=str(maskpath),maskSha256=sha(maskpath),acceptedPixelCount=int(mm.sum()),acceptedRowCount=int(valid.sum()),excluded='RGB gradient>=6 or same-coordinate RGB difference>=65; profiles with effective valid weight<0.15 disabled',sampleWidth=40))
"""
s=s[:start]+new+s[end:]
start=s.index('def safety_weights(k):');end=s.index('\n\ndef seam_metrics(',start)
s=s[:start]+"def safety_weights(k):\n    return np.ones(1254,dtype=np.float32),np.zeros(1254,dtype=np.float32)\n"+s[end:]
start=s.index("    source = sources[k]; basepath = source")
end=s.index("    base = fimage(basepath)",start)
s=s[:start]+"    source = sources[k]; basepath = source\n"+s[end:]
s=s.replace("boatSamplePolicy='p31-p32:16px matching deck band only, native y<800, exclude gradients>=4.5 and RGB differences>=60; p41-p42:no trustworthy common surface, disabled',","boatSamplePolicy='Geometry-repaired inputs; every seam uses smooth same-coordinate pixel samples only; RGB gradient<6 and difference<65, at least8/40 samples per profile row',")
s=s.replace("boatCorrectionSafety='zero within128px of boat seam; restore field smoothly128..384px away; p31/p32 y760..880 transition to full protection; p41/p42 full height'","boatCorrectionSafety='No color correction used to conceal geometry; p32-p33 hull-bottom was jointly repaired first; color anchor is geometry-corrected source'")
start=s.index("    if (a,b) in [('p31','p32'),('p41','p42')]:");end=s.index("    r=int(a[1])-1",start)
s=s[:start]+s[end:]
s=s.replace('r10_c09','r11_c09')
s=s.replace("'selected input pixels'","'geometry-reviewed selected input pixels'")
s=s.replace("'cumulative correction bound anchor'","'geometry-corrected source color bound anchor'")
s=s.replace("'maximumCumulativeChannelChangeFromNative'","'maximumCumulativeChannelChangeFromNative'")
(R/'color_match_tile.py').write_text(s,encoding='utf-8')
print(str(R/'color_match_tile.py'))

