const el = id => document.getElementById(id);
const samples = [
  "Construction of Boundary Wall and Gate",
  "Construction of Two class rooms for School",
  "Annual Maintenance and Catering Services"
];
async function request(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Please check the input length and file format.");
  return data;
}
function display(row) {
  el("decision").textContent = row.decision + " · " + row.score + "/100";
  el("category").textContent = row.title + " | " + row.category + " | " + row.priority;
  el("reason").textContent = row.explanation;
}
let historyVersion = 0;
async function refresh() {
  const version = ++historyVersion;
  const rows = await request("/api/tenders?decision=" + encodeURIComponent(el("filter").value));
  if (version !== historyVersion) return;
  el("records").replaceChildren();
  if (!rows.length) el("records").textContent = "No saved screenings for this selection.";
  for (const row of rows) {
    const button = document.createElement("button");
    button.className = "record";
    button.textContent = row.title + " · " + row.decision + " · " + row.score + "/100";
    button.onclick = () => display(row);
    el("records").append(button);
  }
}
function showError(error) { el("notice").textContent = error.message; }
el("example").onchange = event => {
  if (!event.target.value) return;
  el("title").value = event.target.value;
  el("scope").value = samples[event.target.selectedIndex - 1];
};
el("file").onchange = async event => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.size > 5000000) return showError(new Error("Choose a PDF under 5 MB."));
  const form = new FormData();
  form.append("file", file);
  el("submit").disabled = true;
  try {
    const result = await request("/api/extract", {method:"POST",body:form});
    el("title").value = file.name.replace(/\.pdf$/i,"").slice(0,180);
    el("scope").value = result.text;
    el("notice").textContent = "Review the extracted text and keep the relevant scope before screening.";
  } catch (error) { showError(error); }
  finally { el("submit").disabled = false; }
};
el("screen").onsubmit = async event => {
  event.preventDefault();
  el("submit").disabled = true;
  try {
    const row = await request("/api/tenders", {method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({title:el("title").value,description:el("scope").value})});
    display(row);
    el("notice").textContent = "Screening saved.";
    await refresh();
  } catch (error) { showError(error); }
  finally { el("submit").disabled = false; }
};
el("filter").onchange = () => refresh().catch(showError);
refresh().catch(showError);
