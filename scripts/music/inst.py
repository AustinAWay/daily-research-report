from lib import *  # sample paths are relative to SOUNDS_DIR
V='vsco/'
def I():
  D={}
  D['piano']=Sampler('piano',V+'Keys/Upright Nr1/UR1_*.wav',rx=r'UR1_([A-G]#?)(\d)_',vel=['_pp_','_mf_','_f_'],rel=.35)
  D['vln']=Sampler('vln',V+'Strings/Violin Section/susVib/*.wav',vel=['_v1','_v2'],loop=True,att=.12,rel=.5)
  D['vla']=Sampler('vla',V+'Strings/Viola Section/susvib/*.wav',vel=['_v1','_v2'],loop=True,att=.12,rel=.5)
  D['vc']=Sampler('vc',V+'Strings/Cello Section/susvib/*.wav',vel=['_v1','_v3'],loop=True,att=.12,rel=.5)
  D['vlntrem']=Sampler('vlntrem',V+'Strings/Violin Section/Trem/*.wav',vel=['_v1','_v2'],loop=True,att=.05,rel=.3)
  D['vctrem']=Sampler('vctrem',V+'Strings/Cello Section/trem/*.wav',vel=['_v1','_v2'],loop=True,att=.05,rel=.3)
  D['pizz']=Sampler('pizz',V+'Strings/Violin Section/Pizz/*.wav',vel=['_v1','_v2'],rel=.2)
  D['spic']=Sampler('spic',V+'Strings/Violin Section/Spic/*.wav',vel=['_v1','_v2'],rel=.15)
  D['harp']=Sampler('harp',V+'Strings/Harp/*.wav',rx=r'_([A-G]#?)(\d)_',rel=.6)
  D['glock']=Sampler('glock',V+'Percussion/Glock/*.wav',rx=r'_([A-G]#?)(\d)\.wav',rel=.8)
  D['marimba']=Sampler('marimba',V+'Percussion/Marimba/*.wav',rx=r'_([A-G]#?)(\d)_',rel=.4)
  D['xylo']=Sampler('xylo',V+'Percussion/Xylo/*.wav',rx=r'_([A-G]#?)(\d)_',rel=.3)
  D['horn']=Sampler('horn',V+'Brass/F Horn/sus/*.wav',rx=r'_([A-G]#?)(\d)_',vel=['_v1','_v2','_v3'],loop=True,att=.03,rel=.35)
  D['tpt']=Sampler('tpt',V+'Brass/Trumpet/stac/*.wav',rx=r'_([A-G]#?)(\d)_',vel=['_v1','_v2','_v3'],rel=.2)
  D['vctrem'].off=12
  for s in D.values(): normgain(s)
  return D
if __name__=='__main__':
  D=I()
  for k,s in D.items(): print(k,'off',s.off,'range',min(s.Z)+s.off,max(s.Z)+s.off,'n',sum(len(f) for v in s.Z.values() for f in v.values()))
