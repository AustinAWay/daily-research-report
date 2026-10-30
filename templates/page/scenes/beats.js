// Data-driven beats: one visual idea per scripted line (episode.beats). Each beat lives on its own patch of the voxel stage
// (x = -300*k), the camera whips there on the line's first word and keeps drifting, and the DOM layer carries a few key words.
// Beat types: headline, paper, counter, bars, model, stamp, citations, image. Add your own by extending TYPES.
// Rules baked in: minimal on-screen text, every reveal lands on a spoken word, nothing holds still > 1.5 s, one sound cue per reveal.
import {TL,TM,gsap,Vox,modelPts,textPts,boxPts,card,cam,whip,RIG,POST,layer,H,typeIn,typeOut,zoomPunch,flashAt,shake,cue,counter,E,INK,BL,CO,YE} from '../engine.js';
import {at,atEnd,accent} from './_util.js';
const COL={blue:BL,coral:CO,ink:INK,yellow:YE};const col=c=>COL[c]||c||BL;
export function textures(ep){return (ep.beats||[]).filter(b=>b.image).map(b=>b.image);}
const TYPES={
 headline(b,L0,t0,t1,X){const e=H(L0,`<div class="a h" style="left:120px;top:${b.top||360}px;width:1680px;white-space:normal;font-size:${b.size||130}px">${accent(b.text)}</div>`);
   typeIn(e,at(b.line,b.on)-.12);cue(at(b.line,b.on)-.05,'pop','headline');
   if(b.model){const v=new Vox(4000,[t0,t1]);v.assemble(t0+.1,1.0,modelPts(b.model,{s:b.scale||1}).map(q=>({...q,p:[q.p[0]+X+9,q.p[1],q.p[2]]})),{seed:7});}},
 paper(b,L0,t0,t1){const tag=b.preprint?`<span class="chip" style="position:relative;background:${CO};color:#fff;font-size:24px">PREPRINT</span>`:`<span class="chip" style="position:relative;background:${INK};color:#FFF6E8;font-size:24px">${b.tag||'PEER-REVIEWED'}</span>`;
   const e=H(L0,`<div class="card" style="left:460px;top:170px;width:1000px;padding:56px 64px">
     <div class="m" style="font-size:24px;color:${BL}">${b.venue||''} · ${b.date||''}</div>
     <div class="h" style="font-size:72px;white-space:normal;margin:26px 0">${accent(b.title)}</div>
     <div class="t" style="font-size:32px;margin-bottom:30px">${b.authors||''}</div>${tag}</div>`);
   const t=at(b.line,b.on)-.1;TL.fromTo(e,{yPercent:80,rotation:5,autoAlpha:0},{yPercent:0,rotation:-1.5,autoAlpha:1,duration:.55,ease:'back.out(1.6)',immediateRender:false},t);TL.set(e,{autoAlpha:0},0);
   TL.to(e,{rotation:1,scale:1.03,duration:Math.max(.5,t1-t-.6),ease:'none'},t+.6);cue(t,'page','paper');},
 counter(b,L0,t0,t1){const e=H(L0,`<div class="a" style="left:0;right:0;top:250px;text-align:center"><div class="h n" style="font-size:380px;color:${col(b.color)}">0</div><div class="h" style="font-size:72px;margin-top:20px">${accent(b.label||'')}</div></div>`);
   const n=e.querySelector('.n'),tl=at(b.line,b.on),d=b.dur||.9,dec=b.decimals||0;
   counter(n,tl-d,d,b.from||0,b.to,v=>(b.prefix||'')+v.toFixed(dec)+(b.suffix||''));
   TL.fromTo(e,{autoAlpha:0,scale:.7},{autoAlpha:1,scale:1,duration:.35,ease:'back.out(2)',immediateRender:false},tl-d-.1);TL.set(e,{autoAlpha:0},0);
   zoomPunch(tl,.1,.35);cue(tl,'hit','counter lands');},
 bars(b,L0,t0,t1){const mx=Math.max(...b.bars.map(x=>x.value));
   const e=H(L0,`<div class="a" style="left:200px;top:180px;width:1520px"><div class="h" style="font-size:64px;margin-bottom:50px">${accent(b.title||'')}</div>${b.bars.map((x,i)=>`
     <div class="row" style="position:relative;height:150px"><div class="m" style="font-size:30px">${x.label}</div>
     <div class="bf" style="position:absolute;top:50px;left:0;height:60px;border-radius:30px;width:${1200*x.value/mx}px;background:${col(x.color)};transform-origin:0 50%"></div>
     <div class="h v" style="position:absolute;top:44px;left:${1200*x.value/mx+30}px;font-size:70px">${x.value}${b.unit||''}</div></div>`).join('')}</div>`);
   TL.fromTo(e,{autoAlpha:0},{autoAlpha:1,duration:.3,immediateRender:false},t0+.1);TL.set(e,{autoAlpha:0},0);
   [...e.querySelectorAll('.row')].forEach((r,i)=>{const t=at(b.bars[i].line||b.line,b.bars[i].on);TL.fromTo(r.querySelector('.bf'),{scaleX:0},{scaleX:1,duration:.5,ease:'expo.out',immediateRender:false},t-.05);TL.set(r.querySelector('.bf'),{scaleX:0},0);
     TL.fromTo(r.querySelector('.v'),{autoAlpha:0},{autoAlpha:1,duration:.2,immediateRender:false},t+.25);TL.set(r.querySelector('.v'),{autoAlpha:0},0);cue(t,'tick','bar '+i);});},
 model(b,L0,t0,t1,X){const v=new Vox(6000,[t0,t1]);const t=at(b.line,b.on)-.3;
   v.assemble(t,1.0,modelPts(b.model,{s:b.scale||1.2}).map(q=>({...q,p:[q.p[0]+X,q.p[1],q.p[2]]})),{seed:11});cue(t+.6,'thud','model lands');
   if(b.label){const e=H(L0,`<div class="a h" style="left:0;right:0;top:120px;text-align:center;font-size:90px">${accent(b.label)}</div>`);typeIn(e,t+.3);}
   if(b.shatter_on){const ts=at(b.line,b.shatter_on);v.shatter(ts,1.4,{c:[X,3,0]});shake(ts,.3,.5);cue(ts,'shatter','model breaks');}},
 stamp(b,L0,t0,t1){const t=at(b.line,b.on);const e=H(L0,`<div class="a h" style="left:0;right:0;top:400px;text-align:center;font-size:${b.size||170}px;color:${col(b.color||'coral')}"><span style="display:inline-block;border:14px solid currentColor;border-radius:24px;padding:10px 40px;transform:rotate(-6deg)">${b.text}</span></div>`);
   TL.fromTo(e,{autoAlpha:0,scale:2.2},{autoAlpha:1,scale:1,duration:.2,ease:'inQuint',immediateRender:false},t-.2);TL.set(e,{autoAlpha:0},0);
   shake(t,.35,.45);flashAt(t,.35,.25);cue(t,'stamp',b.text);},
 image(b,L0,t0,t1,X){const t=at(b.line,b.on)-.15;const c=card(b.image,b.h||9,[t0,t1]);c.position.set(X+(b.dx||0),0,0);
   TL.fromTo(c.scale,{x:.001,y:.001},{x:1,y:1,duration:.5,ease:'back.out(1.7)',immediateRender:false},t);cue(t,'pop','image');},
 citations(b,L0,t0,t1){/* "cited this month" card. Numbers come from citations/summary.json via episode.js; never typed by hand. */
   const C=b.data, tN=at(b.line,b.on_count), e=H(L0,`<div class="card" style="left:310px;top:150px;width:1300px;height:780px;padding:50px 60px;overflow:hidden">
     <div class="chip" style="position:relative;display:inline-block;background:${INK};color:#FFF6E8;font-size:26px">CITATION TRACKER</div>
     <div class="p1"><div class="h" style="font-size:84px;margin-top:30px">THIS MONTH, AT LEAST</div><div class="h n" style="font-size:330px;color:${BL}">0</div>
       <div class="m" style="font-size:22px">${C.sources_line}</div></div>
     <div class="p2" style="position:absolute;left:60px;top:150px;right:60px"><div class="h" style="font-size:56px;margin-bottom:30px">OF THE ${C.readable} I COULD READ:</div>
       ${C.rows.map(r=>`<div class="r" style="display:flex;gap:30px;align-items:center;height:120px"><div class="h" style="font-size:110px;width:150px;text-align:right;color:${col(r.color)}">${r.n}</div><div class="h" style="font-size:42px;white-space:normal">${r.label}</div></div>`).join('')}
       <div class="m" style="font-size:18px;margin-top:20px;white-space:normal">${C.footer||''}</div></div></div>`);
   const n=e.querySelector('.n');counter(n,tN-1.0,1.0,0,C.at_least,v=>Math.round(v)+'');
   TL.fromTo(e,{yPercent:120,rotation:6},{yPercent:0,rotation:-2,duration:.55,ease:'back.out(1.6)',immediateRender:false},t0+.05);TL.set(e,{yPercent:120},0);cue(t0+.1,'whoosh','cite card');cue(tN,'hit','count lands');
   const p2=at(b.line,b.on_breakdown)-.2,p1=e.querySelector('.p1'),q2=e.querySelector('.p2');
   TL.to(p1,{autoAlpha:0,y:-40,duration:.18,ease:'power2.in'},p2-.2);   // old content fully gone before the new wipe (no doubled text)
   TL.fromTo(q2,{autoAlpha:0},{autoAlpha:1,duration:.01,immediateRender:false},p2);TL.set(q2,{autoAlpha:0},0);
   [...q2.querySelectorAll('.r')].forEach((r,i)=>{const t=at(b.line,C.rows[i].on);TL.fromTo(r,{autoAlpha:0,x:-40},{autoAlpha:1,x:0,duration:.3,ease:'power3.out',immediateRender:false},t-.08);TL.set(r,{autoAlpha:0},0);cue(t,'tick','row '+i);});},
};
export function build(ep){
  const B=(ep.beats||[]).map((b,k)=>({...b,k}));
  B.forEach((b,i)=>{
    const t0=b.t0??(at(b.line)-.2), nx=B[i+1], t1=nx?(nx.t0??(at(nx.line)-.2)):atEnd(b.until||b.line)+.4, X=-300*(i+1);
    const L0=layer(t0,t1);
    whip(t0-.15,.4,{x:X+(b.cx||0),y:b.cy||7,z:b.cz||28,tx:X,ty:4,tz:0,fov:32,roll:0},[(i%2?-1:1),0]);
    cam(t0+.3,Math.max(.6,t1-t0-.3),{z:(b.cz||28)-2.5,x:X+(b.cx||0)+(i%2?1.2:-1.2)},'inOutSine');   // always-moving push
    TL.fromTo(L0,{scale:1},{scale:1.02,duration:Math.max(.5,t1-t0),ease:'none',immediateRender:false},t0);
    const f=TYPES[b.type];if(!f)throw Error('unknown beat type '+b.type);f(b,L0,t0,t1,X);
  });
}
