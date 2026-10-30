// Sources end card: every source the script relies on, with its date and type (preprint labelled), plus image credits.
import {TL,TM,gsap,cam,whip,layer,H,cue,INK,BL,CO} from '../engine.js';
export function build(ep){
  const t0=TM.marks.endcard, t1=TM.marks.end||TM.dur, XE=-12000; if(!(t1>t0))return;
  const L0=layer(t0-.1,t1+1);
  whip(t0-.3,.45,{x:XE,y:6,z:26,tx:XE,ty:4,tz:0,fov:32,roll:0},[0,1]);
  const rows=(ep.sources||[]).map(s=>`<div style="margin-bottom:22px"><span class="m" style="font-size:20px;color:${s.preprint?CO:BL}">${s.preprint?'PREPRINT · NOT PEER-REVIEWED':(s.kind||'PAPER')}</span><div class="t" style="font-size:30px;line-height:1.25">${s.cite}</div></div>`).join('');
  const c=H(L0,`<div class="card" style="left:150px;top:90px;width:1620px;height:900px;padding:60px 70px">
    <div class="h" style="font-size:64px;margin-bottom:40px">SOURCES</div>${rows}
    <div class="m" style="position:absolute;left:70px;bottom:40px;right:70px;font-size:16px;line-height:1.6;white-space:normal;color:rgba(26,26,58,.6)">${ep.credits||''}</div></div>`);
  TL.fromTo(c,{yPercent:110,rotation:4},{yPercent:0,rotation:0,duration:.6,ease:'back.out(1.5)',immediateRender:false},t0);TL.set(c,{yPercent:110},0);
  [...c.children].forEach((e,i)=>TL.from(e,{autoAlpha:0,x:-30,duration:.3,ease:'outExpo'},t0+.35+i*.08));
  TL.fromTo(c,{scale:1},{scale:1.025,duration:t1-t0,ease:'none',immediateRender:false},t0+.6);  // slow push: no frozen frame
  cue(t0,'whoosh','end card');
}
