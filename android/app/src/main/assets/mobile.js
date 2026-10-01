const $=id=>document.getElementById(id);
const state={project:null,assets:{characters:[],backgrounds:[],styles:[],voiceovers:[]},playing:false,raf:0,audioCtx:null,analyser:null,source:null,recordDest:null,images:{characters:[],backgrounds:[]},approved:false,rendering:false};
const toast=m=>{const t=$("toast");t.textContent=m;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2200)};

const DB_NAME="UnitedRoadStudioMobile",DB_VERSION=1;
let db=null;
function openDb(){
  return new Promise((resolve,reject)=>{
    const req=indexedDB.open(DB_NAME,DB_VERSION);
    req.onupgradeneeded=()=>{const d=req.result;if(!d.objectStoreNames.contains("kv"))d.createObjectStore("kv")};
    req.onsuccess=()=>{db=req.result;resolve(db)};
    req.onerror=()=>reject(req.error);
  });
}
function put(key,value){return new Promise((resolve,reject)=>{const tx=db.transaction("kv","readwrite");tx.objectStore("kv").put(value,key);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)})}
function get(key){return new Promise((resolve,reject)=>{const tx=db.transaction("kv","readonly");const r=tx.objectStore("kv").get(key);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)})}

function fileMeta(file){return {name:file.name,type:file.type,size:file.size,lastModified:file.lastModified,blob:file}}
function assetLabel(file){const kb=Math.max(1,Math.round(file.size/1024));return `<span class="chip">${file.name} · ${kb} KB</span>`}
function refreshLists(){
  $("characterList").innerHTML=state.assets.characters.map(assetLabel).join("");
  $("backgroundList").innerHTML=state.assets.backgrounds.map(assetLabel).join("");
  $("styleList").innerHTML=state.assets.styles.map(assetLabel).join("");
  $("voiceList").innerHTML=state.assets.voiceovers.map(assetLabel).join("");
}
function projectFromForm(){
  return {title:$("title").value.trim()||"Untitled Episode",directorNotes:$("directorNotes").value,productionNotes:$("productionNotes").value,approved:state.approved,updatedAt:new Date().toISOString()}
}
async function saveProject(silent=false){
  state.project=projectFromForm();
  await put("project",state.project);
  $("status").textContent=state.approved?"APPROVED":"DRAFT";
  if(!silent)toast("Project saved on phone");
}
async function saveAssets(){
  const map=[["characters","characters"],["backgrounds","backgrounds"],["styles","styles"],["voiceovers","voiceovers"]];
  for(const [inputId,key] of map){
    const files=[...$(inputId).files];
    if(files.length)state.assets[key]=files;
  }
  const serial={};
  for(const [key,files] of Object.entries(state.assets))serial[key]=files.map(fileMeta);
  await put("assets",serial);
  state.approved=false;await saveProject(true);
  refreshLists();toast("Assets stored on this phone");
}
async function restore(){
  const p=await get("project");
  if(p){state.project=p;state.approved=!!p.approved;$("title").value=p.title||"";$("directorNotes").value=p.directorNotes||"";$("productionNotes").value=p.productionNotes||""}
  const a=await get("assets");
  if(a){
    for(const key of Object.keys(state.assets))state.assets[key]=(a[key]||[]).map(x=>new File([x.blob],x.name,{type:x.type,lastModified:x.lastModified}));
  }
  $("status").textContent=state.approved?"APPROVED":"DRAFT";
  $("renderMaster").disabled=!state.approved;
  refreshLists();
}
async function loadImage(file){
  const url=URL.createObjectURL(file);
  try{return await new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=url})}
  finally{setTimeout(()=>URL.revokeObjectURL(url),1000)}
}
async function prepareImages(){
  state.images.characters=[];
  state.images.backgrounds=[];
  for(const f of state.assets.characters)state.images.characters.push(await loadImage(f));
  for(const f of state.assets.backgrounds)state.images.backgrounds.push(await loadImage(f));
}
function cover(ctx,img,w,h){
  const s=Math.max(w/img.width,h/img.height),dw=img.width*s,dh=img.height*s;
  ctx.drawImage(img,(w-dw)/2,(h-dh)/2,dw,dh);
}
function contain(ctx,img,w,h,scale=0.82,bob=0){
  const targetH=h*scale,s=targetH/img.height,dw=img.width*s,dh=img.height*s;
  ctx.drawImage(img,(w-dw)/2,h-dh-8+bob,dw,dh);
}
async function buildPreview(){
  if(!state.assets.characters.length){toast("Upload at least one character image");return}
  if(!state.assets.voiceovers.length){toast("Upload at least one voiceover");return}
  await prepareImages();
  const audioFile=state.assets.voiceovers[0];
  $("audio").src=URL.createObjectURL(audioFile);
  $("previewInfo").textContent=`${state.images.characters.length} character asset(s), ${state.images.backgrounds.length} background(s), voiceover: ${audioFile.name}`;
  drawFrame(0,0);
  toast("Preview ready on this phone");
}
function drawFrame(t,energy){
  const c=$("stage"),ctx=c.getContext("2d"),w=c.width,h=c.height;
  ctx.clearRect(0,0,w,h);
  if(state.images.backgrounds.length){
    const bg=state.images.backgrounds[Math.floor(t/5)%state.images.backgrounds.length];cover(ctx,bg,w,h);
  }else{
    const g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,"#20242d");g.addColorStop(1,"#0d0f13");ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
  }
  if(state.images.characters.length){
    const pose=Math.floor(t/2.1)%state.images.characters.length,img=state.images.characters[pose];
    const bob=Math.sin(t*7)*2-energy*10;
    contain(ctx,img,w,h,0.78+energy*0.025,bob);
  }
}
function setupAudioGraph(){
  if(state.audioCtx)return;
  state.audioCtx=new (window.AudioContext||window.webkitAudioContext)();
  state.analyser=state.audioCtx.createAnalyser();state.analyser.fftSize=512;
  state.recordDest=state.audioCtx.createMediaStreamDestination();
  state.source=state.audioCtx.createMediaElementSource($("audio"));
  state.source.connect(state.analyser);
  state.analyser.connect(state.audioCtx.destination);
  state.source.connect(state.recordDest);
}
async function playPreview(){
  if(!$("audio").src){await buildPreview();if(!$("audio").src)return}
  setupAudioGraph();await state.audioCtx.resume();state.playing=true;await $("audio").play();
  const data=new Uint8Array(state.analyser.frequencyBinCount);
  const tick=()=>{
    if(!state.playing)return;
    state.analyser.getByteFrequencyData(data);
    let sum=0;for(const x of data)sum+=x;const energy=Math.min(1,(sum/data.length)/90);
    drawFrame($("audio").currentTime||0,energy);
    state.raf=requestAnimationFrame(tick);
  };tick();
}
function stopPreview(){state.playing=false;cancelAnimationFrame(state.raf);$("audio").pause();$("audio").currentTime=0;drawFrame(0,0)}
async function runReview(){
  const findings=[];
  if(!state.assets.characters.length)findings.push({severity:"block",message:"No character artwork uploaded."});
  if(!state.assets.voiceovers.length)findings.push({severity:"block",message:"No voiceover uploaded."});
  if(!state.assets.backgrounds.length)findings.push({severity:"warn",message:"No background uploaded; Studio will use a neutral stage."});
  if(state.assets.characters.some(f=>f.size<20_000))findings.push({severity:"warn",message:"One or more character images are very small and may look soft in HD."});
  if(!$("directorNotes").value.trim())findings.push({severity:"warn",message:"Director notes are empty."});
  const passed=!findings.some(f=>f.severity==="block");
  const box=$("qa");box.className="qa "+(passed?"pass":"fail");
  box.innerHTML=`<h3>${passed?"✓ Core review passed":"✕ Fixes required"}</h3>`+(findings.length?findings.map(f=>`<div class="finding ${f.severity}">${f.message}</div>`).join(""):"<p>No blocking problems found in the current on-device project.</p>");
  $("approve").disabled=!passed;
  toast(passed?"Review passed":"Review found blocking issues");
}
async function approve(){state.approved=true;await saveProject(true);$("status").textContent="APPROVED";$("renderMaster").disabled=false;toast("Episode approved")}


function chooseRecorderMime(){
  const types=[
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm"
  ];
  return types.find(t=>window.MediaRecorder&&MediaRecorder.isTypeSupported(t))||"";
}
function bytesToBase64(buffer){
  const bytes=new Uint8Array(buffer);let binary="";const step=0x8000;
  for(let i=0;i<bytes.length;i+=step)binary+=String.fromCharCode(...bytes.subarray(i,i+step));
  return btoa(binary);
}
function safeTitle(){return (($("title").value||"United-Road-Episode").trim().replace(/[^A-Za-z0-9._-]+/g,"-").replace(/^-+|-+$/g,""))||"United-Road-Episode"}
async function renderVideo(width,height,fps,kind){
  if(state.rendering){toast("A render is already running");return}
  if(!state.assets.characters.length||!state.assets.voiceovers.length){toast("Character artwork and a voiceover are required");return}
  if(!window.MediaRecorder||!$("stage").captureStream){toast("This Android WebView does not support on-device recording yet");return}
  if(!window.UnitedRoadAndroid?.beginExport){toast("Android export bridge is unavailable");return}

  state.rendering=true;
  const box=$("renderProgress"),p=box.querySelector("p");
  p.textContent="Preparing "+kind+"…";
  try{
    await buildPreview();setupAudioGraph();await state.audioCtx.resume();
    const canvas=$("stage"),oldW=canvas.width,oldH=canvas.height;
    canvas.width=width;canvas.height=height;drawFrame(0,0);
    const mime=chooseRecorderMime();
    const canvasStream=canvas.captureStream(fps);
    const combined=new MediaStream();
    canvasStream.getVideoTracks().forEach(t=>combined.addTrack(t));
    state.recordDest.stream.getAudioTracks().forEach(t=>combined.addTrack(t));
    const recorder=new MediaRecorder(combined,mime?{mimeType:mime,videoBitsPerSecond:kind==="4K master"?28000000:8000000}:undefined);
    const fileName=safeTitle()+(kind==="4K master"?"-4K-master.webm":"-720p-review.webm");
    if(!window.UnitedRoadAndroid.beginExport(fileName,mime||"video/webm"))throw new Error("Android could not open the export file");

    let writeChain=Promise.resolve();
    recorder.ondataavailable=e=>{
      if(!e.data||!e.data.size)return;
      writeChain=writeChain.then(async()=>{
        const b64=bytesToBase64(await e.data.arrayBuffer());
        if(!window.UnitedRoadAndroid.appendExport(b64))throw new Error("Could not write video chunk");
      });
    };

    const audio=$("audio");audio.pause();audio.currentTime=0;
    let ended=false;
    const stopWhenEnded=()=>{ended=true};audio.addEventListener("ended",stopWhenEnded,{once:true});
    recorder.start(1000);
    await audio.play();
    const data=new Uint8Array(state.analyser.frequencyBinCount);
    const started=performance.now();
    await new Promise((resolve,reject)=>{
      const tick=()=>{
        if(ended){resolve();return}
        state.analyser.getByteFrequencyData(data);let sum=0;for(const x of data)sum+=x;
        const energy=Math.min(1,(sum/data.length)/90);drawFrame(audio.currentTime||0,energy);
        const duration=Number.isFinite(audio.duration)&&audio.duration>0?audio.duration:1;
        const percent=Math.min(99,Math.round((audio.currentTime/duration)*100));
        p.textContent=kind+" rendering on phone — "+percent+"%";
        state.raf=requestAnimationFrame(tick);
      };tick();
    });
    cancelAnimationFrame(state.raf);audio.pause();
    const stopped=new Promise(resolve=>recorder.addEventListener("stop",resolve,{once:true}));
    recorder.stop();await stopped;await writeChain;
    const location=window.UnitedRoadAndroid.finishExport();
    canvas.width=oldW;canvas.height=oldH;drawFrame(0,0);
    p.textContent=kind+" saved to Downloads/UnitedRoadStudio.";
    toast(kind+" complete");
    return location;
  }catch(e){
    try{window.UnitedRoadAndroid.finishExport()}catch{}
    p.textContent="Render failed: "+e.message;toast("Render failed: "+e.message);
  }finally{state.rendering=false}
}

document.querySelectorAll(".tab").forEach(b=>b.onclick=()=>{document.querySelectorAll(".tab").forEach(x=>x.classList.toggle("active",x===b));document.querySelectorAll(".panel").forEach(x=>x.classList.toggle("active",x.id===b.dataset.panel))});
$("saveProject").onclick=()=>saveProject(false);
$("saveAssets").onclick=saveAssets;
$("buildPreview").onclick=buildPreview;
$("playPreview").onclick=playPreview;
$("stopPreview").onclick=stopPreview;
$("runReview").onclick=runReview;
$("approve").onclick=approve;
$("exportPreview").onclick=()=>renderVideo(1280,720,30,"720p review");
$("renderMaster").onclick=()=>{if(!state.approved){toast("Approve the episode first");return}renderVideo(3840,2160,60,"4K master")};
let timer=null;["title","directorNotes","productionNotes"].forEach(id=>$(id).addEventListener("input",()=>{state.approved=false;$("status").textContent="DRAFT";clearTimeout(timer);timer=setTimeout(()=>saveProject(true).catch(()=>{}),800)}));

(async()=>{await openDb();await restore();drawFrame(0,0)})().catch(e=>toast("Startup error: "+e.message));