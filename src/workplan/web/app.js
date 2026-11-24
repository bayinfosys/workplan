// workplan serve: the board. Talks to the server's /api; loads nothing else.

"use strict";

const STATES = [
  ["unspecified", "plan"], ["refinement", "plan"],
  ["waiting", "work"], ["stale", "work"], ["development", "work"], ["testing", "work"],
  ["complete", "done"], ["merged", "done"],
  ["dropped", "closed"], ["unknown", "closed"],
];
const PATCHED = ["waiting", "stale", "development", "testing"];
const DOCS = [["Task", "TASK.md"], ["Breakdown", "BREAKDOWN.md"], ["Notes", "NOTES.md"]];
const REFRESH_MS = 5000;

const token = new URLSearchParams(location.search).get("token") || "";
const view = {
  workplans: [],
  selected: null,       // workplan id
  status: null,         // ops.status for the selected workplan
  panel: null,          // {kind: "task", task} or {kind: "plan"}
  tab: "TASK.md",
  editing: false,
  busy: false,
};

const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------------------
// the API

async function api(path, body) {
  const response = await fetch(path, {
    method: body === undefined ? "GET" : "POST",
    headers: {"X-Workplan-Token": token, "Content-Type": "application/json"},
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  let reply = {};
  try { reply = await response.json(); } catch (e) { reply = {error: response.statusText}; }
  if (!response.ok) throw new Error(reply.error || response.statusText);
  return reply.data;
}

function say(text, kind) {
  const line = $("line");
  line.textContent = text || "";
  line.className = "line" + (kind ? " " + kind : "");
}

async function operation(label, body, done) {
  if (view.busy) return;
  view.busy = true;
  say(label + "...", "busy");
  render();
  try {
    const data = await api("/api/run", body);
    say(done(data));
  } catch (e) {
    say(e.message, "error");
  } finally {
    view.busy = false;
    await refresh();
  }
}

// ---------------------------------------------------------------------------
// rendering Markdown and diffs

function esc(text) {
  return text.replace(/[&<>"]/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
}

function inline(text) {
  return text.split(/(`[^`]+`)/).map((part) => {
    if (part.length > 1 && part.startsWith("`") && part.endsWith("`")) {
      return "<code>" + esc(part.slice(1, -1)) + "</code>";
    }
    return esc(part)
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[\s(])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>")
      .replace(/&lt;([^&]*?)&gt;/g, '<span class="placeholder">&lt;$1&gt;</span>')
      .replace(/\[([^\]]+)\]\(((?:https?:\/\/|\/|\.)[^)\s]*)\)/g, '<a href="$2">$1</a>');
  }).join("");
}

function markdown(text) {
  const lines = text.replace(/\r/g, "").split("\n");
  const out = [];
  let paragraph = [];
  let list = null;

  const flush = () => {
    if (paragraph.length) out.push("<p>" + inline(paragraph.join(" ")) + "</p>");
    paragraph = [];
    if (list) out.push("<" + list.tag + ">" + list.items.map((i) => "<li>" + inline(i) + "</li>").join("") + "</" + list.tag + ">");
    list = null;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("```")) {
      flush();
      const code = [];
      for (i++; i < lines.length && !lines[i].startsWith("```"); i++) code.push(lines[i]);
      out.push("<pre><code>" + esc(code.join("\n")) + "</code></pre>");
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    const item = line.match(/^\s*([-*]|\d+\.)\s+(.*)$/);
    if (heading) {
      flush();
      const level = Math.min(heading[1].length, 3);
      out.push("<h" + level + ">" + inline(heading[2]) + "</h" + level + ">");
    } else if (item) {
      if (paragraph.length) { const keep = list; list = null; flush(); list = keep; }
      const tag = /\d/.test(item[1]) ? "ol" : "ul";
      if (!list || list.tag !== tag) { flush(); list = {tag, items: []}; }
      list.items.push(item[2]);
    } else if (!line.trim()) {
      flush();
    } else if (list && /^\s+\S/.test(line)) {
      list.items[list.items.length - 1] += " " + line.trim();
    } else if (/^\s{4}/.test(line) && !paragraph.length && !list) {
      const code = [line.slice(4)];
      while (i + 1 < lines.length && (/^\s{4}/.test(lines[i + 1]) || !lines[i + 1].trim())) {
        code.push(lines[++i].slice(4));
      }
      out.push("<pre><code>" + esc(code.join("\n").replace(/\s+$/, "")) + "</code></pre>");
    } else {
      if (list) flush();
      paragraph.push(line.trim());
    }
  }
  flush();
  return out.join("\n");
}

function diff(text) {
  const lines = text.replace(/\n$/, "").split("\n").map((line) => {
    let kind = "";
    if (line.startsWith("diff --git")) kind = "file";
    else if (line.startsWith("@@")) kind = "hunk";
    else if (line.startsWith("+") && !line.startsWith("+++")) kind = "add";
    else if (line.startsWith("-") && !line.startsWith("---")) kind = "del";
    return '<span class="' + kind + '">' + esc(line || " ") + "</span>";
  });
  return '<pre class="diff">' + lines.join("") + "</pre>";
}

// ---------------------------------------------------------------------------
// loading

async function refresh() {
  if (!token) return;
  try {
    view.workplans = await api("/api/workplans");
    if (!view.workplans.some((w) => w.id === view.selected)) {
      const current = view.workplans.find((w) => w.current);
      view.selected = current ? current.id : (view.workplans.length ? view.workplans[view.workplans.length - 1].id : null);
    }
    view.status = view.selected ? await api("/api/status?id=" + encodeURIComponent(view.selected)) : null;
  } catch (e) {
    say(e.message, "error");
  }
  render();
}

function task(id) {
  return view.status ? view.status.tasks.find((t) => t.id === id) : null;
}

// ---------------------------------------------------------------------------
// the page

function render() {
  renderPicker();
  renderPlan();
  renderBoard();
  if (view.panel && !view.editing) renderPanel();
}

function renderPicker() {
  const picker = $("picker");
  picker.innerHTML = "";
  for (const w of view.workplans) {
    const option = document.createElement("option");
    option.value = w.id;
    option.textContent = w.id + (w.editable ? "" : " (read-only)");
    option.selected = w.id === view.selected;
    picker.append(option);
  }
  picker.disabled = view.busy || !view.workplans.length;
  $("new-plan").disabled = view.busy;
}

function renderPlan() {
  const s = view.status;
  $("plan").hidden = !s;
  if (!s) {
    $("board").innerHTML = token
      ? '<p class="notice">No workplans yet. Choose New workplan to start one.</p>'
      : "";
    return;
  }
  $("title").textContent = s.title || s.workplan;
  $("branch").textContent = s.branch;
  $("source").textContent = s.source === "tree" ? "" : "(read from " + s.source + ")";
  $("goal").innerHTML = markdown(s.goal || "");
  const notice = $("read-only");
  notice.hidden = s.editable;
  const merged = s.tasks.length > 0 && s.tasks.every((t) => ["merged", "dropped"].includes(t.state));
  notice.textContent = merged
    ? "Merged into master. Read-only."
    : "Read-only. Check out " + s.branch + " to change this workplan; the page follows the branch on its next refresh.";

  const states = s.tasks.map((t) => t.state);
  const finished = states.length > 0 && states.every((x) => ["complete", "dropped", "merged"].includes(x))
    && states.includes("complete");
  $("define-tasks").hidden = !s.editable;
  $("merge").hidden = !s.editable;
  $("define-tasks").disabled = view.busy;
  $("merge").disabled = view.busy || !finished;
  $("merge").title = finished ? "" : "Every task must be complete or dropped first.";
}

function renderBoard() {
  const s = view.status;
  if (!s) return;
  const board = $("board");
  board.innerHTML = "";
  if (!s.tasks.length) {
    board.innerHTML = '<p class="notice">No tasks yet. ' + (s.editable
      ? "Define tasks has the agent write them from WORKPLAN.md."
      : "None are defined on " + esc(s.branch) + ".") + "</p>";
    return;
  }
  const widths = [];
  for (const [state, phase] of STATES) {
    const tasks = s.tasks.filter((t) => t.state === state);
    if (state === "unknown" && !tasks.length) continue;
    widths.push(tasks.length ? "minmax(11rem, 1fr)" : "7.5rem");
    const column = document.createElement("div");
    column.className = "column " + phase;
    column.innerHTML = "<h2><span>" + state + '</span><span class="count">' + (tasks.length || "") + "</span></h2>";
    if (!tasks.length) column.insertAdjacentHTML("beforeend", '<p class="empty">None</p>');
    for (const t of tasks) {
      const card = document.createElement("button");
      card.className = "card";
      card.setAttribute("aria-pressed", String(view.panel && view.panel.task === t.id));
      const after = t.depends.length ? "after " + t.depends.map((d) => d.split("/")[1]).join(", ") : "";
      card.innerHTML = '<span class="number">' + t.id.split("/")[1] + "</span>"
        + '<span class="name">' + esc(t.title || "(no TASK.md)") + "</span>"
        + (after ? '<span class="after">' + after + "</span>" : "");
      card.addEventListener("click", () => openTask(t.id));
      column.append(card);
    }
    board.append(column);
  }
  board.style.gridTemplateColumns = widths.join(" ");
}

// ---------------------------------------------------------------------------
// the panel

function openTask(id) {
  view.panel = {kind: "task", task: id};
  view.tab = "TASK.md";
  view.editing = false;
  renderBoard();
  renderPanel();
}

function openPlan() {
  view.panel = {kind: "plan"};
  view.tab = "WORKPLAN.md";
  view.editing = false;
  renderBoard();
  renderPanel();
}

function closePanel() {
  view.panel = null;
  view.editing = false;
  $("panel").hidden = true;
  renderBoard();
}

function documentName() {
  return view.panel.kind === "plan" ? "WORKPLAN.md" : view.panel.task.split("/")[1] + "/" + view.tab;
}

async function renderPanel() {
  const panel = view.panel;
  const s = view.status;
  const t = panel.kind === "task" ? task(panel.task) : null;
  if (panel.kind === "task" && !t) return closePanel();
  $("panel").hidden = false;
  $("panel-title").textContent = t ? t.id.split("/")[1] : "WORKPLAN.md";
  $("panel-state").textContent = t ? t.state : s.workplan;
  $("panel-name").textContent = t ? t.title : s.title;

  const tabs = $("tabs");
  tabs.innerHTML = "";
  const names = t ? DOCS.slice() : [["Workplan", "WORKPLAN.md"]];
  if (t && PATCHED.includes(t.state)) names.push(["Patch", "patch"]);
  for (const [label, name] of names) {
    const tab = document.createElement("button");
    tab.textContent = label;
    tab.setAttribute("aria-selected", String(view.tab === name));
    tab.addEventListener("click", () => { view.tab = name; view.editing = false; renderPanel(); });
    tabs.append(tab);
  }

  $("editor").hidden = true;
  $("doc").hidden = false;
  const docActions = $("doc-actions");
  docActions.innerHTML = "";
  renderTaskActions(t);

  const doc = $("doc");
  try {
    if (view.tab === "patch") {
      const data = await api("/api/diff?task=" + encodeURIComponent(t.id));
      doc.innerHTML = diff(data.text);
      return;
    }
    const data = await api("/api/document?id=" + encodeURIComponent(s.workplan) + "&name=" + encodeURIComponent(documentName()));
    doc.innerHTML = data.text.trim() ? markdown(data.text)
      : '<p class="placeholder">' + esc(view.tab) + " is empty." + (data.editable ? " Edit it to start one." : "") + "</p>";
    if (data.editable) {
      const edit = button("Edit", true, () => startEditing(data.text));
      edit.disabled = view.busy;
      docActions.append(edit);
    }
  } catch (e) {
    doc.innerHTML = '<p class="placeholder">' + esc(e.message) + "</p>";
  }
}

function renderTaskActions(t) {
  const actions = $("task-actions");
  actions.innerHTML = "";
  if (!t || !view.status.editable) return;
  const id = t.id;
  const number = id.split("/")[1];
  const offer = (label, op, states, done) => {
    if (!states.includes(t.state)) return;
    const b = button(label, false, () => operation(label + " " + number, {op, task: id}, done));
    b.disabled = view.busy;
    actions.append(b);
  };
  offer("Produce patch", "produce-patch", ["refinement", "stale", "development"],
        (d) => "Patch produced for " + number + ": " + d.commit_msg);
  offer("Apply", "apply", ["development"], () => "Applied " + number + ".");
  offer("Accept", "accept", ["development", "testing"], (d) => "Accepted: " + d.commit);
  offer("Reject", "reject", ["testing"], () => "Rejected " + number + ".");
}

function startEditing(text) {
  view.editing = true;
  const editor = $("editor");
  editor.value = text;
  editor.hidden = false;
  $("doc").hidden = true;
  const docActions = $("doc-actions");
  docActions.innerHTML = "";
  docActions.append(
    button("Save", false, save),
    button("Cancel", true, () => { view.editing = false; renderPanel(); }),
  );
  $("task-actions").innerHTML = "";
  editor.focus();
}

async function save() {
  const name = documentName();
  try {
    await api("/api/document", {id: view.status.workplan, name, text: $("editor").value});
    say("Saved " + name + ".");
    view.editing = false;
    await refresh();
    renderPanel();
  } catch (e) {
    say(e.message, "error");
  }
}

function button(label, quiet, onClick) {
  const b = document.createElement("button");
  b.textContent = label;
  if (quiet) b.className = "quiet";
  b.addEventListener("click", onClick);
  return b;
}

// ---------------------------------------------------------------------------
// plan and merge

function newPlan() {
  const form = $("plan-form");
  form.reset();
  $("plan-dialog").showModal();
}

$("plan-dialog").addEventListener("close", () => {
  if ($("plan-dialog").returnValue !== "plan") return;
  const form = $("plan-form");
  const name = form.elements.name.value.trim();
  const goal = form.elements.goal.value.trim();
  operation("Creating workplan " + name, {op: "plan", name, goal}, (d) => {
    view.selected = d.workplan;
    return "Created " + d.workplan + " on " + d.branch + ".";
  });
});

async function startMerge() {
  try {
    const data = await api("/api/merge-message?id=" + encodeURIComponent(view.status.workplan));
    $("merge-form").elements.message.value = data.text;
    $("merge-dialog").showModal();
  } catch (e) {
    say(e.message, "error");
  }
}

$("merge-dialog").addEventListener("close", () => {
  if ($("merge-dialog").returnValue !== "merge") return;
  const message = $("merge-form").elements.message.value;
  operation("Merging " + view.status.workplan, {op: "merge", id: view.status.workplan, message},
    (d) => "Merged: " + d.commit + ". Next: " + d.next.join("; "));
});

// ---------------------------------------------------------------------------
// wiring

$("picker").addEventListener("change", (e) => {
  view.selected = e.target.value;
  closePanel();
  refresh();
});
$("new-plan").addEventListener("click", newPlan);
$("open-plan").addEventListener("click", openPlan);
$("panel-close").addEventListener("click", closePanel);
$("merge").addEventListener("click", startMerge);
$("define-tasks").addEventListener("click", () =>
  operation("Defining tasks", {op: "define-tasks", id: view.status.workplan},
    (d) => "Defined " + d.tasks.length + " task(s); committed " + d.commit + "."));
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && view.panel && !view.editing && !document.querySelector("dialog[open]")) closePanel();
});

if (!token) {
  $("no-token").hidden = false;
} else {
  refresh();
  setInterval(() => { if (!view.busy && !view.editing && !document.querySelector("dialog[open]")) refresh(); }, REFRESH_MS);
}
