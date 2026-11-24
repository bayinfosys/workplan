// workplan serve: one function per command the page uses, each calling
// the command's route (see registry.py). The token comes from the page's
// address, as workplan serve printed it.

"use strict";

const api = (() => {
  const token = new URLSearchParams(location.search).get("token") || "";
  const one = encodeURIComponent;
  const task = (id) => id.split("/").map(one).join("/");

  async function request(method, path, body) {
    const response = await fetch(path, {
      method,
      headers: {"X-Workplan-Token": token, "Content-Type": "application/json"},
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    let reply = {};
    try { reply = await response.json(); } catch (e) { reply = {error: response.statusText}; }
    if (!response.ok) throw new Error(reply.error || response.statusText);
    return reply.data;
  }

  return {
    token,

    listWorkplan: () => request("GET", "/api/workplan"),
    showWorkplan: (id) => request("GET", "/api/workplan/" + one(id)),
    addWorkplan: (name, goal) => request("POST", "/api/workplan", {name, goal}),
    editWorkplan: (id, text) => request("PUT", "/api/workplan/" + one(id), {text}),
    mergeWorkplan: (id, message) =>
      request("POST", "/api/workplan/" + one(id) + "/merge", {message}),
    mergeMessage: (id) => request("POST", "/api/workplan/" + one(id) + "/merge", {show: true}),

    listTask: (id) => request("GET", "/api/workplan/" + one(id) + "/task"),
    showTask: (id) => request("GET", "/api/task/" + task(id)),
    addTask: (id, title, depend) =>
      request("POST", "/api/workplan/" + one(id) + "/task", {title, depend}),
    addTaskReply: (id, reply) =>
      request("POST", "/api/workplan/" + one(id) + "/task", {reply}),
    genTask: (id) => request("POST", "/api/workplan/" + one(id) + "/task/gen", {}),
    genTaskPrompt: (id) =>
      request("POST", "/api/workplan/" + one(id) + "/task/gen", {prompt: true}),
    dropTask: (id) => request("DELETE", "/api/task/" + task(id)),
    editTask: (id, doc, text) => request("PUT", "/api/task/" + task(id) + "/" + one(doc), {text}),

    showPatch: (id) => request("GET", "/api/task/" + task(id) + "/patch"),
    addPatch: (id, reply) => request("POST", "/api/task/" + task(id) + "/patch", {reply}),
    genPatch: (id) => request("POST", "/api/task/" + task(id) + "/patch/gen", {}),
    genPatchPrompt: (id) =>
      request("POST", "/api/task/" + task(id) + "/patch/gen", {prompt: true}),
    applyPatch: (id) => request("POST", "/api/task/" + task(id) + "/patch/apply", {}),
    acceptPatch: (id) => request("POST", "/api/task/" + task(id) + "/patch/accept", {}),
    dropPatch: (id) => request("DELETE", "/api/task/" + task(id) + "/patch"),
    rejectPatch: (id) => request("POST", "/api/task/" + task(id) + "/patch/reject", {}),
  };
})();
