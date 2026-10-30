#!/usr/bin/env python3
"""Designed SFX layer + master glue. usage: sfx.py WORK_DIR
Every cue the page emits (window.CUES -> cues.json, via `node render.js PAGE cues cues.json`) gets an audible sound whose
transient lands on the cue time; risers and reverse swells END on their target. Glitch cues also stutter the music.
in : audio/music_raw.npy (score.py), cues.json, timing.json      out: audio/music_fx.npy, audio/sfx_only.npy
Sounds: Kenney Interface Sounds, Virtuosity Drums, VSCO-2-CE, TR-808 (all CC0; scripts/fetch_sounds.sh). pedalboard (GPL-3) is a
tool dependency only."""
import sys, json, glob, pathlib, numpy as np
from lib import *
import pedalboard as pb
W = pathlib.Path(sys.argv[1]); T = json.load(open(W / 'timing.json')); DUR = T['dur']; CU = json.load(open(W / 'cues.json'))
mus = np.load(W / 'audio' / 'music_raw.npy').astype(np.float64); N = len(mus)
I=lambda t:int(round(t*SR))
def nrm(x,p=.9): return x*(p/(np.abs(x).max()+1e-9))
def P(x,chain): return chain(x.T.astype(np.float32),SR).T.astype(np.float64)
PLATE=ir(1.3,.28,9000,.006,9)
def stutter(x,t,n=4,sl=.03,dur=.14,crush=6):
  i=I(t); L=I(sl); seg=x[i:i+L].copy(); q=2**crush; seg=np.round(seg*q)/q
  rep=np.concatenate([seg*(.9**k) for k in range(int(dur/sl)+1)])[:I(dur)]; e=np.ones(len(rep)); f=I(.002); e[-f:]=np.linspace(1,0,f)
  x[i:i+len(rep)]=rep*e[:,None]
SFX=np.zeros((N,2)); RG=np.random.default_rng(21)
K=lambda p:sorted(glob.glob(f'{SD}/kenney_interface/Audio/{p}'))
def ken(p,i=0): return nrm(load(K(p)[i%len(K(p))]))
def put(t,x,g=1.0,pan=0.0,align=0):
  """align: sample index inside x that must land exactly on t (transient / peak)"""
  place(SFX,t-align/SR,x,g,pan)
def env_exp(n,tau): return np.exp(-np.arange(n)/(tau*SR))
def peak_idx(x): e=np.abs(x).mean(1); return int(np.argmax(e>0.5*e.max()))
def whoosh(t,d=.55,g=.33,seed=0,lo=350,hi=5200,pan=(-.7,.7),tail=.16):
  pre=d-tail; n=I(d); u=np.arange(n)/n; pk=pre/d
  fc=lambda c:lo*(hi/lo)**np.where(c<pk,(c/pk)**1.4,1-(c-pk)/(1-pk)*.6)
  y=stft_sweep(n,fc,lambda c:.55+.25*np.sin(np.pi*c),seed)
  e=np.where(u<pk,(u/pk)**2.2,np.exp(-(u-pk)*d/(tail*.35))); y=y*e[:,None]
  pn=np.linspace(*pan,n); y[:,0]*=np.sqrt(np.clip(1-pn,0,2)); y[:,1]*=np.sqrt(np.clip(1+pn,0,2))
  body=st(lp(noise(n),500))*e[:,None]*.25; put(t,(y+body),g,0,I(pre))
def sub(t,d=1.2,f=44,g=.6,sweep=40):
  n=I(d); tt=np.arange(n)/SR; fr=f+sweep*np.exp(-tt/.06); y=np.tanh(1.8*np.sin(2*np.pi*np.cumsum(fr)/SR))*np.exp(-tt/(d*.35)); y[:I(.003)]*=np.linspace(0,1,I(.003)); put(t,st(y),g)
def crack(t,g=.4,f=2500,d=.06): n=I(d); put(t,st(hp(noise(n),f)*env_exp(n,d/5)),g)
def tail(t,g=.3,d=1.4): n=I(d); x=np.stack([lp(noise(n),1800),lp(noise(n),1800)],1)*env_exp(n,d/4)[:,None]; put(t,x,g)
def oneshot(t,x,g=1.0,pan=0.0): put(t,x,g,pan,peak_idx(x))
def blip(t,f=1800,g=.18,pan=0.0,d=.07,f2=None):
  n=I(d); tt=np.arange(n)/SR; ff=f if f2 is None else f+(f2-f)*tt/d
  y=(np.sin(2*np.pi*np.cumsum(np.full(n,ff) if np.isscalar(ff) else ff)/SR))*env_exp(n,d/4); y[:48]*=np.linspace(0,1,48); put(t,st(y),g,pan)
def riser(t0,t1,g=.3,seed=1):
  n=I(t1-t0); u=np.arange(n)/n; y=stft_sweep(n,lambda c:250*(9000/250)**(c**1.6),lambda c:.5+0*c,seed)*(.05+u**2.2)[:,None]
  tt=np.arange(n)/SR; tone=np.sin(2*np.pi*np.cumsum(110*2**(3*u**1.5))/SR)*u**2*.35
  x=y+st(tone); x[-I(.004):]*=np.linspace(1,0,I(.004))[:,None]; place(SFX,t0,x,g)
def shepard(t0,t1,g=.28):
  n=I(t1-t0); tt=np.arange(n)/SR; out=np.zeros(n); rate=1/1.1   # octaves per second
  for k in range(8):
    oc=(k+rate*tt)%8; f=55*2**oc; amp=np.exp(-.5*((oc-4)/1.6)**2); ph=2*np.pi*np.cumsum(f)/SR
    out+=amp*(np.sin(ph)+.3*np.sin(2*ph))
  u=tt/(t1-t0); x=st(out/8)*(.15+u**1.5)[:,None]+stft_sweep(n,lambda c:300*(8000/300)**c,lambda c:.5+0*c,4)*(u**2.5)[:,None]*.6
  x[-I(.003):]*=np.linspace(1,0,I(.003))[:,None]; place(SFX,t0,x,g)
def revswell(t_end,d=.6,g=.4,src=None):
  x=(src if src is not None else nrm(load(f'{SD}/vdrums/Samples/mid/crash/mid_crash_crash_vl3_rr1.flac')))[::-1]
  n=I(d); x=x[-n:] if len(x)>=n else np.pad(x,((n-len(x),0),(0,0))); x=x*np.linspace(0,1,n)[:,None]**1.5; x=hp(x,400); place(SFX,t_end-d,x,g)
CRASH=nrm(load(f'{SD}/vdrums/Samples/mid/crash/mid_crash_crash_vl3_rr2.flac')); GONG=nrm(load(f'{SD}/vsco/Miscellania Raw/Misc 1/cymb_gong.wav'))
METAL=[nrm(load(f)) for f in sorted(glob.glob(f'{SD}/vsco/Miscellania Raw/Misc 1/metal_hit*.wav'))]
GLASS=[nrm(load(f)) for f in sorted(glob.glob(f'{SD}/vsco/Miscellania Raw/Misc 1/glass_break*.wav'))]
B808=nrm(load(f'{SD}/tr808/bd8/BD7575.WAV')); KAC=nrm(load(f'{SD}/vdrums/Samples/mid/kick/mid_kick_snoff_vl4_rr1.flac'))
RIM=nrm(load(f'{SD}/vdrums/Samples/mid/snare/mid_snare_rimshot_vl12.flac' if glob.glob(f'{SD}/vdrums/Samples/mid/snare/mid_snare_rimshot_vl12.flac') else sorted(glob.glob(f'{SD}/vdrums/Samples/mid/snare/mid_snare_rimshot_*'))[-1]))
LTOM=nrm(load(sorted(glob.glob(f'{SD}/vdrums/Samples/mid/ltom/mid_ltom_center_vl1[0-6].flac'))[-1]))
def impact(t,g=.5,f=42,big=False):
  sub(t,1.6 if big else 1.0,f,g*.9); oneshot(t,lp(B808,220),g*.6); oneshot(t,KAC,g*.45); crack(t,g*.35,2200,.05); tail(t,g*.25,1.8 if big else 1.0)
  if big: oneshot(t,CRASH,g*.35,.2); oneshot(t,GONG*.6,g*.3,-.2)
def page(t,g=.22,seed=0):
  n=I(.3); r=np.random.default_rng(seed); u=np.arange(n)/n; am=np.abs(np.sin(2*np.pi*np.cumsum(28+20*u)/SR))**3
  y=bp(noise(n),1400,7000)*am*np.sin(np.pi*u)**.7; x=st(y); x[:,0]*=1-.5*u; x[:,1]*=.5+.5*u
  put(t,x,g); n2=I(.05); put(t+.26,st(lp(noise(n2),900)*env_exp(n2,.01)),g*.6)
def cutfx(t,g=.3,i=0):
  whoosh(t,.24,g*.8,seed=30+i,lo=600,hi=7000,pan=(.5,-.5) if i%2 else (-.5,.5),tail=.06); oneshot(t,ken('click_00*.ogg',i),g*.5); crack(t,g*.3,4000,.02)
def glitchfx(t,g=.32,i=0):
  oneshot(t,ken('glitch_00*.ogg',i),g); 
  for k in range(3): blip(t+.03*k,[2400,1200,3200][k],g*.35,(-.4,.4,0)[k],.025)
  x=noise(I(.12)); q=np.round(np.repeat(x[::40],40)[:len(x)]*3)/3; put(t,st(bp(q,800,6000)*env_exp(len(q),.04)),g*.4)
def popfx(t,g=.3,i=0):
  oneshot(t,ken(['drop_00*.ogg','pluck_00*.ogg'][i%2],i),g*.8,.1*(-1)**i); blip(t,500,g*.5,0,.09,1400)
def tickfx(t,g=.22,f=1800,i=0,pan=0.0): oneshot(t,ken('tick_00*.ogg',i),g,pan); blip(t,f,g*.55,pan,.05)
def downfx(t,g=.3):
  n=I(.8); tt=np.arange(n)/SR; y=np.sin(2*np.pi*np.cumsum(180+2400*np.exp(-tt/.22))/SR)*env_exp(n,.35); put(t,st(y),g*.7); whoosh(t+.25,.5,g*.7,seed=77,lo=1500,hi=200,tail=.3)
def stamp(t,g=.45,i=0):
  sub(t,.5,58,g*.6); oneshot(t,RIM,g*.5); oneshot(t,LTOM,g*.5); n=I(.12); put(t,st(lp(noise(n),2500)*env_exp(n,.02)),g*.8); tail(t,g*.15,.8)
def shatter(t,g=.5):
  oneshot(t,GLASS[0],g*.7,-.2); oneshot(t+.03,GLASS[3%len(GLASS)],g*.5,.3); r=np.random.default_rng(3)
  for k in range(30):
    o=abs(r.normal(0,.35)); n=I(.03); f=r.uniform(1500,6000); put(t+o,st(bp(noise(n),f*.7,f*1.3)*env_exp(n,.006)),g*.4*r.uniform(.4,1)*np.exp(-o/.5),r.uniform(-.8,.8))
def lockfx(t,g=.35,i=0): oneshot(t,ken('switch_00*.ogg',i),g); oneshot(t+.045,METAL[i%len(METAL)]*.5,g*.6,.2); blip(t+.045,1900,g*.3)
def scratchfx(t,g=.35):
  oneshot(t,ken('scratch_00*.ogg',0),g*.9); n=I(.3); tt=np.arange(n)/SR; f=900+700*np.sin(2*np.pi*7*tt); x=bp(noise(n),300,3000)*.5+.4*np.sin(2*np.pi*np.cumsum(f)/SR); put(t,st(x*np.sin(np.pi*tt/.3)),g*.5)
def rewindfx(t,g=.4):
  n=I(.9); tt=np.arange(n)/SR; x=bp(noise(n),500,5000)*.4+.3*np.sign(np.sin(2*np.pi*np.cumsum(300+2500*(tt/.9)**2)/SR)); put(t-.1,st(lp(x,6000)*np.sin(np.pi*tt/.9)),g)
def dropfx(t,g=.5): oneshot(t,ken('switch_00*.ogg',3),g*.7); sub(t,1.8,34,g*.8,25); tail(t,g*.2,1.5)
def flipfx(t,g=.4): whoosh(t,.3,g*.8,seed=90); page(t,g*.5,9); sub(t+.05,.4,62,g*.4)
def logohit(t,g=.6,i=0):
  revswell(t,1.1,g*.6); impact(t,g,40,True); oneshot(t,METAL[(i+4)%len(METAL)]*.6,g*.25,-.3); whoosh(t,.9,g*.45,seed=55+i,lo=200,hi=3000,tail=.6)
CH_I=[0]
def F(t,kind,why,i):
  if kind=='whoosh': whoosh(t,.55 if 'whip' not in why else .4,.3,seed=i,lo=RG.uniform(280,450),hi=RG.uniform(4200,6500),pan=(-.7,.7) if i%2 else (.7,-.7))
  elif kind=='cut': cutfx(t,.3,i)
  elif kind=='page': page(t,.2,i)
  elif kind=='glitch': glitchfx(t,.3,i); stutter(mus,t)
  elif kind=='pop': popfx(t,.3,i)
  elif kind=='click': oneshot(t,ken('click_00*.ogg',2),.35); oneshot(t,ken('switch_00*.ogg',1),.25)
  elif kind=='tick': CH_I[0]+=1; tickfx(t,.2,1500+150*(CH_I[0]%5),i,(-.3,.3)[i%2])
  elif kind=='hit': impact(t,.55 if 'big' in why else .45,46)
  elif kind=='thud': sub(t,.5,60,.35); oneshot(t,LTOM,.25); n=I(.08); put(t,st(lp(noise(n),900)*env_exp(n,.02)),.3)
  elif kind=='slam': impact(t,.6,40,True); oneshot(t,METAL[1],.25,.2)
  elif kind=='stamp': stamp(t,.45,i)
  elif kind=='riser': riser(t-1.2,t,.3,i)          # ends ON the cue
  elif kind=='revcym': revswell(t,.6,.45)           # ends ON the cue
  elif kind=='down': downfx(t,.3)
  elif kind=='logohit': logohit(t,.6,i)
  elif kind=='lock': lockfx(t,.35,i)
  elif kind=='scratch': scratchfx(t)
  elif kind=='shatter': shatter(t,.45)
  elif kind=='subdrop': sub(t,2.4,34,.75,45); tail(t,.15,2)
  elif kind=='rewind': rewindfx(t)
  elif kind=='drop': dropfx(t)
  elif kind=='flip': flipfx(t)
  else: raise SystemExit('no sfx for cue kind '+kind)
end = T['marks'].get('end', DUR)
for i,(t,kind,why) in enumerate(CU):
  if t<end: F(t,kind,why,i)
if T.get('bleep'): shepard(T['bleep'][0]-3.0,T['bleep'][0],.3)   # endless rise into the bleep -> hard stop
SFX=P(SFX,pb.Pedalboard([pb.HighpassFilter(25)]))+conv(SFX,PLATE)*.18
mus=P(mus,pb.Pedalboard([pb.HighpassFilter(30),pb.LowShelfFilter(80,-5,.7),pb.PeakFilter(300,-1.5,.8),pb.HighShelfFilter(5500,3.5,.7),pb.Compressor(-14,2,20,160),pb.Distortion(1.5)]))
mix=mus+SFX
ci=I(end); fo=I(1.2); mix[max(0,ci-fo):ci]*=np.linspace(1,0,ci-max(0,ci-fo))[:,None]**2; mix[ci:]=0
mix=mix[:I(DUR)]; pk=np.abs(mix).max()+1e-9; mix/=pk
np.save(W/'audio'/'music_fx.npy',mix.astype(np.float32)); np.save(W/'audio'/'sfx_only.npy',(SFX[:len(mix)]/pk).astype(np.float32))
print('sfx ok peak',round(pk,3),'cues',len(CU))
