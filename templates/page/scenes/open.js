// Show open: a fast montage of the episode's key images/words, then the sonic-logo title card
// ("DAILY RESEARCH REPORT" assembling in voxels). Window: marks.montage -> marks.logo (set by build_vo.py from the gap you leave
// after the cold open). The host's "this is your daily research report" line plays right after this.
import {TL,TM,gsap,Vox,textPts,boxPts,cam,whip,layer,H,typeIn,zoomPunch,flashAt,cue,E,INK,BL,CO,YE} from '../engine.js';
import {accent} from './_util.js';
export function textures(ep){return (ep.open&&ep.open.images)||[];}
export function build(ep){
  const m0=TM.marks.montage, m1=TM.marks.logo, o=ep.open||{}, words=o.montage||['ONE STUDY','THE CLAIM','THE CHECK'], XO=-9000;
  if(!(m1>m0))return;
  const lm=Math.min(m1-m0-1.6, words.length*.45);            // montage, then >= 1.6 s of logo
  const step=lm/words.length;
  const L0=layer(m0,m1+.4);
  whip(m0-.25,.45,{x:XO,y:6,z:26,tx:XO,ty:4,tz:0,fov:34,roll:0},[1,0]);
  words.forEach((s,i)=>{const t=m0+i*step;
    const e=H(L0,`<div class="a h" style="left:0;right:0;top:390px;text-align:center;font-size:${150-6*Math.min(i,8)}px">${accent(s,i%2?'r':'b')}</div>`);
    TL.set(e,{autoAlpha:0},0);TL.set(e,{autoAlpha:1},t);TL.set(e,{autoAlpha:0},t+step);
    TL.fromTo(e,{scale:1.25},{scale:1,duration:step,ease:'outQuint',immediateRender:false},t);
    cue(t,i%3===2?'glitch':'cut','montage '+i);zoomPunch(t,.08,.25);});
  const t1=m0+lm;                                            // logo hit
  const title=(o.title||'DAILY RESEARCH REPORT').toUpperCase();
  const v=new Vox(9000,[t1-.6,m1+.4]);
  v.assemble(t1-.55,.8,textPts(title,{cell:.32,rows:15,depth:2,color:INK,x:XO,y:2.4}),{r:24,stag:.45,seed:3,ease:E('outQuint')});
  cam(t1-.6,m1-t1+.6,{x:XO,y:5,z:21,tx:XO,ty:4.6},'outQuint');
  const sub=H(L0,`<div class="a m" style="left:0;right:0;top:800px;text-align:center;font-size:34px;color:${BL}">${o.tagline||'ONE STUDY · CHECKED'}</div>`);
  TL.set(sub,{autoAlpha:0},0);TL.fromTo(sub,{autoAlpha:0,y:20},{autoAlpha:1,y:0,duration:.35,ease:'outExpo',immediateRender:false},t1+.25);
  flashAt(t1,.6,.3);cue(t1,'logohit','logo');
  v.dissolve(m1-.35,.5,{stag:.5});TL.to(sub,{autoAlpha:0,duration:.25},m1-.3);
}
