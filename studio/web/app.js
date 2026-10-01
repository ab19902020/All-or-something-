const state={project:null,projects:[],activeJob:null};
const $=id=>document.getElementById(id);
const api=async(url,opts={})=>{const r=await fetch(url,opts);let d;try{d=await r.json()}catch{d=null}if(!r.ok)throw new Error(d?.detail||d?.error||r.statusText);return d};
const toast=m=>{const t=$("toast");t.textContent=m;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2400)};
const esc=s=>(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

async function loadProjects(){
  state.projects=await api("/api/projects");
  $("projectList").innerHTML=state.projects.map(p=>`<button class="project-item ${state.project?.id===p.id?"active":""}" data-id="${p.id}"><strong>${esc(p.title)}</strong><small>${p.status}</small></button>`).join("")||'<div class="asset-chip">No episodes yet</div>';
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
  fillAssets();fillPlan();fillQA();fillSettings();refreshPreview();refreshServices();await loadProjects();
}

function fillAssets(){
  const p=state.project;
  const lists={character:p.character_assets,background:p.background_assets,style:p.style_references,voiceover:p.voiceovers};
  Object.entries(lists).forEach(([k,arr])=>{$(k+"List").innerHTML=(arr||[]).map(x=>`<div class="asset-chip" title="${esc(x)}">${esc(x.split("/").pop())}</div>`).join("")||'<div class="asset-chip">None uploaded</div>'});
}

function fillPlan(){
  $("planOutput").textContent=state.project.plan?JSON.stringify(state.project.plan,null,2):"No direction plan built yet.";
}
function fillQA(){
  const q=state.project.qa,box=$("qaBox");
  box.className="qa-box";
  if(!q){box.innerHTML="<p>No QA report yet.</p>";return}
  box.classList.add(q.passed?"qa-pass":"qa-fail");
  box.innerHTML=`<h3>${q.passed?"✓ Self-review passed":"✕ Fixes required"}</h3><p>${esc(q.summary||"")}</p><p class="asset-chip">Local vision review: ${q.vision_review_used?"used":"not available — deterministic checks still ran"}</p>`+
    (q.findings||[]).map(f=>`<div class="finding ${f.severity||"warn"}"><strong>${esc((f.category||"issue").toUpperCase())}</strong> — ${esc(f.message||"")}</div>`).join("");
  $("masterBtn").disabled=state.project.status!=="approved";
  $("approveBtn").disabled=!q.passed;
}
function fillSettings(){
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
  try{const s=await api(`/api/projects/${state.project.id}/services`);
    $("ollamaDot").classList.toggle("on",s.ollama);$("comfyDot").classList.toggle("on",s.comfyui);
  }catch{}
}
function refreshPreview(){
  if(!state.project)return;
  const v=$("previewVideo"),miss=$("previewMissing");
  if(state.project.has_preview){v.src=`/api/projects/${state.project.id}/media/renders/preview.mp4?t=${Date.now()}`;miss.classList.add("hidden")}
  else{v.removeAttribute("src");v.load();miss.classList.remove("hidden")}
  const link=$("masterLink");
  if(state.project.has_master){link.href=`/api/projects/${state.project.id}/media/renders/master_4k.mp4`;link.classList.remove("hidden")}else link.classList.add("hidden");
}

async function newProject(){
  const title=prompt("Episode title");if(!title)return;
  const p=await api("/api/projects",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title})});
  await openProject(p.id);toast("Episode created");
}
$("newProjectBtn").onclick=newProject;$("emptyNewBtn").onclick=newProject;

async function saveNotes(){
  if(!state.project)return;
  state.project=await api(`/api/projects/${state.project.id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({director_notes:$("directorNotes").value,production_notes:$("productionNotes").value})});
  $("statusPill").textContent=state.project.status.toUpperCase();toast("Notes saved");
}
$("saveNotesBtn").onclick=saveNotes;
let noteTimer=null;
["directorNotes","productionNotes"].forEach(id=>{
  $(id).addEventListener("input",()=>{
    clearTimeout(noteTimer);
    noteTimer=setTimeout(()=>saveNotes().catch(()=>{}),900);
  });
});

document.querySelectorAll(".uploadBtn").forEach(btn=>btn.onclick=async()=>{
  if(!state.project)return;
  const kind=btn.dataset.upload,input=$(kind+"Files"),files=[...input.files];if(!files.length){toast("Choose files first");return}
  const fd=new FormData();files.forEach(f=>fd.append("files",f));
  btn.disabled=true;
  try{const r=await api(`/api/projects/${state.project.id}/upload/${kind}`,{method:"POST",body:fd});state.project=r.project;fillAssets();toast(files.length+" file(s) uploaded")}
  catch(e){toast(e.message)}finally{btn.disabled=false}
});

function showJob(job,title){
  $("jobBox").classList.remove("hidden");$("jobTitle").textContent=title||job.kind;$("jobPercent").textContent=Math.round((job.progress||0)*100)+"%";$("jobProgress").style.width=Math.round((job.progress||0)*100)+"%";$("jobMessage").textContent=job.message||"";
}
async function waitJob(jobId,title){
  state.activeJob=jobId;
  while(true){
    const j=await api("/api/jobs/"+jobId);showJob(j,title);
    if(j.status==="done"){state.activeJob=null;state.project=await api(`/api/projects/${state.project.id}`);$("statusPill").textContent=state.project.status.toUpperCase();fillPlan();fillQA();refreshPreview();toast(title+" complete");return j.result}
    if(j.status==="failed"){state.activeJob=null;throw new Error(j.error||j.message||"Job failed")}
    await new Promise(r=>setTimeout(r,1000));
  }
}
async function runJob(url,title){
  try{const r=await api(url,{method:"POST"});return await waitJob(r.job_id,title)}catch(e){toast(e.message);throw e}
}

$("transcribeBtn").onclick=async()=>{const r=await runJob(`/api/projects/${state.project.id}/transcribe`,"Voice analysis");$("transcriptOutput").textContent=JSON.stringify(r,null,2)};
$("planBtn").onclick=async()=>{await saveNotes();const r=await runJob(`/api/projects/${state.project.id}/plan`,"Direction plan");$("planOutput").textContent=JSON.stringify(r,null,2)};
$("renderBtn").onclick=async()=>{await saveNotes();const profile=document.querySelector('input[name="previewProfile"]:checked').value;await runJob(`/api/projects/${state.project.id}/render/${profile}`,"Preview render")};
$("reviewBtn").onclick=async()=>{await runJob(`/api/projects/${state.project.id}/review`,"Self-review")};
$("refreshPreviewBtn").onclick=async()=>{state.project=await api(`/api/projects/${state.project.id}`);refreshPreview()};
$("approveBtn").onclick=async()=>{try{state.project=await api(`/api/projects/${state.project.id}/approve`,{method:"POST"});$("statusPill").textContent="APPROVED";$("masterBtn").disabled=false;toast("Final master approved")}catch(e){toast(e.message)}};
$("masterBtn").onclick=async()=>{if(!confirm("Render the final 4K master now? This is the expensive final-quality render."))return;await runJob(`/api/projects/${state.project.id}/render/final_master_4k`,"4K master render")};

$("saveSettingsBtn").onclick=async()=>{
  const body={ollama_url:$("ollamaUrl").value,director_model:$("directorModel").value,vision_model:$("visionModel").value,whisper_model:$("whisperModel").value,comfyui_url:$("comfyUrl").value,comfy_checkpoint:$("comfyCheckpoint").value,renderer:$("rendererMode").value,legacy_root:$("legacyRoot").value,legacy_scene:$("legacyScene").value};
  state.project.settings=await api(`/api/projects/${state.project.id}/settings`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});refreshServices();toast("Settings saved");
};
$("generateImageBtn").onclick=async()=>{
  const prompt=$("imagePrompt").value.trim();if(!prompt){toast("Write an image prompt first");return}
  try{const r=await api(`/api/projects/${state.project.id}/generate-image`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt,style_description:$("styleDescription").value})});const out=await waitJob(r.job_id,"Local image generation");$("generatedImage").innerHTML=`<img style="max-width:100%;margin-top:14px;border-radius:10px" src="/api/projects/${state.project.id}/media/${out.media}?t=${Date.now()}">`}catch(e){toast(e.message)}
};

document.querySelectorAll(".step").forEach(b=>b.onclick=()=>{
  document.querySelectorAll(".step").forEach(x=>x.classList.remove("active"));b.classList.add("active");
  document.querySelectorAll(".panel").forEach(x=>x.classList.remove("active-panel"));$(b.dataset.target).classList.add("active-panel");
});

(async()=>{await loadProjects();if(state.projects.length)await openProject(state.projects[0].id)})();
