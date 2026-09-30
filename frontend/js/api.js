const api = {
  token: localStorage.getItem("peip_token") || "",
  async req(path, opts = {}) {
    const headers = { ...(opts.headers || {}) };
    if (this.token) headers.Authorization = `Bearer ${this.token}`;
    if (opts.body && !(opts.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(opts.body);
    }
    const res = await fetch(path, { ...opts, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || data.message || res.statusText);
    return data;
  },
  login(username, password) {
    return this.req("/api/auth/login", { method: "POST", body: { username, password } });
  },
  me() { return this.req("/api/auth/me"); },
  language(language) { return this.req("/api/auth/language", { method: "POST", body: { language } }); },
  tree() { return this.req("/api/curriculum/tree"); },
  search(q) { return this.req("/api/curriculum/search?q=" + encodeURIComponent(q)); },
  stats() { return this.req("/api/curriculum/stats"); },
  overview() { return this.req("/api/overview"); },
  upload(form) { return this.req("/api/ingest/upload", { method: "POST", body: form }); },
  generate(body) { return this.req("/api/assessments/generate", { method: "POST", body }); },
  assessments() { return this.req("/api/assessments"); },
  assessment(id) { return this.req("/api/assessments/" + id); },
  review(id, body) { return this.req("/api/assessments/" + id + "/review", { method: "POST", body }); },
  start(id) { return this.req("/api/assessments/" + id + "/start", { method: "POST", body: {} }); },
  submit(id, answers) { return this.req("/api/attempts/" + id + "/submit", { method: "POST", body: { answers } }); },
  learning(chapterId, topicId, simple) {
    const u = new URL("/api/learning/" + chapterId, location.origin);
    if (topicId) u.searchParams.set("topic_id", topicId);
    if (simple) u.searchParams.set("simple", "true");
    return this.req(u.pathname + u.search);
  },
  targeted(body) { return this.req("/api/practice/targeted", { method: "POST", body }); },
  copilot(body) { return this.req("/api/copilot", { method: "POST", body }); },
  myDash() { return this.req("/api/me/dashboard"); },
  teacher() { return this.req("/api/teacher/overview"); },
  management() { return this.req("/api/management/overview"); },
  audit() { return this.req("/api/audit"); },
};
