// Deterministic frame renderer: headless Chromium (Playwright) seeks the page to t = f/FPS, screenshots via CDP, pipes JPEGs to ffmpeg.
// usage: node render.js PAGE_DIR cues OUT.json        -> sound-design cue list (window.CUES)
//        node render.js PAGE_DIR stills t1,t2,.. DIR  -> JPEG stills at those times
//        node render.js PAGE_DIR frames F0 F1 OUT.mp4 -> frames [F0,F1) as x264 crf 17 (bt709, tv range)
// env: SC=open,beats (render only some scenes), FX=ao,dof,bloom (post FX), Q=lite, CHROME_PATH (optional system Chrome)
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');const path=require('path');
const [PAGE,MODE,...A]=process.argv.slice(2);const FPS=30;
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,
  args:['--force-color-profile=srgb','--hide-scrollbars','--disable-gpu','--allow-file-access-from-files','--enable-unsafe-swiftshader','--renderer-process-limit=1','--js-flags=--max-old-space-size=1024']});
const p=await b.newPage({viewport:{width:1920,height:1080}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));p.on('console',m=>{if(m.type()==='error')errs.push(m.text());});
const qs=[process.env.SC?'s='+process.env.SC:'',process.env.FX!==undefined?'fx='+process.env.FX:'',process.env.Q?'q='+process.env.Q:''].filter(Boolean).join('&');
await p.goto('file://'+path.resolve(PAGE,'index.html')+(qs?'?'+qs:''));
await p.waitForFunction('window.READY===true',{timeout:120000}).catch(()=>{console.log('NOT READY',errs);process.exit(2);});
const cdp=await p.context().newCDPSession(p);const shot=async()=>Buffer.from((await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:92})).data,'base64');
if(MODE==='cues'){fs.writeFileSync(A[0],JSON.stringify(await p.evaluate(()=>window.CUES.slice().sort((a,b)=>a[0]-b[0]))));console.log('errs',errs);await b.close();return;}
if(MODE==='stills'){fs.mkdirSync(A[1],{recursive:true});for(const t of A[0].split(',').map(Number)){await p.evaluate(t=>seek(t),t);fs.writeFileSync(`${A[1]}/t${t.toFixed(2).padStart(7,'0')}.jpg`,await shot());}console.log('errs',errs);await b.close();return;}
if(MODE!=='frames'){console.log('mode must be cues|stills|frames');process.exit(1);}
const DUR=await p.evaluate(()=>window.TIMING.dur);const f0=+A[0],f1=Math.min(+A[1],Math.round(DUR*FPS));
const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-vf','scale=out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','17','-threads','2','-r',String(FPS),A[2]]);
for(let f=f0;f<f1;f++){await p.evaluate(t=>seek(t),f/FPS);const buf=await shot();if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
ff.stdin.end();await new Promise(r=>ff.on('close',r));console.log('done',A[2],'errs',errs.length,errs.slice(0,3));await b.close();
if(errs.length)process.exit(3);})();
