// Motion library. Every animated property in the film goes through one of these curves.
// Nothing here is linear: springs overshoot and settle, anticipation dips before it goes,
// staggers carry per-element jitter so no two things move in perfect sync.
const gsap=window.gsap;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
// damped spring, normalised to the tween's duration: fully settled (|err|<.1%) at u=1.
// stiffness ~ how many wobbles fit in the tween, damping ratio zeta (0..1, lower = bouncier).
export function spring(stiffness=180,damping=14,mass=1){
  const w0=Math.sqrt(stiffness/mass),zeta=clamp(damping/(2*Math.sqrt(stiffness*mass)),.05,.999),wd=w0*Math.sqrt(1-zeta*zeta);
  // physical settle time for 0.1% envelope; map tween u in [0,1] onto that span
  const Ts=-Math.log(.001)/(zeta*w0);
  return u=>{if(u<=0)return 0;if(u>=1)return 1;const t=u*Ts;
    const v=1-Math.exp(-zeta*w0*t)*(Math.cos(wd*t)+zeta*w0/wd*Math.sin(wd*t));
    const k=clamp((u-.9)/.1);return v+(1-v)*k*k*(3-2*k);};}
export const outBack=(s=1.70158)=>u=>{u-=1;return 1+u*u*((s+1)*u+s);};
export const outExpo=u=>u>=1?1:1-Math.pow(2,-10*u);
export const outQuint=u=>1-Math.pow(1-u,5);
export const inOutQuint=u=>u<.5?16*u**5:1-Math.pow(-2*u+2,5)/2;
export const inOutSine=u=>-(Math.cos(Math.PI*u)-1)/2;
export const inQuint=u=>u**5;
// anticipation: pull back by `a` (fraction of travel) over the first `p` of the tween, then expo out with a small overshoot
export const anticipate=(a=.12,p=.28)=>{const sp=spring(240,16);return u=>{if(u<=0)return 0;if(u>=1)return 1;if(u<p){const k=u/p;return -a*Math.sin(k*Math.PI/2)**2;}
  return -a+(1+a)*sp((u-p)/(1-p));};};
// slam: accelerates into the impact at `hit` (no ease-out before contact), then a decaying ring-out around the rest value
export const slam=(hit=.22,ring=.12)=>u=>{if(u<=0)return 0;if(u>=1)return 1;if(u<hit)return Math.pow(u/hit,2.6);const k=(u-hit)/(1-hit);return 1-ring*Math.sin(k*Math.PI*3.2)*Math.exp(-5*k)*(1-k);};
// curves registered as named eases so plain gsap calls use them too
const reg=(n,f)=>gsap.registerEase(n,f);
reg('spring',spring(180,14));reg('springSoft',spring(90,11));reg('springHard',spring(320,18));reg('springBouncy',spring(220,9));
reg('settle',spring(140,16));reg('anticip',anticipate());reg('anticipBig',anticipate(.22,.32));reg('slam',slam());
reg('outQuint',outQuint);reg('outExpo',outExpo);reg('inOutQuint',inOutQuint);reg('drift',inOutSine);
// default ease for every tween that does not name one: quint-out (never linear)
gsap.defaults({ease:'outQuint'});
// deterministic jitter per element (seconds)
export function jitter(i,amt=.04,seed=1){const x=Math.sin((i+1)*12.9898+seed*78.233)*43758.5453;return (x-Math.floor(x)-.5)*2*amt;}
// stagger with cascade order and jitter. from: 'start'|'end'|'center'|'edges'|'front'(by z, nearest first)|fn(i)->rank
export function stagger(items,each=.04,o={}){const n=items.length;let rank;
  if(typeof o.from==='function')rank=items.map((x,i)=>o.from(x,i));
  else if(o.from==='center')rank=items.map((x,i)=>Math.abs(i-(n-1)/2));
  else if(o.from==='end')rank=items.map((x,i)=>n-1-i);
  else if(o.from==='edges')rank=items.map((x,i)=>(n-1)/2-Math.abs(i-(n-1)/2));
  else rank=items.map((x,i)=>i);
  return items.map((x,i)=>Math.max(0,rank[i]*each+jitter(i,o.jitter??each*.35,o.seed||3)));}
// wave helper for gsap: returns a stagger function for gsap's `stagger` field
export const wave=(each=.03,o={})=>(i,el,list)=>stagger(list,each,o)[i];
// secondary motion: squash and stretch on an impact, then spring back (DOM or Object3D.scale)
export function squash(TL,target,t,amt=.22,dur=.5,axis='y'){const isObj=target&&target.isVector3;const a=1-amt,b=1+amt*.6;
  const s0=axis==='y'?{scaleX:b,scaleY:a}:{scaleX:a,scaleY:b};
  if(isObj){const v0=axis==='y'?{x:b,y:a,z:b}:{x:a,y:b,z:a};TL.fromTo(target,v0,{x:1,y:1,z:1,duration:dur,ease:'springBouncy',immediateRender:false},t);}
  else TL.fromTo(target,s0,{scaleX:1,scaleY:1,duration:dur,ease:'springBouncy',immediateRender:false},t);return t;}
// follow-through: a child lags its parent by `lag` seconds and overshoots (use on labels, tails, hands)
export function follow(TL,target,t,props,dur=.7,lag=.06){TL.to(target,{...props,duration:dur,ease:'springBouncy'},t+lag);return t+lag+dur;}
// pop in with anticipation (scale .8 -> 1.06 -> 1) and a tiny rotation settle
export function popIn(TL,el,t,o={}){TL.fromTo(el,{autoAlpha:0,scale:o.s0??.6,rotation:o.rot??-6,y:o.y??30},{autoAlpha:1,scale:1,rotation:0,y:0,duration:o.d??.7,ease:o.ease||'springBouncy',immediateRender:false},t);return t;}
export function popOut(TL,el,t,o={}){TL.to(el,{autoAlpha:0,scale:o.s1??.85,y:o.y??-20,duration:o.d??.28,ease:'inQuint'},t);return t;}
export const MOTION={spring,outBack,outExpo,outQuint,inOutQuint,inOutSine,anticipate,slam,jitter,stagger,wave,squash,follow,popIn,popOut};
// surge: never-zero velocity (camera keeps flying), with a kick at the start of each beat
export const surge=u=>.4*u+.6*(1-Math.pow(1-u,4));gsap.registerEase('surge',surge);
reg('inQuint',inQuint);reg('inExpo',u=>u<=0?0:Math.pow(2,10*u-10));reg('fall',u=>u*u);
