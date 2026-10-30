// engine: one deterministic paused GSAP timeline + a three.js voxel stage (GTAO/DOF/bloom) + a DOM kinetic-type layer + 2D post (zoom / directional blur). seek(t) renders time t exactly.
import * as THREE from './vendor/three.module.min.js';
import {MODELS} from './models.js';
import {spring,anticipate,outBack} from './motion.js';
import {EffectComposer} from './vendor/jsm/postprocessing/EffectComposer.js';
import {RenderPass} from './vendor/jsm/postprocessing/RenderPass.js';
import {GTAOPass} from './vendor/jsm/postprocessing/GTAOPass.js';
import {BokehPass} from './vendor/jsm/postprocessing/BokehPass.js';
import {UnrealBloomPass} from './vendor/jsm/postprocessing/UnrealBloomPass.js';
import {OutputPass} from './vendor/jsm/postprocessing/OutputPass.js';
export {THREE,MODELS};
export const TM=window.TIMING, FPS=30, W=1920, HG=1080;
export const INK='#1A1A3A',BL='#2F6BFF',CO='#FF5A4E',CR='#FFF6E8',YE='#FFC446';
export const gsap=window.gsap; export const TL=gsap.timeline({paused:true});window.TL=TL;
export const CUES=window.CUES=[];  // [t,kind,why] -> sound design
export const cue=(t,k,why='')=>{CUES.push([+t.toFixed(3),k,why]);return t;};
// ---------- timing helpers ----------
const nz=s=>s.toLowerCase().replace(/[^a-z0-9']/g,'');
export function L(id){const l=TM.lines.find(l=>l.id===id);if(!l)throw Error('line '+id);return l;}
function wd(id,word,k){const l=L(id),q=nz(word);let ws=l.words.filter(x=>nz(x.w)===q);if(!ws.length)ws=l.words.filter(x=>nz(x.w).startsWith(q));if(!ws[k])throw Error(`word ${id}:${word}:${k}`);return ws[k];}
export const w=(id,word,k=0)=>wd(id,word,k).s, we=(id,word,k=0)=>wd(id,word,k).e;
export const ls=id=>L(id).t, le=id=>L(id).t+L(id).d;
export function rng(seed){let s=(seed*2654435761)>>>0||1;return()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296;};}
export const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), lerp=(a,b,u)=>a+(b-a)*u;
export const E=n=>gsap.parseEase(n);
const eBack=outBack(1.9),eLand=spring(210,13),eMorph=anticipate(.07,.22),eTo=spring(170,15),eP3o=eTo;
// ---------- renderer / stage ----------
export const glc=document.getElementById('gl');
export const R=new THREE.WebGLRenderer({canvas:glc,antialias:true,alpha:false,preserveDrawingBuffer:true});
R.setPixelRatio(1);R.setSize(W,HG,false);R.outputColorSpace=THREE.SRGBColorSpace;R.shadowMap.enabled=true;R.shadowMap.type=THREE.VSMShadowMap;
export const S=new THREE.Scene();{const c=document.createElement('canvas');c.width=4;c.height=256;const g=c.getContext('2d');const gr=g.createLinearGradient(0,0,0,256);gr.addColorStop(0,'#F3E4CC');gr.addColorStop(.55,'#FBF0DE');gr.addColorStop(1,'#FFF6E8');g.fillStyle=gr;g.fillRect(0,0,4,256);const bt=new THREE.CanvasTexture(c);bt.colorSpace=THREE.SRGBColorSpace;S.background=bt;}S.fog=new THREE.Fog(CR,60,140);
export const CAM=new THREE.PerspectiveCamera(32,W/HG,.1,400);
// ---------- post: GTAO (contact AO) -> bokeh DOF (autofocus on the rig target) -> HDR bloom (only >1.0 emitters) ----------
const FX=new URLSearchParams(location.search).get('fx')??'ao,dof,bloom';const QL=new URLSearchParams(location.search).get('q')==='lite';
const RT=new THREE.WebGLRenderTarget(W,HG,{type:THREE.HalfFloatType,samples:QL?2:4});
export const COMP=new EffectComposer(R,RT);COMP.setPixelRatio(1);COMP.setSize(W,HG);COMP.addPass(new RenderPass(S,CAM));
export let GTAO=null,BOKEH=null,BLOOM=null;
if(FX.includes('ao')){GTAO=new GTAOPass(S,CAM,W,HG);GTAO.blendIntensity=1;
 GTAO.updateGtaoMaterial({radius:1.6,distanceExponent:1.6,thickness:3,scale:1.15,samples:QL?8:12,distanceFallOff:1,screenSpaceRadius:false});
 GTAO.updatePdMaterial({lumaPhi:10,depthPhi:2,normalPhi:3,radius:7,radiusExponent:1,rings:2,samples:QL?8:12});COMP.addPass(GTAO);}
if(FX.includes('dof')){BOKEH=new BokehPass(S,CAM,{focus:30,aperture:.00012,maxblur:.0042});COMP.addPass(BOKEH);}
if(FX.includes('bloom')){BLOOM=new UnrealBloomPass(new THREE.Vector2(W/2,HG/2),.6,.6,2.4);COMP.addPass(BLOOM);}
COMP.addPass(new OutputPass());
S.add(new THREE.HemisphereLight(0xffffff,0xb8a890,1.75));
export const SUN=new THREE.DirectionalLight(0xffffff,2.3);SUN.castShadow=true;SUN.shadow.mapSize.set(2048,2048);
Object.assign(SUN.shadow.camera,{left:-34,right:34,top:34,bottom:-34,near:1,far:160});SUN.shadow.bias=-.0004;SUN.shadow.radius=7;SUN.shadow.blurSamples=QL?8:14;S.add(SUN);S.add(SUN.target);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(1200,1200),new THREE.ShadowMaterial({opacity:.24,color:new THREE.Color('#3a2a10')}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;S.add(ground);
export const GROUND=ground;
// dot grid on the floor (texture) gives the camera something to parallax against
{const c=document.createElement('canvas');c.width=c.height=128;const g=c.getContext('2d');g.fillStyle='rgba(26,26,58,.10)';g.beginPath();g.arc(64,64,5,0,7);g.fill();
 const tx=new THREE.CanvasTexture(c);tx.wrapS=tx.wrapT=THREE.RepeatWrapping;tx.repeat.set(300,300);tx.colorSpace=THREE.SRGBColorSpace;
 const m=new THREE.Mesh(new THREE.PlaneGeometry(1200,1200),new THREE.MeshBasicMaterial({map:tx,transparent:true,depthWrite:false}));m.rotation.x=-Math.PI/2;m.position.y=.01;S.add(m);}
// camera rig: tweened by GSAP; handheld drift added at render so no frame is ever static
export const RIG={x:0,y:8,z:30,tx:0,ty:3,tz:0,roll:0,fov:32,drift:1,shake:0,dof:1,focus:0,breath:1};
export function cam(t,dur,o,ease='inOutQuint'){if(dur<=0){TL.set(RIG,o,t);}else TL.to(RIG,{...o,duration:dur,ease},t);return t+dur;}
export const POST={zoom:0,dx:0,dy:0,rgb:0,flash:0,uiBlurX:0,uiBlurY:0,spin:0,cx:960,cy:540};
// ---------- voxels ----------
const edge=(()=>{const c=document.createElement('canvas');c.width=c.height=64;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,64,64);for(let k=0;k<9;k++){g.strokeStyle=`rgba(40,28,10,${(.075*(1-k/9)**1.6).toFixed(3)})`;g.lineWidth=1;g.strokeRect(k+.5,k+.5,63-2*k,63-2*k);}
 g.strokeStyle='rgba(255,255,255,.55)';g.lineWidth=1;g.beginPath();g.moveTo(2,1.5);g.lineTo(62,1.5);g.moveTo(1.5,2);g.lineTo(1.5,62);g.stroke();g.strokeStyle='rgba(30,20,10,.22)';g.lineWidth=1.2;g.strokeRect(.6,.6,62.8,62.8);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;})();
const BOX=new THREE.BoxGeometry(1,1,1);
function voxMat(){const m=new THREE.MeshStandardMaterial({map:edge,roughness:.74,metalness:0});
 m.onBeforeCompile=sh=>{sh.vertexShader=sh.vertexShader.replace('#include <common>',`#include <common>
attribute vec2 aoMask;attribute float aoK;varying float vAO;varying float vKey;
float nb(ivec3 d){int idx=(d.x+1)*9+(d.y+1)*3+(d.z+1);if(idx==13)return 0.;if(idx>13)idx-=1;float m=idx<13?aoMask.x:aoMask.y;int b=idx<13?idx:idx-13;return mod(floor(m/exp2(float(b))),2.);}`).replace('#include <begin_vertex>',`#include <begin_vertex>
{ivec3 N=ivec3(round(normal));ivec3 P=ivec3(sign(position));ivec3 A,B;
 if(N.x!=0){A=ivec3(0,P.y,0);B=ivec3(0,0,P.z);}else if(N.y!=0){A=ivec3(P.x,0,0);B=ivec3(0,0,P.z);}else{A=ivec3(P.x,0,0);B=ivec3(0,P.y,0);}
 float s1=nb(N+A),s2=nb(N+B),c=nb(N+A+B);float occ=(s1>.5&&s2>.5)?3.:s1+s2+c;
 vAO=1.-aoK*occ*.16;vKey=N.y>0?1.05:(N.y<0?.8:mix(.86,1.03,position.y+.5));}`);
  sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying float vAO;varying float vKey;').replace('#include <map_fragment>','#include <map_fragment>\ndiffuseColor.rgb*=vAO*vKey;');};
 return m;}
// voxel neighbour masks on a half-cell lattice (computed once per target state)
function aoMasks(state){const key=(x,y,z)=>x+','+y+','+z,set=new Set(),q=[];
 for(const v of state){if(!(v.s>0)){q.push(null);continue;}const c=v.s/.94;const k=[Math.round(v.p[0]/c*2),Math.round(v.p[1]/c*2),Math.round(v.p[2]/c*2)];q.push(k);set.add(key(...k));}
 return q.map(k=>{if(!k)return[0,0];let a=0,b=0,idx=0;for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++)for(let dz=-1;dz<=1;dz++){if(!dx&&!dy&&!dz)continue;
  if(set.has(key(k[0]+dx*2,k[1]+dy*2,k[2]+dz*2))){if(idx<13)a+=2**idx;else b+=2**(idx-13);}idx++;}return[a,b];});}
const ACTORS=[];
const FACE={clock:Math.PI/2,calendar:Math.PI/2,magnifier:Math.PI/2,neurons:Math.PI/2,two_x:Math.PI/2,qmark:Math.PI/2};
export function modelPts(name,o={}){const m=MODELS[name];if(!m)throw Error('model '+name);const s=o.s||1,ry=(o.ry||0)+(FACE[name]||0),cr=Math.cos(ry),sr=Math.sin(ry);
 return m.map(([x,y,z,c])=>({p:[(x*cr+z*sr)*s+(o.x||0),y*s+(o.y||0),(-x*sr+z*cr)*s+(o.z||0)],c:o.color||c,s:o.vs||s*.94}));}
export class Vox{
 // a pool of instanced cubes moving through segments: assemble / morph / shatter / dissolve / scatterOut / recolor
 constructor(cap,win){this.cap=cap;this.win=win;const geo=BOX.clone();this.aoM=new THREE.InstancedBufferAttribute(new Float32Array(cap*2),2);this.aoK=new THREE.InstancedBufferAttribute(new Float32Array(cap),1);geo.setAttribute('aoMask',this.aoM);geo.setAttribute('aoK',this.aoK);
  this.mesh=new THREE.InstancedMesh(geo,voxMat(),cap);
  this.mesh.castShadow=true;this.mesh.receiveShadow=true;this.mesh.frustumCulled=false;this.g=new THREE.Group();this.g.add(this.mesh);S.add(this.g);
  this.segs=[];this.state=null;this.mb=1;const c=new THREE.Color();for(let i=0;i<cap;i++)this.mesh.setColorAt(i,c.set('#fff'));ACTORS.push(this);
  this.tmpC=new THREE.Color();this.cA=new THREE.Color();this.cB=new THREE.Color();}
 _fill(pts){const n=pts.length,o=[];for(let i=0;i<this.cap;i++){const q=pts[i%Math.max(1,n)]||{p:[0,0,0],c:'#fff',s:0};o.push({p:q.p.slice(),c:q.c,s:i<n?q.s:0});}return o;}
 _sortKey(a){return a.map((q,i)=>[q.s>0?q.p[1]*1000+q.p[0]*3+q.p[2]:1e9+i,i]).sort((x,y)=>x[0]-y[0]).map(x=>x[1]);}
 assemble(t0,dur,pts,o={}){const to=this._fill(pts),r=rng(o.seed||7),R0=o.r||18;const fr=to.map(q=>{const a=r()*6.283,b=(r()-.3)*2,d=R0*(.4+.6*r());
   return{p:[q.p[0]+Math.cos(a)*d+(o.dir?o.dir[0]:0),q.p[1]+Math.abs(b)*d*.6+(o.dir?o.dir[1]:6),q.p[2]+Math.sin(a)*d+(o.dir?o.dir[2]:0)],c:q.c,s:0};});
  const ys=to.map(q=>q.p[1]),y0=Math.min(...ys),y1=Math.max(...ys)+1e-3;
  const xs=to.map(q=>q.p[0]),x0=Math.min(...xs),x1=Math.max(...xs)+1e-3;const del=to.map((q,i)=>(o.order==='rand'?r():o.order==='x'?(q.p[0]-x0)/(x1-x0):(q.p[1]-y0)/(y1-y0))*(o.stag??.55)*dur*(.92+.08*r())+r()*.035*dur);
  this.segs.push({t0,dur,k:'move',land:o.land??1,fr,to,del,each:dur*(1-(o.stag??.55)),arc:o.arc??3,ease:o.ease||eLand,spin:o.spin??2.5,r:rng(o.seed||7)});this.state=to;return t0+dur;}
 extrude(t0,dur,pts,o={}){/* columns grow straight up from the floor (no flight, no clipping), eased with overshoot-settle */const to=this._fill(pts),vis=to.filter(q=>q.s>0),yb=Math.min(...vis.map(q=>q.p[1]));
  const fr=to.map(q=>({p:[q.p[0],yb,q.p[2]],c:q.c,s:q.s*.35}));this.segs.push({t0,dur,k:'move',fr,to,del:to.map(()=>0),each:dur,arc:0,ease:E(o.ease||'settle'),spin:0,r:rng(1),land:0});this.state=to;return t0+dur;}
 drain(t0,dur,yMax,o={}){/* cubes above yMax shrink away in place, top layer first */const fr=this.state,ys=fr.filter(q=>q.s>0).map(q=>q.p[1]),y1=Math.max(...ys)+1e-3,st=o.stag??.6;
  const to=fr.map(q=>q.p[1]>yMax?{...q,p:q.p.slice(),s:0}:{...q,p:q.p.slice()});const del=fr.map(q=>q.p[1]>yMax?(y1-q.p[1])/Math.max(1e-3,y1-yMax)*st*dur:0);
  this.segs.push({t0,dur,k:'move',fr,to,del,each:dur*(1-st),arc:0,ease:E('outQuint'),spin:0,r:rng(2),land:0});this.state=to;return t0+dur;}
 morph(t0,dur,pts,o={}){const fr=this.state.map(q=>({...q,p:q.p.slice()})),to0=this._fill(pts);const a=this._sortKey(fr),b=this._sortKey(to0);const to=new Array(this.cap);
  for(let k=0;k<this.cap;k++)to[a[k]]=to0[b[k]];
  for(let i=0;i<this.cap;i++){if(fr[i].s===0&&to[i].s>0)fr[i].p=to[i].p.slice();}
  const r=rng(o.seed||11),del=fr.map(()=>r()*(o.stag??.35)*dur);this.segs.push({t0,dur,k:'move',fr,to,del,each:dur*(1-(o.stag??.35)),arc:o.arc??4,ease:o.ease||eMorph,spin:o.spin??1.2,r,land:o.land??.6});this.state=to;return t0+dur;}
 to(t0,dur,fn,o={}){/* fn(q,i)->new q : transform current state (e.g. recolor, offset) */const fr=this.state,to=fr.map((q,i)=>fn({...q,p:q.p.slice()},i));const r=rng(o.seed||3);
  const del=fr.map((q,i)=>(o.del?o.del(q,i):r()*(o.stag??.2))*dur);this.segs.push({t0,dur,k:'move',fr,to,del,each:dur*(1-(o.stag??.2)),arc:o.arc??0,ease:o.ease||eP3o,spin:o.spin??0,r});this.state=to;return t0+dur;}
 shatter(t0,dur,o={}){const fr=this.state,r=rng(o.seed||5),c=o.c||[0,4,0];const v=fr.map(q=>{const d=[q.p[0]-c[0],q.p[1]-c[1],q.p[2]-c[2]],n=Math.hypot(...d)+.3,sp=(o.pow||14)*(.5+r());
   return[d[0]/n*sp+(r()-.5)*4,(o.up??8)+r()*8,d[2]/n*sp+(r()-.5)*4+(o.toward||0)];});
  const ax=fr.map(()=>[r()-.5,r()-.5,r()-.5]);this.segs.push({t0,dur,k:'phys',fr,v,ax,g:o.g||-38,floor:o.floor??.5,rest:o.rest??.32});
  this.state=fr.map((q,i)=>({...q,p:this._phys(fr[i].p,v[i],dur,o.g||-38,o.floor??.5,o.rest??.32)}));return t0+dur;}
 _phys(p,v,t,g,fl,rs){let x=p[0],y=p[1],z=p[2],vx=v[0],vy=v[1],vz=v[2];const dt=1/120;let k=Math.floor(t/dt);
  for(let s=0;s<k;s++){vy+=g*dt;x+=vx*dt;y+=vy*dt;z+=vz*dt;if(y<fl){y=fl;vy=-vy*rs;vx*=.7;vz*=.7;}}return[x,y,z];}
 dissolve(t0,dur,o={}){const fr=this.state,r=rng(o.seed||9),to=fr.map(q=>({p:[q.p[0]+(r()-.5)*(o.spread??2),q.p[1]+(o.rise??3)*(.5+r()),q.p[2]+(r()-.5)*(o.spread??2)],c:o.c||'#F3E6D0',s:0}));
  const del=fr.map(q=>(o.order==='y'?1-(q.p[1]/20):r())*(o.stag??.6)*dur);this.segs.push({t0,dur,k:'move',fr,to,del,each:dur*(1-(o.stag??.6)),arc:0,ease:E('inQuint'),spin:o.spin??3,r,fade:1,land:0});this.state=to;return t0+dur;}
 hide(t){this.segs.push({t0:t,dur:0,k:'hide'});this.state=this.state.map(q=>({...q,s:0}));return t;}
 _at(t,i,out){let seg=null;for(const s of this.segs){if(t>=s.t0)seg=s;else break;}
  if(!seg){out.s=0;return;}
  if(seg.k==='hide'){out.s=0;return;}
  if(seg.k==='phys'){out.sq=0;out.ak=0;const tt=Math.min(t-seg.t0,seg.dur);const q=seg.fr[i];const p=this._phys(q.p,seg.v[i],tt,seg.g,seg.floor,seg.rest);out.p=p;out.s=q.s;out.c0=q.c;out.c1=q.c;out.u=1;out.rot=tt*6;out.ax=seg.ax[i];return;}
  const a=seg.fr[i],b=seg.to[i];const u=clamp((t-seg.t0-seg.del[i])/Math.max(1e-3,seg.each)),e=seg.ease(u);
  out.p=[lerp(a.p[0],b.p[0],e),lerp(a.p[1],b.p[1],e)+Math.sin(Math.PI*clamp(u))*seg.arc,lerp(a.p[2],b.p[2],e)];
  out.s=seg.fade?lerp(a.s,b.s,e):(a.s===0&&b.s>0?b.s*eBack(u):(b.s===0&&a.s>0?a.s*(1-E('fall')(u)):lerp(a.s,b.s,e)));out.c0=a.c;out.c1=b.c;out.u=e;out.rot=seg.spin*(1-e)*(u>0&&u<1?1:0)*3;out.ax=[.6,.3,.5];
  out.sq=0;if(seg.land&&b.s>0&&u>.42&&u<1){const k=(u-.42)/.58;out.sq=seg.land*.3*Math.sin(Math.PI*Math.min(1,k*1.6))*Math.exp(-k*3.2)*(k<.625?1:Math.cos((k-.625)*9));}
  if(!seg.mask)seg.mask=aoMasks(seg.to);out.m=seg.mask[i];out.ak=b.s>0?clamp((u-.55)/.45)**1.5:0;}
 update(t){const vis=t>=this.win[0]&&t<this.win[1];this.g.visible=vis;if(!vis)return;
  const m=this.mesh,M=new THREE.Matrix4(),Q=new THREE.Quaternion(),P=new THREE.Vector3(),Sc=new THREE.Vector3(),A={},B={},dir=new THREE.Vector3(),zA=new THREE.Vector3(0,0,1),Qs=new THREE.Quaternion(),ax=new THREE.Vector3();
  for(let i=0;i<this.cap;i++){this._at(t,i,A);if(!A.s||A.s<.002){M.makeScale(0,0,0);m.setMatrixAt(i,M);continue;}
   this._at(t-1/30,i,B);P.set(...A.p);
   let st=1;if(this.mb&&B.s){dir.set(A.p[0]-B.p[0],A.p[1]-B.p[1],A.p[2]-B.p[2]);const sp=dir.length()*30;if(sp>6){st=1+Math.min(2.2,(sp-6)*.045);Qs.setFromUnitVectors(zA,dir.normalize());}}
   if(A.rot){ax.set(...A.ax).normalize();Q.setFromAxisAngle(ax,A.rot);}else Q.identity();
   if(st>1){Q.copy(Qs);Sc.set(A.s*.9,A.s*.9,A.s*st);}else if(A.sq){const q=A.sq;Sc.set(A.s*(1+q*.55),A.s*(1-q),A.s*(1+q*.55));P.y-=A.s*q*.5;}else Sc.set(A.s,A.s,A.s);
   const mm=A.m||[0,0];this.aoM.setXY(i,mm[0],mm[1]);this.aoK.setX(i,A.ak||0);
   M.compose(P,Q,Sc);m.setMatrixAt(i,M);
   if(A.c0===A.c1)this.tmpC.set(A.c0);else{this.cA.set(A.c0);this.cB.set(A.c1);this.tmpC.copy(this.cA).lerp(this.cB,clamp(A.u));}
   m.setColorAt(i,this.tmpC);}
  m.instanceMatrix.needsUpdate=true;m.instanceColor.needsUpdate=true;this.aoM.needsUpdate=true;this.aoK.needsUpdate=true;}
}
// photo -> voxels: sample a card's photo into a coloured voxel mosaic standing where the card stands (for photo<->voxel transitions)
export function photoPts(name,o={}){const t=TEX[name];if(!t)throw Error('no tex '+name);const im=t.image,a=im.width/im.height,h=o.h||5,cols=o.cols||36,cell=h*a/cols,rows=Math.round(h/cell);
 const c=document.createElement('canvas');c.width=cols;c.height=rows;const g=c.getContext('2d');g.drawImage(im,0,0,cols,rows);const d=g.getImageData(0,0,cols,rows).data;const pts=[];const ry=o.ry||0,cr=Math.cos(ry),sr=Math.sin(ry);
 const y0=(o.y||0)+(o.base?h*.022+cell/2:-h/2+cell/2);
 for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){const k=(j*cols+i)*4;if(d[k+3]<128)continue;const lx=(i-cols/2+.5)*cell,lz=o.depth?0:0;
  const col='#'+[d[k],d[k+1],d[k+2]].map(v=>Math.round(Math.min(255,v*1.04+6)).toString(16).padStart(2,'0')).join('');
  pts.push({p:[(o.x||0)+lx*cr,y0+(rows-1-j)*cell,(o.z||0)-lx*sr],c:col,s:cell*.96});}
 return pts;}
export function shake(t,amp=.25,dur=.5){TL.fromTo(RIG,{shake:amp},{shake:0,duration:dur,ease:'outExpo',immediateRender:false},t);return t;}
export function fade(g,t,dur,to,from){const ms=[];g.traverse(o=>{if(o.material)ms.push(o.material);});const m=ms;if(from!==undefined)TL.fromTo(m,{opacity:from},{opacity:to,duration:dur,ease:'outQuint',immediateRender:false},t);else TL.to(m,{opacity:to,duration:dur,ease:'outQuint'},t);return t+dur;}
// ---------- photo cutout cards (real alpha, real shadows, true parallax) ----------
const TEX={};export const IMGS=window.IMGS||{};
export function loadTextures(list){const ld=new THREE.TextureLoader();return Promise.all(list.map(n=>new Promise((res,rej)=>ld.load(`${window.IMG_BASE||"img/"}${n}.png`,t=>{t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;TEX[n]=t;res();},undefined,()=>rej(Error('tex '+n))))));}
// unified photo treatment: one warm grade, halftone + paper fibre, scissor-cut white paper outline (dilated alpha), contact blob
const CARD_FS=`
uniform vec2 cMg;uniform vec2 cTx;uniform float cOut;uniform float cHt;uniform float cDuo;uniform vec3 cDA;uniform vec3 cDB;
float h21(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
float aAt(vec2 uv){vec2 q=(uv-.5)*(1.+2.*cMg)+.5;if(q.x<0.||q.y<0.||q.x>1.||q.y>1.)return 0.;return texture2D(map,q).a;}`;
function gradeMat(t,o){const asp=t.image.width/t.image.height;const mg=o.outline??.022;const mat=new THREE.MeshBasicMaterial({map:t,transparent:true,alphaTest:.02,side:THREE.DoubleSide,fog:o.fog??true,toneMapped:false});
 mat.userData.u={cMg:{value:new THREE.Vector2(mg/asp,mg)},cTx:{value:new THREE.Vector2(t.image.width,t.image.height)},cOut:{value:o.outline===0?0:1},cHt:{value:o.halftone??1},cDuo:{value:o.duo??0},cDA:{value:new THREE.Color(o.dA||'#1A1A3A')},cDB:{value:new THREE.Color(o.dB||'#FFF4E2')}};
 mat.onBeforeCompile=sh=>{Object.assign(sh.uniforms,mat.userData.u);sh.fragmentShader=sh.fragmentShader.replace('#include <map_pars_fragment>','#include <map_pars_fragment>'+CARD_FS).replace('#include <map_fragment>',`
 {float op=diffuseColor.a;vec2 uv=vMapUv;vec2 q=(uv-.5)*(1.+2.*cMg)+.5;bool inside=q.x>=0.&&q.y>=0.&&q.x<=1.&&q.y<=1.;vec4 tc=inside?texture2D(map,q):vec4(0.);
  float l=dot(tc.rgb,vec3(.299,.587,.114));vec3 g=mix(vec3(l),tc.rgb,.80);g=g*vec3(1.035,1.,.90)+vec3(.04,.03,.012);g=mix(g,vec3(.10,.10,.24),.06*(1.-l));
  vec2 sp=gl_FragCoord.xy*mat2(.866,-.5,.5,.866)/4.2;float d=length(fract(sp)-.5);float r=.62*sqrt(clamp(1.-l,0.,1.));float dotm=1.-smoothstep(r-.12,r+.12,d);
  if(cDuo>0.){vec3 du=mix(cDA,cDB,smoothstep(.04,.96,pow(l,.85)));g=mix(g,du,cDuo);g=mix(g,cDA,clamp(cHt*.24*dotm*cDuo,0.,1.));g*=1.-(1.-cDuo)*cHt*.16*dotm;}else g*=1.-cHt*.16*dotm;g*=.965+.07*h21(floor(uv*cTx*.5));
  float a=tc.a;float ol=0.;if(cOut>.5&&a<.6){float ang=atan(uv.y-.5,uv.x-.5);float rr=1.+.28*sin(ang*7.+1.3)+.18*sin(ang*13.+.4);
   for(int k=0;k<16;k++){float th=6.2832*float(k)/16.;ol=max(ol,aAt(uv+vec2(cos(th),sin(th))*cMg*.85*rr));ol=max(ol,aAt(uv+vec2(cos(th),sin(th))*cMg*.45*rr));}}
  vec3 paper=vec3(1.,.985,.95)*(.97+.03*h21(floor(uv*700.)));diffuseColor=vec4(mix(paper,g,a),max(a,step(.5,ol))*op);}`);};
 return mat;}
const BLOB=(()=>{const c=document.createElement('canvas');c.width=c.height=128;const g=c.getContext('2d');const gr=g.createRadialGradient(64,64,0,64,64,64);gr.addColorStop(0,'rgba(40,26,8,.55)');gr.addColorStop(.5,'rgba(40,26,8,.22)');gr.addColorStop(1,'rgba(40,26,8,0)');g.fillStyle=gr;g.fillRect(0,0,128,128);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;})();
export function card(name,h,win,o={}){const t=TEX[name];if(!t)throw Error('no tex '+name);const a=t.image.width/t.image.height;const mg=o.outline??.022;
 const mat=gradeMat(t,o);const sc=1+2*mg;
 const m=new THREE.Mesh(new THREE.PlaneGeometry(h*a+2*h*mg,h*sc),mat);m.castShadow=o.shadow??true;m.userData.noAO=1;
 const dt=t.clone();dt.needsUpdate=true;dt.wrapS=dt.wrapT=THREE.ClampToEdgeWrapping;dt.repeat.set(1+2*mg/a,1+2*mg);dt.offset.set(-mg/a,-mg);
 m.customDepthMaterial=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,map:dt,alphaTest:.5});
 const g=new THREE.Group();m.position.y=o.base?h*sc/2:0;g.add(m);
 if(o.base&&o.blob!==false){const b=new THREE.Mesh(new THREE.PlaneGeometry(h*a*1.15,h*.42),new THREE.MeshBasicMaterial({map:BLOB,transparent:true,depthWrite:false,toneMapped:false}));b.rotation.x=-Math.PI/2;b.position.y=.03;b.userData.noAO=1;g.add(b);}g.userData.win=win;g.userData.mesh=m;S.add(g);CARDS.push(g);if(o.p)g.position.set(...o.p);if(o.r)g.rotation.set(...o.r);return g;}
export const CARDS=[];
// generic 3D objects with a time window
export const OBJS=[];export function obj(o3,win){o3.userData.win=win;S.add(o3);OBJS.push(o3);return o3;}
// canvas-texture planes for in-world type/graphics (crisp at 2x)
export function texPlane(wu,hu,draw,win,o={}){const c=document.createElement('canvas');const px=o.px||110;c.width=Math.round(wu*px);c.height=Math.round(hu*px);const g=c.getContext('2d');draw(g,c.width,c.height);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;const m=new THREE.Mesh(new THREE.PlaneGeometry(wu,hu),new THREE.MeshBasicMaterial({map:t,transparent:true,side:THREE.DoubleSide,toneMapped:false,fog:false}));
 m.castShadow=o.shadow??false;m.userData.noAO=1;if(o.shadow)m.customDepthMaterial=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,map:t,alphaTest:.5});const gr=new THREE.Group();gr.add(m);gr.userData.mesh=m;return obj(gr,win);}
// ---------- depth field: 3 Z-layers of drifting voxel motes, world-fixed and wrapped around the rig target -> real parallax ----------
export const MOTES={on:1,amt:1};
{const N=66,mm=new THREE.InstancedMesh(BOX,new THREE.MeshStandardMaterial({roughness:.8,map:edge}),N);mm.frustumCulled=false;mm.userData.noAO=1;mm.castShadow=false;S.add(mm);
 const r=rng(4242),pal=['#BFD0FF','#FFD9C2','#E9DCC4','#F2E2C6','#FFE3A3','#2F6BFF','#E9DCC4','#FFD9C2'],P=[],c=new THREE.Color();
 for(let i=0;i<N;i++){const L=i%3;/*0 far,1 mid,2 near*/P.push({x:r()*90,y:L===0?4+r()*16:L===1?2+r()*10:1+r()*8,z:L===0?-(18+r()*40):L===1?-(4+r()*14):8+r()*12,s:L===0?.35+r()*.4:L===1?.16+r()*.18:.08+r()*.1,ph:r()*6.28,sp:.3+r()*.5,ax:[r()-.5,r()-.5,r()-.5]});mm.setColorAt(i,c.set(pal[Math.floor(r()*pal.length)]));}
 const M=new THREE.Matrix4(),Q=new THREE.Quaternion(),V=new THREE.Vector3(),Sc=new THREE.Vector3(),A=new THREE.Vector3();
 MOTES.update=t=>{mm.visible=!!MOTES.on;if(!MOTES.on)return;for(let i=0;i<N;i++){const p=P[i];let dx=((p.x-RIG.tx)%90+90)%90-45;const edgeF=clamp((45-Math.abs(dx))/8);
  V.set(RIG.tx+dx+Math.sin(t*p.sp*.4+p.ph)*.6,p.y+Math.sin(t*p.sp+p.ph)*.35,RIG.tz+p.z);A.set(...p.ax).normalize();Q.setFromAxisAngle(A,t*p.sp+p.ph);const ss=p.s*edgeF*MOTES.amt;Sc.set(ss,ss,ss);M.compose(V,Q,Sc);mm.setMatrixAt(i,M);}
  mm.instanceMatrix.needsUpdate=true;};}
// ---------- DOM layer ----------
export const UI=document.getElementById('ui');
export function H(p,html){const t=document.createElement('template');t.innerHTML=html.trim();const e=t.content.firstChild;(p||UI).appendChild(e);return e;}
export function layer(t0,t1,cls=''){const e=H(UI,`<div class="lay ${cls}"></div>`);TL.set(e,{autoAlpha:1},t0);TL.set(e,{autoAlpha:0},t1);gsap.set(e,{autoAlpha:0});return e;}
// masked per-char rise (SplitText) with overshoot
export function typeIn(el,t,o={}){const sp=new SplitText(el,{type:'chars,words',charsClass:'ch'});el.querySelectorAll('.ch').forEach(c=>{c.style.display='inline-block';});
 const words=el.querySelectorAll('div[style*="inline-block"]');
 if(o.mask!==false){sp.words.forEach(wd=>{wd.style.overflow='hidden';wd.style.paddingBottom='0.08em';wd.style.marginBottom='-0.08em';wd.style.verticalAlign='top';});}
 TL.from(sp.chars,{yPercent:o.y??110,rotate:o.rot??0,opacity:o.fade?0:1,duration:o.d??.42,ease:o.ease||'springBouncy',stagger:o.st??.022},t);return sp;}
export function typeOut(sp,t,o={}){TL.to(sp.chars,{yPercent:o.y??-110,duration:o.d??.3,ease:'inQuint',stagger:o.st??.012},t);}
// ---------- per-frame ----------
const post=document.getElementById('post'),pg=post.getContext('2d');const flash=document.getElementById('flash');
const mbf=document.getElementById('mbblur');const grain=document.getElementById('grain');
let READYFNS=[];export const onFrame=[];
function noise(t,k){return Math.sin(t*.73+k)*.6+Math.sin(t*1.37+k*2.1)*.3+Math.sin(t*2.9+k*3.3)*.1;}
window.seek=function(t){TL.time(t,false);
 for(const f of onFrame)f(t);
 const d=RIG.drift,br=RIG.breath;
 // always-alive camera: handheld drift + a slow breathing dolly + a small orbit around the target, so no shot ever stops
 const ox=RIG.x-RIG.tx,oz=RIG.z-RIG.tz,yaw=(Math.sin(t*.41+.7)*.022+Math.sin(t*.17)*.018)*br,dol=1-(Math.sin(t*.67)*.025+Math.sin(t*.29+2)*.02)*br;
 const cx=RIG.tx+(ox*Math.cos(yaw)-oz*Math.sin(yaw))*dol,cz=RIG.tz+(ox*Math.sin(yaw)+oz*Math.cos(yaw))*dol;
 CAM.position.set(cx+noise(t,1)*.26*d,RIG.ty+(RIG.y-RIG.ty)*dol+noise(t,2)*.16*d,cz+noise(t,3)*.2*d);
 const sh=RIG.shake;const sx=sh?Math.sin(t*61)*sh:0,sy=sh?Math.cos(t*47)*sh:0;
 CAM.lookAt(RIG.tx+noise(t,4)*.1*d+sx,RIG.ty+noise(t,5)*.07*d+sy,RIG.tz);CAM.rotation.z+=RIG.roll;CAM.fov=RIG.fov;CAM.updateProjectionMatrix();
 SUN.position.set(RIG.tx+18,RIG.ty+40,RIG.tz+22);SUN.target.position.set(RIG.tx,0,RIG.tz);
 for(const a of ACTORS)a.update(t);MOTES.update(t);
 for(const c of CARDS)c.visible=t>=c.userData.win[0]&&t<c.userData.win[1];
 for(const o of OBJS)o.visible=t>=o.userData.win[0]&&t<o.userData.win[1];
 CAM.updateMatrixWorld();projectPins(t);
 if(BOKEH){const f=Math.hypot(CAM.position.x-RIG.tx,CAM.position.y-RIG.ty,CAM.position.z-RIG.tz)+RIG.focus;BOKEH.uniforms.focus.value=f;BOKEH.uniforms.aperture.value=.00011*RIG.dof*(30/Math.max(8,f));}
 COMP.render();
 grain.style.backgroundPosition=`${(Math.round(t*30)*137)%256}px ${(Math.round(t*30)*251)%256}px`;
 // 2D post: zoom blur / directional blur / rgb split rendered from the GL buffer
 const z=POST.zoom,dx=POST.dx,dy=POST.dy,rg=POST.rgb;
 const spn=POST.spin;
 if(Math.abs(spn)>.002){post.style.visibility='visible';pg.globalAlpha=1;pg.drawImage(glc,0,0);const N=8;  // rotational motion blur around (cx,cy)
  for(let k=1;k<=N;k++){pg.save();pg.globalAlpha=1/(k+1);pg.translate(POST.cx,POST.cy);pg.rotate(-spn*k/N);pg.translate(-POST.cx,-POST.cy);pg.drawImage(glc,0,0);pg.restore();}pg.globalAlpha=1;}
 else if(z>.002||Math.abs(dx)>.5||Math.abs(dy)>.5||rg>.5){post.style.visibility='visible';pg.globalAlpha=1;pg.drawImage(glc,0,0);const N=8;
  for(let k=1;k<=N;k++){const f=k/N;pg.globalAlpha=1/(k+1);const s=1+z*f;pg.drawImage(glc,W/2-W*s/2+dx*f,HG/2-HG*s/2+dy*f,W*s,HG*s);}
  if(rg>.5){pg.globalAlpha=.45;pg.globalCompositeOperation='multiply';pg.filter='none';pg.drawImage(glc,rg,0);pg.drawImage(glc,-rg,0);pg.globalCompositeOperation='source-over';}
  pg.globalAlpha=1;}else post.style.visibility='hidden';
 flash.style.opacity=POST.flash;
 const bx=POST.uiBlurX,by=POST.uiBlurY;if(bx>.3||by>.3){mbf.setAttribute('stdDeviation',`${bx.toFixed(1)} ${by.toFixed(1)}`);UI.style.filter='url(#mb)';}else UI.style.filter='none';
};
// whip: camera move + directional blur on GL and UI + a whoosh cue
export function whip(t,dur,o,dir=[1,0]){cam(t,dur,o,'inOutQuint');TL.to(POST,{dx:dir[0]*90,dy:dir[1]*90,uiBlurX:Math.abs(dir[0])*26,uiBlurY:Math.abs(dir[1])*26,duration:dur/2,ease:'fall'},t);
 TL.to(POST,{dx:0,dy:0,uiBlurX:0,uiBlurY:0,duration:dur/2,ease:'outQuint'},t+dur/2);cue(t,'whoosh','whip');return t+dur;}
export function zoomPunch(t,amt=.12,dur=.35){TL.fromTo(POST,{zoom:amt},{zoom:0,duration:dur,ease:'outQuint',immediateRender:false},t);return t;}
export function flashAt(t,a=.85,d=.28){TL.fromTo(POST,{flash:a},{flash:0,duration:d,ease:'outQuint',immediateRender:false},t);return t;}
// text -> voxel points (raster a word on a canvas, one voxel per cell, extruded `depth` cells)
export function textPts(str,o={}){const cell=o.cell||1,rows=o.rows||14,depth=o.depth||3;const c=document.createElement('canvas');const g=c.getContext('2d');
 const font=`${o.weight||''} ${rows}px ${o.font||"'Archivo Black'"}`;g.font=font;const wpx=Math.ceil(g.measureText(str).width)+4;c.width=wpx;c.height=Math.ceil(rows*1.25);
 g.font=font;g.fillStyle='#000';g.textBaseline='alphabetic';g.fillText(str,2,Math.round(rows*1.02));const d=g.getImageData(0,0,c.width,c.height).data;const pts=[];
 for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){if(d[(y*c.width+x)*4+3]>110)for(let z=0;z<depth;z++)pts.push({p:[(x-c.width/2)*cell+(o.x||0),(c.height-y)*cell+(o.y||0),(z-depth/2+.5)*cell+(o.z||0)],c:o.color||INK,s:cell*.94});}
 if(o.yfloor!==undefined){const y0=Math.min(...pts.map(q=>q.p[1]));pts.forEach(q=>q.p[1]+=o.yfloor-y0+cell/2);}
 return pts;}
export function boxPts(nx,ny,nz,o={}){const cell=o.cell||1,pts=[];for(let y=0;y<ny;y++)for(let x=0;x<nx;x++)for(let z=0;z<nz;z++)pts.push({p:[(x-nx/2+.5)*cell+(o.x||0),(y+.5)*cell+(o.y||0),(z-nz/2+.5)*cell+(o.z||0)],c:typeof o.color==='function'?o.color(x,y,z):(o.color||BL),s:cell*.94});return pts;}
export const offPts=(pts,dx=0,dy=0,dz=0)=>pts.map(q=>({...q,p:[q.p[0]+dx,q.p[1]+dy,q.p[2]+dz]}));
// pin a DOM element to a 3D world point (projected each frame); f(t) may return [x,y,z]
const PINS=[];const _v=new THREE.Vector3();
export function pin(el,f){PINS.push([el,typeof f==='function'?f:()=>f]);return el;}
onFrame.push(t=>{window.__pinT=t;});
export function projectPins(t){for(const [el,f] of PINS){const p=f(t);if(!p)continue;_v.set(...p).project(CAM);el.style.left=((_v.x+1)/2*W).toFixed(1)+'px';el.style.top=((1-_v.y)/2*HG).toFixed(1)+'px';}}
// counter: tween a number into an element's text
export function counter(el,t,dur,from,to,fmt=v=>Math.round(v)+'',ease='outQuint'){const o={v:from};TL.fromTo(o,{v:from},{v:to,duration:dur,ease,immediateRender:false,onUpdate:()=>{el.textContent=fmt(o.v);}},t);el.textContent=fmt(from);
 onFrame.push(tt=>{if(tt<t)el.textContent=fmt(from);});return el;}
// ---------- premium data viz: shared chart furniture (back grid with value ticks, floor grid, per-bar glow) ----------
// o: {x,z,w,h,unit (world units per tick), ticks:[labels], col, glow:[[x,color],..], t (reveal time), title}
const GLOW=(()=>{const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d');const gr=g.createRadialGradient(128,128,0,128,128,128);gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.35,'rgba(255,255,255,.45)');gr.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=gr;g.fillRect(0,0,256,256);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;})();
export function chartGrid(win,o){const W=o.w||20,Hh=o.h||13,un=o.unit||2.5,col=o.col||'#1A1A3A',x0=(o.x||0)-W/2,z=o.z??-3,t=o.t??win[0]+.2,lab=o.ticks||[];
 const back=texPlane(W,Hh,(g,cw,ch)=>{const px=cw/W;g.lineCap='round';
   for(let k=0;k*un<=Hh-.4;k++){const y=ch-k*un*px-2;g.strokeStyle=k===0?'rgba(26,26,58,.55)':'rgba(26,26,58,.16)';g.lineWidth=k===0?6:3;g.setLineDash(k===0?[]:[18,14]);g.beginPath();g.moveTo(px*1.6,y);g.lineTo(cw-px*.4,y);g.stroke();
     if(lab[k]!=null){g.setLineDash([]);g.font=`${px*.62}px 'JetBrains Mono','DM Mono',monospace`;g.fillStyle='rgba(26,26,58,.6)';g.textAlign='right';g.textBaseline='middle';g.fillText(lab[k],px*1.35,y);}}
   g.setLineDash([]);g.strokeStyle='rgba(26,26,58,.07)';g.lineWidth=2;for(let x=px*1.6;x<cw;x+=px*un){g.beginPath();g.moveTo(x,0);g.lineTo(x,ch);g.stroke();}
   if(o.title){g.font=`${px*.5}px 'JetBrains Mono','DM Mono',monospace`;g.fillStyle='rgba(26,26,58,.55)';g.textAlign='left';g.textBaseline='top';g.fillText(o.title,px*1.6,px*.3);}},win,{px:90});
 const bm=back.userData.mesh;bm.position.set(W/2,Hh/2,0);back.position.set(x0,0,z);
 const fl=texPlane(W,7,(g,cw,ch)=>{const px=cw/W;g.strokeStyle='rgba(26,26,58,.10)';g.lineWidth=3;for(let x=px*1.6;x<cw;x+=px*un){g.beginPath();g.moveTo(x,0);g.lineTo(x,ch);g.stroke();}for(let y=0;y<ch;y+=px*un){g.beginPath();g.moveTo(0,y);g.lineTo(cw,y);g.stroke();}
   const fd=g.createLinearGradient(0,0,0,ch);fd.addColorStop(0,'rgba(243,236,224,0)');fd.addColorStop(1,'rgba(243,236,224,1)');g.globalCompositeOperation='destination-out';const fe=g.createLinearGradient(0,0,0,ch);fe.addColorStop(0,'rgba(0,0,0,0)');fe.addColorStop(1,'rgba(0,0,0,1)');g.fillStyle=fe;g.fillRect(0,0,cw,ch);},win,{px:60});
 const fm=fl.userData.mesh;fm.rotation.x=-Math.PI/2;fm.position.set(W/2,.015,3.5);fl.position.set(x0,0,z);
 const glows=(o.glow||[]).map(([gx,gc,gh])=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(7,(gh||10)*1.25),new THREE.MeshBasicMaterial({map:GLOW,color:gc,transparent:true,opacity:0,depthWrite:false,toneMapped:false,fog:false}));m.position.set(gx,(gh||10)*.55,z+.05);m.userData.noAO=1;return obj(m,win);});
 TL.fromTo([back.scale,fl.scale],{x:.001},{x:1,duration:.9,ease:'inOutQuint',immediateRender:false},t);TL.set([back.scale,fl.scale],{x:.001},0);
 TL.fromTo(bm.material,{opacity:0},{opacity:1,duration:.5,ease:'outQuint',immediateRender:false},t);TL.set(bm.material,{opacity:0},0);
 return {back,fl,glows,glowAt:(i,tt,op=.55)=>{TL.fromTo(glows[i].material,{opacity:0},{opacity:op,duration:.6,ease:'outQuint',immediateRender:false},tt);TL.set(glows[i].material,{opacity:0},0);}};}
