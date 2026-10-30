# Audio engine: CC0 sample instruments (VSCO-2-CE, Virtuosity Drums, TR-808, Kenney Interface) + self-written synths (PolyBLEP / additive / FM),
# rendered at 48 kHz in numpy. SOUNDS_DIR (env) points at the folder made by scripts/fetch_sounds.sh.
import numpy as np, soundfile as sf, scipy.signal as sg, re, os, glob, functools
SR=48000; SD=os.environ.get('SOUNDS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','assets','sounds'))
NOTE={'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
@functools.lru_cache(None)
def load(path,mono=False):
  x,sr=sf.read(path,dtype='float64',always_2d=True)
  if sr!=SR:
    from math import gcd
    g=gcd(SR,sr); x=sg.resample_poly(x,SR//g,sr//g,axis=0)
  if x.shape[1]==1: x=np.repeat(x,2,1)
  x=x[:,:2]
  if mono: x=np.repeat(x.mean(1,keepdims=True),2,1)
  return x
def f0(x):
  m=x.mean(1); m=m[int(.08*SR):int(.5*SR)] if len(m)>int(.5*SR) else m
  m=m*np.hanning(len(m)); n=1<<18; S=np.abs(np.fft.rfft(m,n)); fr=np.fft.rfftfreq(n,1/SR)
  hps=S.copy()
  for h in (2,3): d=S[::h]; hps[:len(d)]*=d
  lo=np.searchsorted(fr,25); hi=np.searchsorted(fr,2500); return fr[lo+np.argmax(hps[lo:hi])]
def repitch(x,ratio):
  if abs(ratio-1)<1e-4: return x
  n=int(len(x)/ratio); p=np.arange(n)*ratio
  return np.stack([np.interp(p,np.arange(len(x)),x[:,c]) for c in range(2)],1)
class Sampler:
  """files: list of paths with a note name in the file name; layers by a velocity key in the name (optional)."""
  def __init__(s,name,pattern,rx=r'_([A-G]#?)(-?\d)_',vel=None,calib=True,gain=1.0,loop=False,att=0.0,rel=.12):
    s.name=name; s.gain=gain; s.loop=loop; s.att=att; s.rel=rel; s.Z={}
    fs=sorted(glob.glob(os.path.join(SD,pattern)))
    assert fs,(name,pattern)
    for f in fs:
      m=re.search(rx,os.path.basename(f))
      if not m: continue
      k=12*(int(m.group(2))+1)+NOTE[m.group(1)]
      v=0
      if vel:
        for i,tag in enumerate(vel):
          if re.search(tag,os.path.basename(f)): v=i
      s.Z.setdefault(k,{}).setdefault(v,[]).append(f)
    s.off=0
    if calib:   # octave sanity check from one sample's measured pitch
      k=sorted(s.Z)[len(s.Z)//2]; vv=sorted(s.Z[k])[-1]; fz=f0(load(s.Z[k][vv][0]))
      km=69+12*np.log2(fz/440); s.off=int(12*round((km-k)/12))
    s.rr=0
  def note(s,k,v,d):
    """returns stereo buffer for midi k, velocity 0..127, duration d (sec, note-off)"""
    ks=np.array(sorted(s.Z)); kk=ks[np.argmin(np.abs(ks+s.off-k))]; lay=s.Z[kk]; L=sorted(lay)
    li=L[min(len(L)-1,int(v/128*len(L)))]; fl=lay[li]; s.rr+=1; f=fl[s.rr%len(fl)]
    x=repitch(load(f),2**((k-(kk+s.off))/12))
    n=int((d+s.rel)*SR)
    if s.loop and len(x)<n:
      a,b=int(len(x)*.35),int(len(x)*.92); seg=x[a:b]; xf=min(int(.25*SR),len(seg)//3); out=[x[:b-xf]]; cur=len(out[0])
      fi=np.linspace(0,1,xf)[:,None]
      tail=x[b-xf:b]
      while cur<n:
        out.append(tail*(1-fi)+seg[:xf]*fi); out.append(seg[xf:len(seg)-xf]); tail=seg[len(seg)-xf:]; cur+=len(seg)-xf
      x=np.concatenate(out)
    x=x[:n].copy()
    if s.att>0: na=min(len(x),int(s.att*SR)); x[:na]*=np.linspace(0,1,na)[:,None]
    nd=int(d*SR); nr=int(s.rel*SR)
    if nd<len(x): e=np.ones(len(x)); e[nd:]=np.exp(-np.arange(len(x)-nd)/max(1,nr/4)); x*=e[:,None]
    return x*s.gain*(v/127)**1.6
class OneShot:
  def __init__(s,pattern,gain=1.0,mono=False):
    s.fs=sorted(glob.glob(os.path.join(SD,pattern))); assert s.fs,pattern; s.g=gain; s.i=0; s.mono=mono
  def get(s,i=None):
    s.i+=1; return load(s.fs[(s.i if i is None else i)%len(s.fs)],s.mono)*s.g
# ---------------------------------------------------------------- synths
def mtof(k): return 440*2**((k-69)/12)
def blep_saw(f,n,ph0=0.0):
  """PolyBLEP saw, f scalar or array (Hz)"""
  f=np.broadcast_to(np.asarray(f,float),(n,)); dt=f/SR; ph=(ph0+np.cumsum(dt))%1.0
  y=2*ph-1
  m=ph<dt; t=ph[m]/dt[m]; y[m]-=t+t-t*t-1
  m=ph>1-dt; t=(ph[m]-1)/dt[m]; y[m]-=t*t+t+t+1
  return y
def adsr(n,a,d,s,r,nd):
  e=np.zeros(n); A=int(a*SR); D=int(d*SR); R=int(r*SR); nd=min(n,int(nd*SR))
  t=np.arange(n)
  e=np.where(t<A,t/max(1,A),s+(1-s)*np.exp(-(t-A)/max(1,D/3)))
  if nd<n: lvl=e[nd-1] if nd>0 else 0; e[nd:]=lvl*np.exp(-(t[nd:]-nd)/max(1,R/4))
  return e
def svf_lp(x,fc,q=.7):
  """time-varying state-variable LP (Chamberlin, oversampled 2x); fc array or scalar"""
  n=len(x); fc=np.broadcast_to(np.asarray(fc,float),(n,))
  F=2*np.sin(np.pi*np.clip(fc,20,SR*.2)/(2*SR)); Q=1/q
  return _svf(x,F,Q)
try:
  from numba import njit
except Exception:
  njit=None
def _svf_py(x,F,Q):
  lo=bd=0.0; y=np.empty_like(x)
  for i in range(len(x)):
    for _ in range(2):
      hi=x[i]-lo-Q*bd; bd+=F[i]*hi; lo+=F[i]*bd
    y[i]=lo
  return y
_svf=njit(cache=True)(_svf_py) if njit else _svf_py
def lp(x,fc,o=2):
  b,a=sg.butter(o,min(fc,SR*.45)/(SR/2)); return sg.lfilter(b,a,x,axis=0)
def hp(x,fc,o=2):
  b,a=sg.butter(o,fc/(SR/2),'high'); return sg.lfilter(b,a,x,axis=0)
def bp(x,f1,f2,o=2):
  b,a=sg.butter(o,[max(20,f1)/(SR/2),min(f2,SR*.45)/(SR/2)],'band'); return sg.lfilter(b,a,x,axis=0)
def st(x,w=0.0):
  """mono -> stereo (Haas-free, equal-power pan w in -1..1)"""
  return np.stack([x*np.sqrt((1-w)/2)*1.414,x*np.sqrt((1+w)/2)*1.414],1)
RNG=np.random.default_rng(14)
def supersaw(k,d,v,voices=7,det=.18,cut=2400,env=(.35,.4,.8,.9),cutenv=0,bright=1.0):
  n=int((d+env[3])*SR); f=mtof(k); L=np.zeros(n); R=np.zeros(n)
  for i in range(voices):
    c=(i-(voices-1)/2)/((voices-1)/2) if voices>1 else 0; ff=f*2**(det*c/12)
    y=blep_saw(ff,n,RNG.random()); pan=c*.8
    L+=y*np.sqrt((1-pan)/2); R+=y*np.sqrt((1+pan)/2)
  e=adsr(n,*env[:3],env[3],d); fc=cut*bright*(1+cutenv*e)
  L=svf_lp(L,fc,.8); R=svf_lp(R,fc,.8)
  return np.stack([L,R],1)*e[:,None]*(v/127)**1.5/np.sqrt(voices)*.5
def pluck(k,d,v,bright=1.0,dec=.28,harm=40,width=.35,tone='saw'):
  """additive band-limited pluck: higher partials decay faster (filter-envelope feel), 2 detuned layers"""
  f=mtof(k); dur=min(d+dec*2.5,2.5); n=int(dur*SR); t=np.arange(n)/SR; out=np.zeros((n,2))
  for lay,(dt,pan) in enumerate(((-.07,-width),(.07,width))):
    ff=f*2**(dt/12); y=np.zeros(n); ph=RNG.random()*6.28
    for h in range(1,harm+1):
      if ff*h>SR*.42: break
      if tone=='sq' and h%2==0: continue
      a=(1/h)*np.exp(-t*(1/dec)*(.25+.12*h/bright))
      y+=a*np.sin(2*np.pi*ff*h*t+ph*h)
    out+=st(y,pan)
  e=np.minimum(1,t/.002)*np.where(t<d,1,np.exp(-(t-d)/.06))
  return out*e[:,None]*(v/127)**1.5*.35
def bell(k,d,v,ratio=3.5,idx=2.2,dec=1.2):
  f=mtof(k); n=int(min(d+dec*2,4)*SR); t=np.arange(n)/SR; ie=idx*np.exp(-t/(dec*.35))
  y=np.sin(2*np.pi*f*t+ie*np.sin(2*np.pi*f*ratio*t))*np.exp(-t/dec)*np.minimum(1,t/.001)
  return st(y)*(v/127)**1.5*.3
def subbass(k,d,v,drive=1.6,glide=0.0,click=True):
  f=mtof(k); n=int((d+.08)*SR); t=np.arange(n)/SR
  fr=f*(1+glide*np.exp(-t/.05)); y=np.sin(2*np.pi*np.cumsum(fr)/SR)
  y=np.tanh(drive*y)/np.tanh(drive)
  e=np.minimum(1,t/.004)*np.where(t<d,1,np.exp(-(t-d)/.02))
  if click: y[:int(.004*SR)]+=0
  return st(y*e)*(v/127)**1.4*.55
def reese(k,d,v,cut=900):
  n=int((d+.06)*SR); f=mtof(k)
  y=(blep_saw(f*2**(-.12/12),n)+blep_saw(f*2**(.12/12),n,.5))*.5
  e=adsr(n,.005,.2,.85,.06,d); y=svf_lp(y,cut*(.6+.8*e),1.1); y=np.tanh(1.8*y)
  return addx(st(y*e)*(v/127)**1.4*.4,subbass(k,d,v,1.2)*.8)
def addx(*xs):
  xs=[x for x in xs if np.ndim(x)==2]; n=max(len(x) for x in xs); o=np.zeros((n,2))
  for x in xs: o[:len(x)]+=x
  return o
def noise(n): return RNG.standard_normal(n)
def ir(dur=2.6,tau=.6,lpf=7000,pre=.014,seed=3,er=True):
  """self-made stereo plate/hall IR: decorrelated exponentially decaying noise + early reflections"""
  r=np.random.default_rng(seed); n=int(dur*SR); t=np.arange(n)/SR
  x=r.standard_normal((n,2))*np.exp(-t/tau)[:,None]
  x=np.stack([lp(x[:,c],lpf*np.ones(1)[0]) for c in range(2)],1)
  # frequency-dependent decay: lowpass the tail more
  tail=np.stack([lp(x[:,c],lpf*.35) for c in range(2)],1); w=np.clip(t/dur*1.6,0,1)[:,None]; x=x*(1-w)+tail*w
  if er:
    for k in range(12):
      d=r.uniform(.006,.07); i=int(d*SR); x[i,0]+=r.uniform(.3,.9)*np.exp(-d/.05); x[int(i*1.07)%n,1]+=r.uniform(.3,.9)*np.exp(-d/.05)
  x[:int(pre*SR)]=0; x/=np.sqrt((x**2).sum(0)); return x
def conv(x,h): return np.stack([sg.fftconvolve(x[:,c],h[:,c])[:len(x)] for c in range(2)],1)
def place(buf,t,x,g=1.0,pan=0.0):
  i=int(round(t*SR)); N=len(buf)
  if i>=N or i+len(x)<=0: return
  if i<0: x=x[-i:]; i=0
  j=min(N,i+len(x)); x=x[:j-i]
  if pan: x=x*np.array([np.sqrt(1-pan),np.sqrt(1+pan)])[None,:]
  buf[i:j]+=x*g
def stft_sweep(n,fc,bw,seed=0):
  """noise shaped by a moving gaussian band (centre fc(t) Hz, width bw(t) octaves) -> designed whoosh/riser core"""
  r=np.random.default_rng(seed); x=r.standard_normal((n,2))
  f,tt,Z=sg.stft(x.T,SR,nperseg=1024,noverlap=768)
  tc=np.clip(tt*SR/n,0,1); c=fc(tc); b=bw(tc)
  lf=np.log2(np.maximum(f,20))[:,None]; M=np.exp(-.5*((lf-np.log2(c)[None,:])/b[None,:])**2)
  _,y=sg.istft(Z*M[None],SR,nperseg=1024,noverlap=768); y=y.T[:n]
  if len(y)<n: y=np.pad(y,((0,n-len(y)),(0,0)))
  return y/ (np.abs(y).max()+1e-9)
class VelShot:
  """velocity-layered one-shot: files whose name has _vl<N>; round robin among same layer; levels kept relative, loudest -> peak .9"""
  def __init__(s,pattern,gain=1.0,rev=False):
    fs=sorted(glob.glob(os.path.join(SD,pattern))); assert fs,pattern; s.L={}
    for f in fs:
      m=re.search(r'_vl(\d+)',os.path.basename(f)); s.L.setdefault(int(m.group(1)) if m else 1,[]).append(f)
    s.keys=sorted(s.L); top=max(np.abs(load(f)).max() for f in s.L[s.keys[-1]]); s.g=gain*.9/top; s.i=0
  def get(s,v):
    lay=s.L[s.keys[min(len(s.keys)-1,int(v/128*len(s.keys)))]]; s.i+=1; return load(lay[s.i%len(lay)])*s.g
def normgain(sm,target=.5):
  ks=sorted(sm.Z); k=ks[len(ks)//2]; vv=sorted(sm.Z[k])[-1]; p=np.abs(load(sm.Z[k][vv][0])).max(); sm.gain*=target/p; return sm
