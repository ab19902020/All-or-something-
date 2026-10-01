const state={project:null,projects:[],activeJob:null,installPrompt:null,engineBase:""};
const $=id=>document.getElementById(id);
const isFileMode=location.protocol==="file:";
const isAndroidShell=new URLSearchParams(location.search).get("android")==="1";
const cleanBase=v=>(v||"").trim().replace(/\/$/,"");
state.engineBase=isFileMode?cleanBase(localStorage.getItem("urs_engine_url")||""):"";

const endpoint=path=>{
  if(/^https?:\/\//i.test(path))return path;
  return (state.engineBase||"")+path;
};
const mediaUrl=path=>endpoint(path);
const api=async(url,opts={})=>{
  const r=await fetch(endpoint(url),opts);
  let d=null;
  try{d=await r.json()}catch{}
  if(!r.ok)throw new Error(d?.detail||d?.error||r.statusText||"Request failed");
  return d;
};
const toast=m=>{
  const t=$("toast");if(!t)return;
  t.textContent=m;t.classList.add("show");
  setTimeout(()=>t.classList.remove("show"),2400);
};
const esc=s=>(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function showEngineOverlay(message=""){
  $("engineOverlay").classList.remove("hidden");
  $("engineUrlInput").value=state.engineBase||localStorage.getItem("urs_engine_url")||"";
  $("engineError").textContent=message;
}
function hideEngineOverlay(){$("engineOverlay").classList.add("hidden")}
function setEngineConnected(ok){
  $("engineDot").classList.toggle("on",!!ok);
  $("engineAddress").textContent=ok?(state.engineBase||location.origin):"Engine disconnected";
  $("changeEngineBtn").classList.toggle("hidden",!(isFileMode||isAndroidShell));
}
async function connectEngine(){
  let url=cleanBase($("engineUrlInput").value);
  if(!url){$("engineError").textContent="Enter the engine address shown on the computer running Studio.";return}
  if(!/^https?:\/\//i.test(url))url="http://"+url;
  $("engineError").textContent="Connecting…";
  try{
    const r=await fetch(url+"/api/health",{cache:"no-store"});
    if(!r.ok)throw new Error("Engine replied with "+r.status);
    const d=await r.json();
    if(!d.ok)throw new Error("This address is not a United Road Studio engine.");
    state.engineBase=url;
    localStorage.setItem("urs_engine_url",url);
    hideEngineOverlay();setEngineConnected(true);
    await bootWorkspace();
    toast("Phone connected to Studio Engine");
  }catch(e){
    $("engineError").textContent="Could not connect: "+e.message;
    setEngineConnected(false);
  }
}

async function testCurrentEngine(){
  try{
    const h=await api("/api/health",{cache:"no-store"});
    if(!h.ok)throw new Error("Engine unavailable");
    setEngineConnected(true);return true;
  }catch(e){
    setEngineConnected(false);
    showEngineOverlay(isFileMode?"The interface loaded, but it needs the Studio Engine address.":"Studio Engine is not responding. Start the engine, then retry.");
    return false;
  }
}

async function loadProjects(){
  state.projects=await api("/api/projects");
  $("projectList").innerHTML=state.projects.map(p=>`<button class="project-item ${state.project?.id===p.id?"active":""}" data-id="${p.id}"><strong>${esc(p.title)}</strong><small>${esc(p.status)}</small></button>`).join("")||'<div class="asset-chip">No episodes yet</div>';
  document.querySelectorAll(".project-item").forEach(b=>b.onclick=()=>openProject(b.dataset.id));
}

async function openProject(id){
  state.project=await api("/api/projects/"+id);
  $("emptyState").classList.add("hidden");$("workspace").classList.remove("hidden");
  $("projectTitle").textContent=state.project.title;
  $("statusPill").textContent=state.project.status.toUpperCase();
  $("saveNotesBtn").disabled=false;
  $("directorNotes").value=state.project.director_notes||"";
  $("productionNotes").value=state.project.production_notes||"";
  fillAssets();fillPlan();fillQA();fillSettings();refreshPreview();refreshServices();
  await loadProjects();
}

function fillAssets(){
  if(!state.project)return;
  const p=state.project;
  const lists={character:p.character_assets,background:p.background_assets,style:p.style_references,voiceover:p.voiceovers};
  Object.entries(lists).forEach(([k,arr])=>{
    $(k+"List").innerHTML=(arr||[]).map(x=>`<div class="asset-chip" title="${esc(x)}">${esc(x.split("/").pop())}</div>`).join("")||'<div class="asset-chip">None uploaded</div>';
  });
}
function fillPlan(){
  $("planOutput").textContent=state.project?.plan?JSON.stringify(state.project.plan,null,2):"No direction plan built yet.";
}
function fillQA(){
  if(!state.project)return;
  const q=state.project.qa,box=$("qaBox");
  box.className="qa-box";
  if(!q){
    box.innerHTML="<p>No QA report yet.</p>";
    $("approveBtn").disabled=true;$("masterBtn").disabled=true;return;
  }
  box.classList.add(q.passed?"qa-pass":"qa-fail");
  box.innerHTML=`<h3>${q.passed?"✓ Self-review passed":"✕ Fixes required"}</h3><p>${esc(q.summary||"")}</p><p class="asset-chip">Local vision review: ${q.vision_review_used?"used":"not available — deterministic checks still ran"}</p>`+
    (q.findings||[]).map(f=>`<div class="finding ${f.severity||"warn"}"><strong>${esc((f.category||"issue").toUpperCase())}</strong> — ${esc(f.message||"")}</div>`).join("");
  $("approveBtn").disabled=!q.passed;
  $("masterBtn").disabled=state.project.status!=="approved";
}
function fillSettings(){
  if(!state.project)return;
  const s=state.project.settings||{};
  $("ollamaUrl").value=s.ollama_url||"http://127.0.0.1:11434";
  $("directorModel").value=s.director_model||"qwen2.5:7b";
  $("visionModel").value=s.vision_model||"qwen2.5vl:7b";
  $("whisperModel").value=s.whisper_model||"small.en";
  $("comfyUrl").value=s.comfyui_url||"http://127.0.0.1:8188";
  $("comfyCheckpoint").value=s.comfy_checkpoint||"";
  $("rendererMode").value=s.renderer||"auto";
  $("legacyRoot").value=s.legacy_root||"";
  $("legacyScene").value=s.legacy_scene||"";
}
async function refreshServices(){
  if(!state.project)return;
  try{
    const s=await api(`/api/projects/${state.project.id}/services`);
    $("ollamaDot").classList.toggle("on",!!s.ollama);
    $("comfyDot").classList.toggle("on",!!s.comfyui);
  }catch{}
}
function refreshPreview(){
  if(!state.project)return;
  const v=$("previewVideo"),miss=$("previewMissing");
  if(state.project.has_preview){
    v.src=mediaUrl(`/api/projects/${state.project.id}/media/renders/preview.mp4?t=${Date.now()}`);
    miss.classList.add("hidden");
  }else{
    v.removeAttribute("src");v.load();miss.classList.remove("hidden");
  }
  const link=$("masterLink");
  if(state.project.has_master){
    link.href=mediaUrl(`/api/projects/${state.project.id}/media/renders/master_4k.mp4`);
    link.classList.remove("hidden");
  }else link.classList.add("hidden");
}

async function newProject(){
  const title=prompt("Episode title");if(!title)return;
  const p=await api("/api/projects",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title})});
  await openProject(p.id);toast("Episode created");
}
async function saveNotes(silent=false){
  if(!state.project)return;
  state.project=await api(`/api/projects/${state.project.id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({director_notes:$("directorNotes").value,production_notes:$("productionNotes").value})});
  $("statusPill").textContent=state.project.status.toUpperCase();
  if(!silent)toast("Notes saved");
}

function showJob(job,title){
  $("jobBox").classList.remove("hidden");
  $("jobTitle").textContent=title||job.kind;
  $("jobPercent").textContent=Math.round((job.progress||0)*100)+"%";
  $("jobProgress").style.width=Math.round((job.progress||0)*100)+"%";
  $("jobMessage").textContent=job.message||"";
}
async function waitJob(jobId,title){
  state.activeJob=jobId;
  while(true){
    const j=await api("/api/jobs/"+jobId);showJob(j,title);
    if(j.status==="done"){
      state.activeJob=null;
      state.project=await api(`/api/projects/${state.project.id}`);
      $("statusPill").textContent=state.project.status.toUpperCase();
      fillPlan();fillQA();refreshPreview();toast(title+" complete");
      return j.result;
    }
    if(j.status==="failed"){state.activeJob=null;throw new Error(j.error||j.message||"Job failed")}
    await new Promise(r=>setTimeout(r,1000));
  }
}
async function runJob(url,title){
  try{
    const r=await api(url,{method:"POST"});
    return await waitJob(r.job_id,title);
  }catch(e){toast(e.message);throw e}
}

function activatePanel(target){
  document.querySelectorAll(".step").forEach(x=>x.classList.toggle("active",x.dataset.target===target));
  document.querySelectorAll(".panel").forEach(x=>x.classList.remove("active-panel"));
  const p=$(target);if(p)p.classList.add("active-panel");
  if(window.innerWidth<981)window.scrollTo({top:0,behavior:"smooth"});
}

function bindUI(){
  $("newProjectBtn").onclick=newProject;$("emptyNewBtn").onclick=newProject;
  $("saveNotesBtn").onclick=()=>saveNotes(false);
  $("connectEngineBtn").onclick=connectEngine;
  $("retryEngineBtn").onclick=()=>state.engineBase?testCurrentEngine().then(ok=>ok&&bootWorkspace()):connectEngine();
  $("changeEngineBtn").onclick=()=>{
    if(isAndroidShell && window.UnitedRoadAndroid?.changeEngine){window.UnitedRoadAndroid.changeEngine();return}
    showEngineOverlay("");
  };

  let noteTimer=null;
  ["directorNotes","productionNotes"].forEach(id=>{
    $(id).addEventListener("input",()=>{
      clearTimeout(noteTimer);
      noteTimer=setTimeout(()=>saveNotes(true).catch(()=>{}),1000);
    });
  });

  document.querySelectorAll(".uploadBtn").forEach(btn=>btn.onclick=async()=>{
    if(!state.project)return;
    const kind=btn.dataset.upload,input=$(kind+"Files"),files=[...input.files];
    if(!files.length){toast("Choose files first");return}
    const fd=new FormData();files.forEach(f=>fd.append("files",f));
    btn.disabled=true;
    try{
      const r=await api(`/api/projects/${state.project.id}/upload/${kind}`,{method:"POST",body:fd});
      state.project=r.project;fillAssets();fillQA();toast(files.length+" file(s) uploaded");
    }catch(e){toast(e.message)}finally{btn.disabled=false}
  });

  $("transcribeBtn").onclick=async()=>{const r=await runJob(`/api/projects/${state.project.id}/transcribe`,"Voice analysis");$("transcriptOutput").textContent=JSON.stringify(r,null,2)};
  $("planBtn").onclick=async()=>{await saveNotes(true);const r=await runJob(`/api/projects/${state.project.id}/plan`,"Direction plan");$("planOutput").textContent=JSON.stringify(r,null,2)};
  $("renderBtn").onclick=async()=>{await saveNotes(true);const profile=document.querySelector('input[name="previewProfile"]:checked').value;await runJob(`/api/projects/${state.project.id}/render/${profile}`,"Preview render");activatePanel("review")};
  $("reviewBtn").onclick=async()=>{await runJob(`/api/projects/${state.project.id}/review`,"Self-review")};
  $("refreshPreviewBtn").onclick=async()=>{state.project=await api(`/api/projects/${state.project.id}`);refreshPreview()};
  $("approveBtn").onclick=async()=>{
    try{
      state.project=await api(`/api/projects/${state.project.id}/approve`,{method:"POST"});
      $("statusPill").textContent="APPROVED";$("masterBtn").disabled=false;toast("Final master approved");
    }catch(e){toast(e.message)}
  };
  $("masterBtn").onclick=async()=>{
    if(!confirm("Render the final 4K master now?"))return;
    await runJob(`/api/projects/${state.project.id}/render/final_master_4k`,"4K master render");
  };
  $("saveSettingsBtn").onclick=async()=>{
    const body={ollama_url:$("ollamaUrl").value,director_model:$("directorModel").value,vision_model:$("visionModel").value,whisper_model:$("whisperModel").value,comfyui_url:$("comfyUrl").value,comfy_checkpoint:$("comfyCheckpoint").value,renderer:$("rendererMode").value,legacy_root:$("legacyRoot").value,legacy_scene:$("legacyScene").value};
    state.project.settings=await api(`/api/projects/${state.project.id}/settings`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    refreshServices();fillQA();toast("Settings saved");
  };
  $("generateImageBtn").onclick=async()=>{
    const prompt=$("imagePrompt").value.trim();if(!prompt){toast("Write an image prompt first");return}
    try{
      const r=await api(`/api/projects/${state.project.id}/generate-image`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt,style_description:$("styleDescription").value})});
      const out=await waitJob(r.job_id,"Local image generation");
      $("generatedImage").innerHTML=`<img class="generated-preview" src="${mediaUrl(`/api/projects/${state.project.id}/media/${out.media}?t=${Date.now()}`)}">`;
    }catch(e){toast(e.message)}
  };

  document.querySelectorAll(".step").forEach(b=>b.onclick=()=>activatePanel(b.dataset.target));

  window.addEventListener("beforeinstallprompt",e=>{
    e.preventDefault();state.installPrompt=e;$("installBtn").classList.remove("hidden");
  });
  $("installBtn").onclick=async()=>{
    if(!state.installPrompt)return;
    state.installPrompt.prompt();await state.installPrompt.userChoice;state.installPrompt=null;$("installBtn").classList.add("hidden");
  };
}

async function bootWorkspace(){
  await loadProjects();
  if(state.projects.length)await openProject(state.projects[0].id);
}

async function init(){
  bindUI();
  if("serviceWorker" in navigator && location.protocol.startsWith("http")){
    navigator.serviceWorker.register("./sw.js").catch(()=>{});
  }
  if(isFileMode && !state.engineBase){
    showEngineOverlay("This file is only the mobile interface. Connect it to the Studio Engine to make the buttons work.");
    return;
  }
  const ok=await testCurrentEngine();
  if(ok){hideEngineOverlay();await bootWorkspace()}
}

init().catch(e=>{console.error(e);showEngineOverlay(e.message)});
