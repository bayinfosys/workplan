// workplan serve: the board. Calls the server through api.js; loads nothing else.

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
// running commands

function say(text, kind) {
  const line = $("line");
  line.textContent = text || "";
  line.className = "line" + (kind ? " " + kind : "");
}

async function operation(label, call, done) {
  if (view.busy) return;
  view.busy = true;
  say(label + "...", "busy");
  render();
  let data = null;
  try {
    data = await call();
    say(done(data));
  } catch (e) {
    say(e.message, "error");
  } finally {
    view.busy = false;
    await refresh();
  }
  return data;
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
  if (!api.token) return;
  try {
    view.workplans = await api.listWorkplan();
    if (!view.workplans.some((w) => w.id === view.selected)) {
      const current = view.workplans.find((w) => w.current);
      view.selected = current ? current.id : (view.workplans.length ? view.workplans[view.workplans.length - 1].id : null);
    }
    view.status = view.selected ? await api.listTask(view.selected) : null;
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
    $("board").innerHTML = api.token
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
  $("gen-task").hidden = !s.editable;
  for (const id of ["add-task", "task-prompt", "task-reply"]) {
    $(id).hidden = !s.editable;
    $(id).disabled = view.busy;
  }
  $("merge").hidden = !s.editable;
  $("gen-task").disabled = view.busy;
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
      ? "Gen tasks has the agent write them from WORKPLAN.md."
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

let panelDraw = 0;   // only the latest drawing of the panel writes to it

async function renderPanel() {
  const draw = ++panelDraw;
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
      const data = await api.showPatch(t.id);
      if (draw !== panelDraw) return;
      doc.innerHTML = diff(data.text);
      return;
    }
    const data = await readDocument();
    if (draw !== panelDraw) return;
    doc.innerHTML = data.text.trim() ? markdown(data.text)
      : '<p class="placeholder">' + esc(view.tab) + " is empty." + (data.editable ? " Edit it to start one." : "") + "</p>";
    if (data.editable) {
      const edit = button("Edit", true, () => startEditing(data.text));
      edit.disabled = view.busy;
      docActions.append(edit);
    }
  } catch (e) {
    if (draw !== panelDraw) return;
    doc.innerHTML = '<p class="placeholder">' + esc(e.message) + "</p>";
  }
}

async function readDocument() {
  if (view.panel.kind === "plan") {
    const data = await api.showWorkplan(view.status.workplan);
    return {text: data.text, editable: data.editable};
  }
  const data = await api.showTask(view.panel.task);
  return {text: data.documents[view.tab] || "", editable: data.editable};
}

function renderTaskActions(t) {
  const actions = $("task-actions");
  actions.innerHTML = "";
  if (!t || !view.status.editable) return;
  const id = t.id;
  const number = id.split("/")[1];
  const offer = (label, op, states, done) => {
    if (!states.includes(t.state)) return;
    const b = button(label, false, () => operation(label + " " + number, () => op(id), done));
    b.disabled = view.busy;
    actions.append(b);
  };
  offer("Gen patch", api.genPatch, ["refinement", "stale", "development"],
        (d) => "Patch generated for " + number + ": " + d.commit_msg);
  if (["refinement", "stale", "development"].includes(t.state)) {
    const copy = button("Copy prompt", true, () => copyPrompt(() => api.genPatchPrompt(id)));
    const paste = button("Paste reply", true, () => askReply("patch", id));
    copy.disabled = paste.disabled = view.busy;
    actions.prepend(copy, paste);
  }
  offer("Apply", api.applyPatch, ["development"], () => "Applied " + number + ".");
  offer("Accept", api.acceptPatch, ["development", "testing"], (d) => "Accepted: " + d.commit);
  offer("Reject", api.rejectPatch, ["testing"], () => "Rejected " + number + ".");
  const drop = (label, states, text, call, done) => {
    if (!states.includes(t.state)) return;
    const b = button(label, true, async () => {
      if (await ask(label + " " + number + "?", text, label)) {
        operation(label + " " + number, () => call(id), done);
      }
    });
    b.disabled = view.busy;
    actions.prepend(b);
  };
  drop("Drop patch", ["waiting", "stale", "development"],
       "Deletes output.patch and COMMIT_MSG. The task stays as it is.",
       api.dropPatch, () => "Dropped the patch for " + number + ".");
  drop("Drop task", ["unspecified", "refinement", "waiting", "stale", "development"],
       "Moves the task to Dropped in WORKPLAN.md and commits WORKPLAN.md. Its files stay.",
       api.dropTask, (d) => "Dropped: " + d.commit);
}

function startEditing(text) {
  panelDraw++;          // a drawing still loading must not replace the editor
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
    const text = $("editor").value;
    if (view.panel.kind === "plan") await api.editWorkplan(view.status.workplan, text);
    else await api.editTask(view.panel.task, view.tab, text);
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
  operation("Creating workplan " + name, () => api.addWorkplan(name, goal), (d) => {
    view.selected = d.workplan;
    return "Created " + d.workplan + " on " + d.branch + ".";
  });
});

function newTask() {
  $("task-form").reset();
  $("task-dialog").showModal();
}

$("task-dialog").addEventListener("close", async () => {
  if ($("task-dialog").returnValue !== "add") return;
  const form = $("task-form");
  const title = form.elements.title.value.trim();
  const depend = form.elements.depend.value.split(",").map((d) => d.trim()).filter(Boolean);
  const id = view.status.workplan;
  const added = await operation("Adding task", () => api.addTask(id, title, depend),
    (d) => "Added " + d.task + ".");
  if (!added) return;
  openTask(added.task);
  const data = await api.showTask(added.task);
  startEditing(data.documents["TASK.md"]);
});

// ---------------------------------------------------------------------------
// manual mode: a prompt for any chat, and its reply pasted back

async function copyPrompt(load) {
  try {
    const data = await load();
    await navigator.clipboard.writeText(data.prompt);
    say("Prompt copied: paste it into a chat, then paste the reply back here.");
  } catch (e) {
    say(e.message, "error");
  }
}

function ask(title, text, ok) {
  $("confirm-title").textContent = title;
  $("confirm-text").textContent = text;
  $("confirm-ok").textContent = ok;
  const dialog = $("confirm-dialog");
  dialog.returnValue = "";
  dialog.showModal();
  return new Promise((resolve) =>
    dialog.addEventListener("close", () => resolve(dialog.returnValue === "ok"), {once: true}));
}

let replyFor = null;   // {kind: "patch", task} or {kind: "tasks", workplan}

function askReply(kind, target) {
  replyFor = kind === "patch" ? {kind, task: target} : {kind, workplan: target};
  $("reply-form").reset();
  $("reply-title").textContent = kind === "patch" ? "Paste reply for " + target.split("/")[1]
    : "Paste reply with tasks";
  $("reply-hint").textContent = kind === "patch"
    ? "The chat's whole reply: the commit message line and the diff."
    : "The chat's whole reply: each file after its ===== path ===== line.";
  $("reply-dialog").showModal();
}

$("reply-dialog").addEventListener("close", () => {
  if ($("reply-dialog").returnValue !== "use" || !replyFor) return;
  const reply = $("reply-form").elements.reply.value;
  const target = replyFor;
  if (target.kind === "patch") {
    operation("Using the reply", () => api.addPatch(target.task, reply),
      (d) => "Patch from the reply for " + target.task.split("/")[1] + ": " + d.commit_msg);
  } else {
    operation("Using the reply", () => api.addTaskReply(target.workplan, reply),
      (d) => "Added " + d.tasks.length + " task(s) from the reply.");
  }
});

async function startMerge() {
  try {
    const data = await api.mergeMessage(view.status.workplan);
    $("merge-form").elements.message.value = data.message;
    $("merge-dialog").showModal();
  } catch (e) {
    say(e.message, "error");
  }
}

$("merge-dialog").addEventListener("close", () => {
  if ($("merge-dialog").returnValue !== "merge") return;
  const message = $("merge-form").elements.message.value;
  const id = view.status.workplan;
  operation("Merging " + id, () => api.mergeWorkplan(id, message),
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
$("add-task").addEventListener("click", newTask);
$("task-prompt").addEventListener("click", () =>
  copyPrompt(() => api.genTaskPrompt(view.status.workplan)));
$("task-reply").addEventListener("click", () => askReply("tasks", view.status.workplan));
$("panel-close").addEventListener("click", closePanel);
$("merge").addEventListener("click", startMerge);
$("gen-task").addEventListener("click", () => {
  const id = view.status.workplan;
  operation("Generating tasks", () => api.genTask(id),
    (d) => "Generated " + d.tasks.length + " task(s); committed " + d.commit + ".");
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && view.panel && !view.editing && !document.querySelector("dialog[open]")) closePanel();
});

if (!api.token) {
  $("no-token").hidden = false;
} else {
  refresh();
  setInterval(() => { if (!view.busy && !view.editing && !document.querySelector("dialog[open]")) refresh(); }, REFRESH_MS);
}
