const $ = id => document.getElementById(id);
const node = (tag,text,cls) => {
  const element = document.createElement(tag);
  if (text != null) element.textContent = text;
  if (cls) element.className = cls;
  return element;
};
let saved = [], portal = {rows:[]};
const selections = {};
const filters = {source:"All sources",state:"All states",org:"All organizations",category:"All categories",decision:"All decisions"};
const all = () => [...portal.rows,...saved,...examples];
function metric(label,value) {
  const box = node("div",null,"metric");
  box.append(node("b",value),document.createTextNode(" "+label));
  return box;
}
function drawFilters(rows) {
  $("filters").replaceChildren();
  for (const [key,label] of Object.entries(filters)) {
    const select = node("select");
    select.setAttribute("aria-label",label);
    select.add(new Option(label,""));
    for (const value of [...new Set(rows.map(row=>row[key]).filter(Boolean))].sort()) select.add(new Option(value,value));
    select.value = selections[key] || "";
    select.onchange = () => {selections[key]=select.value;render();};
    $("filters").append(select);
  }
}
function openDetail(r) {
  const detail = $("detail");
  const back=node("button","← All tenders");
  back.onclick=()=>{location.hash="";};
  detail.replaceChildren(back,node("h1",r.title),node("p",[r.org,r.state].filter(Boolean).join(" · ")));
  const metrics=node("div",null,"metrics");
  for (const [key,value] of Object.entries({Budget:r.budget,Deadline:r.deadline,Score:r.score,Source:r.source})) metrics.append(metric(key,value??"—"));
  detail.append(metrics);
  const panel=node("section",null,"panel");
  panel.append(node("h2","Tender overview"),node("p","Reference: "+(r.ref||r.id)),node("p","Category: "+r.category));
  if(r.description) panel.append(node("p",r.description));
  panel.append(node("p",r.explanation));
  if(r.url) {
    const link=node("a","Open official tender ↗");link.href=r.url;link.target="_blank";link.rel="noopener";panel.append(link);
  }
  detail.append(panel);
  const similar=all().filter(x=>x.category===r.category && x.id!==r.id).slice(0,4);
  if(similar.length){
    detail.append(node("h2","More in "+r.category));
    for(const x of similar){const b=node("button",x.title);b.onclick=()=>location.hash=encodeURIComponent(x.id);detail.append(b);}
  }
}
function render() {
  const rows=all(), selected=rows.find(r=>encodeURIComponent(r.id)===location.hash.slice(1));
  $("listing").hidden=!!selected;$("detail").hidden=!selected;
  if(selected){openDetail(selected);return;}
  $("stats").replaceChildren(metric("total",rows.length),metric("CPPP",portal.rows.length),metric("saved",saved.length),metric("examples",examples.length));
  drawFilters(rows);
  const query=$("search").value.trim().toLowerCase();
  const visible=rows.filter(r=>Object.keys(filters).every(k=>!selections[k]||r[k]===selections[k])&&
    [r.title,r.ref,r.org,r.state,r.category,r.description].filter(Boolean).join(" ").toLowerCase().includes(query));
  $("shown").textContent=visible.length+" tenders shown";
  $("cards").replaceChildren();
  for(const r of visible){
    const card=node("button",null,"card"),body=node("div");
    body.append(node("small",(r.ref||r.id)+" · "+r.source),node("h2",r.title),node("p",r.org||r.category));
    if(r.deadline||r.decision)body.append(node("small",[r.decision,r.deadline].filter(Boolean).join(" · ")));
    card.append(node("div",r.score,"ring"),body);
    card.onclick=()=>location.hash=encodeURIComponent(r.id);$("cards").append(card);
  }
  if(!visible.length)$("cards").append(node("p","No matching tenders. Change the search or filters."));
}
async function get(path,method="GET"){
  const res=await fetch(path,{method});
  if(!res.ok)throw Error("Request failed");
  return res.json();
}
async function load(){
  const [history,cache]=await Promise.allSettled([get("/api/tenders"),get("/api/portal")]);
  if(history.status==="fulfilled")saved=history.value.map(r=>({...r,id:"saved-"+r.id,source:"Saved screening"}));
  if(cache.status==="fulfilled")portal=cache.value;
  $("message").textContent=history.status==="rejected"||cache.status==="rejected"?"Some records could not be loaded. Reload to retry.":portal.updated?"CPPP last refreshed "+new Date(portal.updated).toLocaleString():"Refresh CPPP to fetch the latest public listing.";
  render();
}
$("refresh").onclick=async()=>{
  $("refresh").disabled=true;$("message").textContent="Reading CPPP latest tenders…";
  try{portal=await get("/api/portal/refresh","POST");$("message").textContent="CPPP refreshed "+new Date(portal.updated).toLocaleString();render();}
  catch{$("message").textContent="CPPP is unavailable or its listing format changed. Showing the last available records.";}
  finally{$("refresh").disabled=false;}
};
$("search").oninput=()=>{if(location.hash)location.hash="";render();};
window.addEventListener("hashchange",render);
render();load();
