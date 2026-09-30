const PEIP = {
  user: null,
  lang: localStorage.getItem("peip_lang") || "en",
  tree: null,
  learnStage: 0,
  learnChapter: null,
};

const NAV = {
  admin: ["dash", "demo", "ingest", "curriculum", "knowledge", "generate", "review", "learn", "assess", "copilot", "teacherDash", "studentDash", "gov", "audit"],
  teacher: ["dash", "demo", "ingest", "curriculum", "knowledge", "generate", "review", "learn", "assess", "copilot", "teacherDash", "studentDash", "gov", "audit"],
  student: ["dash", "learn", "assess", "studentDash"],
  management: ["dash", "demo", "curriculum", "knowledge", "gov", "teacherDash", "studentDash", "audit"],
};

const BOTTOM = {
  admin: ["dash", "generate", "learn", "gov"],
  teacher: ["dash", "generate", "learn", "gov"],
  student: ["dash", "learn", "assess", "studentDash"],
  management: ["dash", "gov", "teacherDash", "audit"],
};

const EMBLEM = `<svg class="emblem" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#01411C" stroke="#c9a227" stroke-width="1.2"/><path fill="#fff" d="M14.6 6.1a6.3 6.3 0 1 0 3.1 11 7.3 7.3 0 1 1-3.1-11z"/><path fill="#fff" d="M16.9 7l.5 1.55 1.62.02-1.3.96.48 1.55-1.3-.97-1.3.97.48-1.55-1.3-.96 1.62-.02z"/></svg>`;

const STAGES = ["Learn", "Understand", "Practice", "Assess", "Identify gap", "Recommend", "Reassess"];

function el(html) {
  const d = document.createElement("div");
  d.innerHTML = html.trim();
  return d.firstElementChild;
}

function esc(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function boot() {
  document.documentElement.lang = PEIP.lang === "ur" ? "ur" : "en";
  document.documentElement.dir = PEIP.lang === "ur" ? "rtl" : "ltr";
  const app = document.getElementById("app");
  if (!api.token) {
    app.innerHTML = "";
    app.append(loginView());
    return;
  }
  try {
    PEIP.user = await api.me();
    PEIP.lang = PEIP.user.language || PEIP.lang;
  } catch {
    api.token = "";
    localStorage.removeItem("peip_token");
    app.innerHTML = "";
    app.append(loginView());
    return;
  }
  renderShell();
  go(location.hash.replace("#/", "") || "dash");
}

function nationBar() {
  return `<div class="nation"><span style="display:flex;align-items:center;gap:8px">${EMBLEM}<b>${t("pakistan")}</b></span><span>${t("punjabGov")}</span></div>`;
}

async function signIn(username, password, errBox) {
  try {
    const r = await api.login(username, password);
    api.token = r.token;
    localStorage.setItem("peip_token", r.token);
    PEIP.user = r.user;
    boot();
  } catch (e) {
    if (errBox) errBox.innerHTML = `<div class="err">${esc(e.message)}</div>`;
  }
}

function loginView() {
  const root = el(`<div>
    ${nationBar()}
    <div class="login">
    <div class="login-left">
      <div>
        <div class="brand-kicker">${t("dept")}</div>
        <h1>${t("platform")}</h1>
        <p>${t("access")}</p>
        <div class="chain">
          <span>Curriculum</span><span>Knowledge</span><span>Learning</span><span>Assessment</span><span>Diagnosis</span><span>Improvement</span>
        </div>
      </div>
      <div class="login-meta">${t("official")}<br/>PCTB Grade 7 General Science · 5 chapters</div>
    </div>
    <div class="login-right">
      <div class="row" style="justify-content:space-between">
        <h2>${t("signin")}</h2>
        <button type="button" class="btn ghost" id="lang0">${t("lang")}</button>
      </div>
      <p class="hint">${t("tapRole")}</p>
      <p class="hint">Student records stay inside the school class. This prototype does not export personal data. By entering you agree to official demonstration use only.</p>
      <div class="roles">
        <button type="button" class="role-card" data-u="teacher" data-p="teacher123"><b>${t("teacher")}</b><span>Ayesha Khan · tap to enter</span></button>
        <button type="button" class="role-card" data-u="student" data-p="student123"><b>${t("student")}</b><span>Ahmed Ali · tap to enter</span></button>
        <button type="button" class="role-card" data-u="director" data-p="director123"><b>${t("management")}</b><span>Monitoring · tap to enter</span></button>
        <button type="button" class="role-card" data-u="admin" data-p="admin123"><b>${t("admin")}</b><span>Curriculum wing · tap to enter</span></button>
      </div>
      <label>${t("username")}</label>
      <input id="u" value="teacher" autocomplete="username" />
      <label>${t("password")}</label>
      <input id="p" type="password" value="teacher123" autocomplete="current-password" />
      <div id="login-err"></div>
      <button class="btn block mt" id="go" type="button">${t("enter")}</button>
    </div>
  </div></div>`);
  const err = root.querySelector("#login-err");
  root.querySelectorAll(".role-card").forEach((b) => {
    b.onclick = () => signIn(b.dataset.u, b.dataset.p, err);
  });
  root.querySelector("#go").onclick = () =>
    signIn(root.querySelector("#u").value.trim(), root.querySelector("#p").value, err);
  root.querySelector("#p").addEventListener("keydown", (e) => {
    if (e.key === "Enter") root.querySelector("#go").click();
  });
  root.querySelector("#lang0").onclick = () => {
    PEIP.lang = PEIP.lang === "en" ? "ur" : "en";
    localStorage.setItem("peip_lang", PEIP.lang);
    boot();
  };
  return root;
}

function closeMenu() {
  document.querySelector(".shell")?.classList.remove("nav-open");
}

function renderShell() {
  const items = NAV[PEIP.user.role] || NAV.teacher;
  const bottom = BOTTOM[PEIP.user.role] || BOTTOM.teacher;
  const app = document.getElementById("app");
  app.innerHTML = "";
  app.append(
    el(`<div class="shell">
      <div class="scrim" id="scrim"></div>
      <aside class="side">
        <div class="logo">${EMBLEM}<div>${t("dept")}<small>${t("punjabGov")}</small></div></div>
        <nav>${items.map((k) => `<a href="#/${k}" data-k="${k}">${t(k)}</a>`).join("")}</nav>
        <div class="who"><b>${esc(PEIP.user.name)}</b>${esc(PEIP.user.role)} · ${esc(PEIP.user.school || t("punjabGov"))}<div class="mt"><button class="btn ghost" id="lo" type="button">${t("logout")}</button></div></div>
      </aside>
      <section class="main">
        ${nationBar()}
        <div class="govbar">
          <button class="icon-btn" id="menu" type="button" aria-label="${t("menu")}">☰</button>
          <div class="titles"><strong>${t("platform")}</strong><span>${t("grounded")}</span></div>
        </div>
        <header class="top">
          <div>
            <div class="crumb" id="crumb">Home</div>
            <div class="journey" id="journey"></div>
          </div>
          <div class="top-actions">
            <button class="btn ghost" id="lang2" type="button">${t("lang")}</button>
          </div>
        </header>
        <div class="content" id="view"></div>
      </section>
      <nav class="bottom-nav">${bottom.map((k) => `<a href="#/${k}" data-k="${k}">${shortNav(t(k))}</a>`).join("")}</nav>
    </div>`)
  );
  const toggleLang = async () => {
    PEIP.lang = PEIP.lang === "en" ? "ur" : "en";
    localStorage.setItem("peip_lang", PEIP.lang);
    try { await api.language(PEIP.lang); } catch {}
    boot();
  };
  app.querySelector("#lo").onclick = () => {
    api.token = "";
    localStorage.removeItem("peip_token");
    boot();
  };
  app.querySelector("#lang2").onclick = toggleLang;
  app.querySelector("#menu").onclick = () => document.querySelector(".shell").classList.toggle("nav-open");
  app.querySelector("#scrim").onclick = closeMenu;
  app.querySelectorAll("a[data-k]").forEach((a) => (a.onclick = closeMenu));
  window.onhashchange = () => go(location.hash.replace("#/", "") || "dash");
}

function shortNav(s) {
  return String(s).replace(/^[0-9]+\.\s/, "").replace(/^[۰-۹]+\.\s/, "");
}

function go(name) {
  const key = name.split("?")[0] || "dash";
  closeMenu();
  document.querySelectorAll("[data-k]").forEach((a) => a.classList.toggle("active", a.dataset.k === key));
  const crumb = document.getElementById("crumb");
  if (crumb) crumb.textContent = t(key) || key;
  const j = document.getElementById("journey");
  if (j) {
    j.innerHTML = "Upload → Structure → Learn → Test → Diagnose → Improve → Dashboard"
      .split(" → ")
      .map((s) => `<span>${s}</span>`)
      .join("<span>→</span>");
  }
  const view = document.getElementById("view");
  const fn = VIEWS[key] || VIEWS.dash;
  view.innerHTML = `<p class="hint">Loading…</p>`;
  Promise.resolve(fn())
    .then((node) => {
      view.innerHTML = "";
      view.append(node);
    })
    .catch((e) => {
      view.innerHTML = `<div class="err">${esc(e.message)}</div>`;
    });
}

async function ensureTree() {
  if (!PEIP.tree) PEIP.tree = await api.tree();
  return PEIP.tree;
}

function firstBook(tree) {
  const books = (tree.versions || []).flatMap((v) => v.books || []);
  return books.find((b) => /PCTB|Class VII/i.test(b.title || "") && !/Ingested/i.test(b.title || "")) || books[0];
}

function chapterSelect(book, selected) {
  return `<select id="ch">${(book.chapters || [])
    .map((c) => `<option value="${c.id}" ${String(c.id) === String(selected) ? "selected" : ""}>Ch.${c.number} ${esc(c.title)}</option>`)
    .join("")}</select>`;
}

const VIEWS = {
  async dash() {
    const [ov, st, tree] = await Promise.all([api.overview(), api.stats(), ensureTree()]);
    const book = firstBook(tree);
    const role = PEIP.user.role;
    const teacherCards = `
      <a class="action" href="#/demo"><div class="n">Presentation</div><h3>11-step demo journey</h3><p>Upload → structure → learn → test → diagnose → improve.</p></a>
      <a class="action" href="#/curriculum"><div class="n">Requirement 2</div><h3>See the textbook map</h3><p>Open chapters, topics, SLOs and source lines.</p></a>
      <a class="action" href="#/generate"><div class="n">Requirement 3</div><h3>Make a test</h3><p>MCQs, homework, exam — from the approved book.</p></a>
      <a class="action" href="#/review"><div class="n">Approve</div><h3>Publish for students</h3><p>AI papers stay hidden until you tap Publish.</p></a>
      <a class="action" href="#/learn"><div class="n">Requirement 4</div><h3>Smart learning</h3><p>Photosynthesis: learn → practice → gap → retry.</p></a>
      <a class="action" href="#/studentDash"><div class="n">Requirement 5</div><h3>Student report</h3><p>Scores, weak topics, written recommendation.</p></a>
      <a class="action" href="#/copilot"><div class="n">Requirement 6</div><h3>Teacher helper</h3><p>Tap a ready sentence. It uses the textbook only.</p></a>
      <a class="action" href="#/gov"><div class="n">Requirement 7</div><h3>Punjab dashboard</h3><p>Student → school → district → Punjab KPIs.</p></a>
      <a class="action" href="#/knowledge"><div class="n">Search</div><h3>Knowledge base</h3><p>Find any idea in the uploaded curriculum.</p></a>
      <a class="action" href="#/teacherDash"><div class="n">Class</div><h3>Class results</h3><p>Who is struggling, which SLOs are weak.</p></a>
      <a class="action" href="#/assess"><div class="n">Try</div><h3>Take a published test</h3><p>Same paper students will sit.</p></a>
      <a class="action" href="#/audit"><div class="n">Record</div><h3>Audit log</h3><p>Who uploaded, generated, approved, attempted.</p></a>
    `;
    const studentCards = `
      <a class="action" href="#/learn"><div class="n">Step 1</div><h3>Learn photosynthesis</h3><p>Simple explanation from the Grade 7 book.</p></a>
      <a class="action" href="#/assess"><div class="n">Step 2</div><h3>Take a test</h3><p>Only papers your teacher published.</p></a>
      <a class="action" href="#/studentDash"><div class="n">Step 3</div><h3>See my gaps</h3><p>What is strong, what to practise next.</p></a>
    `;
    const mgmtCards = `
      <a class="action" href="#/gov"><div class="n">Main</div><h3>Punjab dashboard</h3><p>Coverage, SLO mastery, district comparison.</p></a>
      <a class="action" href="#/curriculum"><div class="n">Books</div><h3>Approved curriculum</h3><p>What is in the knowledge base.</p></a>
      <a class="action" href="#/teacherDash"><div class="n">Schools</div><h3>Class intelligence</h3><p>Live Grade 7-A, Lahore.</p></a>
      <a class="action" href="#/studentDash"><div class="n">Learner</div><h3>Sample student</h3><p>Ahmed Ali learning-gap story.</p></a>
      <a class="action" href="#/audit"><div class="n">Control</div><h3>Audit log</h3><p>Trace every official action.</p></a>
      <a class="action" href="#/knowledge"><div class="n">Search</div><h3>Knowledge base</h3><p>Confirm content is grounded.</p></a>
    `;
    const cards = role === "student" ? studentCards : role === "management" ? mgmtCards : teacherCards;
    const root = el(`<div>
      <h1 class="page-title">${role === "student" ? "Welcome, " + esc(PEIP.user.name) : t("dept")}</h1>
      <p class="lede">${t("homeHint")} Grade ${book?.grade || 7} ${esc(book?.subject || "General Science")} · ${esc(PEIP.user.school || t("punjabGov"))}</p>
      <div class="grid-4">
        <div class="metric"><div class="k">Chapters</div><div class="v">${st.chapters}</div><div class="s">approved textbook</div></div>
        <div class="metric"><div class="k">SLOs</div><div class="v">${st.slos}</div><div class="s">learning outcomes</div></div>
        <div class="metric"><div class="k">Concepts</div><div class="v">${st.concepts}</div><div class="s">traced to pages</div></div>
        <div class="metric"><div class="k">Tests</div><div class="v">${ov.assessments}</div><div class="s">${ov.attempts} attempts</div></div>
      </div>
      <h3 class="mt-2">Tap to use every requirement</h3>
      <div class="grid-2 mt">${cards}</div>
      <p class="foot">© School Education Department · ${t("punjabGov")} · Prototype for official demonstration · Content remains tied to PCTB curriculum.</p>
    </div>`);
    return root;
  },

  async ingest() {
    const root = el(`<div>
      <h1 class="page-title">Curriculum ingestion</h1>
      <p class="lede">Choose a file from your phone or computer. The system reads it and builds chapters, topics and SLOs automatically.</p>
      <div class="grid-2">
        <div class="card">
          <label>Title</label><input id="title" placeholder="General Science Class VII" />
          <label>Grade</label><input id="grade" type="number" value="7" inputmode="numeric" />
          <label>Subject</label><input id="subject" value="General Science" />
          <label>File type</label>
          <select id="kind">
            <option>Textbook</option>
            <option>Curriculum / syllabus</option>
            <option>Learning outcomes / SLOs</option>
            <option>Supporting educational material</option>
          </select>
          <label>File (PDF, Word or text)</label><input id="file" type="file" accept=".pdf,.docx,.txt,.md" />
          <p class="hint">On a laptop you can also use <code>sample_curriculum/grade7_science_punjab.txt</code>.</p>
          <button class="btn block mt" id="up">Upload and structure</button>
          <div id="out"></div>
        </div>
        <div class="card">
          <h3>What you will see next</h3>
          <p>1. Chapters extracted<br/>2. Topics and learning outcomes<br/>3. Searchable knowledge base<br/>4. Every later test cites this file</p>
          <a class="btn ghost mt" href="#/curriculum">Skip — book is already loaded</a>
        </div>
      </div>
    </div>`);
    root.querySelector("#up").onclick = async () => {
      const f = root.querySelector("#file").files[0];
      if (!f) { root.querySelector("#out").innerHTML = `<div class="err">Choose a file</div>`; return; }
      const fd = new FormData();
      fd.append("file", f);
      fd.append("grade", root.querySelector("#grade").value);
      fd.append("subject", root.querySelector("#subject").value);
      fd.append("title", (root.querySelector("#title").value || root.querySelector("#kind").value));
      root.querySelector("#up").disabled = true;
      try {
        const r = await api.upload(fd);
        PEIP.tree = null;
        root.querySelector("#out").innerHTML = `<div class="notice mt">Done. <b>${esc(r.title)}</b> → ${r.chapters} chapters, ${r.topics} topics.<div class="row mt"><a class="btn" href="#/curriculum">Open curriculum map</a></div></div>`;
      } catch (e) {
        root.querySelector("#out").innerHTML = `<div class="err mt">${esc(e.message)}</div>`;
      } finally {
        root.querySelector("#up").disabled = false;
      }
    };
    return root;
  },

  async curriculum() {
    const tree = await ensureTree();
    const versions = tree.versions || [];
    const root = el(`<div>
      <h1 class="page-title">Curriculum map</h1>
      <p class="lede">Grade → Subject → Book → Chapter → Topic → Sub-topic → SLO → Concept. Versioned, approved, and citable.</p>
    </div>`);
    versions.forEach((v) => {
      const box = el(`<div class="card mt"><div class="row"><span class="pill">${esc(v.status)}</span><span class="pill ghost">${esc(v.year)}</span></div>
        <h3 class="mt">${esc(v.name)}</h3>
        <p class="hint">${esc(v.board)} · ${esc(v.notes)}</p>
        <div class="tree"></div></div>`);
      const tEl = box.querySelector(".tree");
      (v.books || []).forEach((b) => {
        tEl.append(
          el(`<details open><summary>Grade ${b.grade} · ${esc(b.subject)} · ${esc(b.title)}</summary>
          <div class="pad">${(b.chapters || [])
            .map(
              (c) => `<details><summary>Chapter ${c.number}. ${esc(c.title)} <span class="pill ghost">${esc(c.difficulty)}</span></summary>
              <div class="pad"><p>${esc(c.summary)}</p>
              ${(c.topics || [])
                .map(
                  (tp) => `<details><summary>${esc(tp.title)}</summary>
                  <div class="pad">
                    ${(tp.slos || []).map((s) => `<div><span class="pill">${esc(s.bloom)}</span> <b>${esc(s.code)}</b> — ${esc(s.statement)}</div>`).join("")}
                    ${(tp.concepts || [])
                      .map(
                        (cn) => `<div class="mt"><b>${esc(cn.name)}</b> <span class="pill ghost">${esc(cn.source_ref)}</span><p>${esc(cn.explanation)}</p><div class="excerpt">“${esc(cn.source_excerpt)}”</div></div>`
                      )
                      .join("")}
                  </div></details>`
                )
                .join("")}
              <p class="mt"><b>Terminology</b></p>
              ${(c.terms || []).map((tm) => `<div><b>${esc(tm.term)}</b> — ${esc(tm.definition)} <span class="pill ghost">${esc(tm.source_ref)}</span></div>`).join("")}
              </div></details>`
            )
            .join("")}</div></details>`)
        );
      });
      root.append(box);
    });
    return root;
  },

  async knowledge() {
    const root = el(`<div>
      <h1 class="page-title">Curriculum knowledge base</h1>
      <p class="lede">Type a word from the book, or tap a ready search.</p>
      <div class="chips" id="chips">
        ${["photosynthesis", "stomata", "chlorophyll", "xylem", "enzymes", "food chain"].map((q) => `<button type="button" data-q="${q}">${q}</button>`).join("")}
      </div>
      <div class="row"><input id="q" placeholder="Search the approved curriculum" /><button class="btn" id="go">Search</button></div>
      <div id="res" class="mt"></div>
    </div>`);
    const run = async () => {
      const q = root.querySelector("#q").value.trim();
      if (!q) return;
      const r = await api.search(q);
      root.querySelector("#res").innerHTML = `
        <h3>Chunks</h3>
        ${(r.chunks || []).map((c) => `<div class="card mt"><div class="row"><span class="pill ghost">${esc(c.source_ref)}</span><span class="hint">score ${c.score}</span></div><p>${esc(c.text)}</p></div>`).join("") || "<p>No chunks</p>"}
        <h3 class="mt-2">Concepts</h3>
        ${(r.concepts || []).map((c) => `<div class="card mt"><b>${esc(c.name)}</b> <span class="pill ghost">${esc(c.source_ref)}</span><p>${esc(c.text)}</p></div>`).join("")}`;
    };
    root.querySelector("#go").onclick = run;
    root.querySelector("#q").addEventListener("keydown", (e) => e.key === "Enter" && run());
    root.querySelectorAll("#chips button").forEach((b) => {
      b.onclick = () => {
        root.querySelector("#q").value = b.dataset.q;
        run();
      };
    });
    return root;
  },

  async generate() {
    const tree = await ensureTree();
    const book = firstBook(tree);
    const ch0 = book.chapters[1] || book.chapters[0];
    const root = el(`<div>
      <h1 class="page-title">Assessment generator</h1>
      <p class="lede">Tap a ready test, or fill the form. Students will not see it until you publish.</p>
      <div class="chips" id="presets">
        <button type="button" data-ty="quiz" data-n="10" data-q="mcq">10 MCQs</button>
        <button type="button" data-ty="homework" data-n="6" data-q="short,mcq,fib">Homework</button>
        <button type="button" data-ty="exam" data-n="12" data-q="mcq,tf,short,long">30-mark exam</button>
        <button type="button" data-ty="worksheet" data-n="8" data-q="mcq,fib,tf">Worksheet</button>
      </div>
      <div class="grid-2">
        <div class="card">
          <label>Grade</label><select id="grade"><option value="7">Grade 7</option></select>
          <label>Subject</label><select id="subject"><option>General Science</option></select>
          <label>Chapter</label>${chapterSelect(book, ch0.id)}
          <label>Topic (optional)</label><select id="tp"><option value="">Whole chapter</option></select>
          <label>Type</label>
          <select id="ty">
            <option value="quiz">Quiz</option>
            <option value="homework">Homework</option>
            <option value="assignment">Assignment</option>
            <option value="exam">Examination paper</option>
            <option value="worksheet">Practice worksheet</option>
            <option value="chapter_test">Chapter test</option>
          </select>
          <label>Difficulty</label>
          <select id="df"><option>easy</option><option selected>medium</option><option>hard</option></select>
          <label>Question types</label>
          <div class="checks" id="types">
            ${["mcq","tf","fib","short","long","conceptual"].map((x,i)=>`<label><input type="checkbox" value="${x}" ${i<2?"checked":""}/> ${x.toUpperCase()}</label>`).join("")}
          </div>
          <label>How many questions</label><input id="n" type="number" value="8" min="3" max="30" inputmode="numeric" />
          <button class="btn block mt" id="gen">Make the paper</button>
        </div>
        <div id="preview" class="card"><p class="hint">The paper appears here with answers and textbook source lines.</p></div>
      </div>
    </div>`);
    const fillTopics = () => {
      const ch = book.chapters.find((c) => String(c.id) === root.querySelector("#ch").value);
      root.querySelector("#tp").innerHTML =
        `<option value="">Whole chapter</option>` +
        (ch?.topics || []).map((t) => `<option value="${t.id}">${esc(t.title)}</option>`).join("");
    };
    fillTopics();
    root.querySelector("#ch").onchange = fillTopics;
    const books = (tree.versions || []).flatMap((v) => v.books || []);
    root.querySelector("#grade").innerHTML = [...new Set(books.map((b) => b.grade))].map((g) => `<option value="${g}">Grade ${g}</option>`).join("");
    root.querySelector("#subject").innerHTML = [...new Set(books.map((b) => b.subject))].map((s) => `<option>${esc(s)}</option>`).join("");
    const applyBook = () => {
      const g = Number(root.querySelector("#grade").value);
      const s = root.querySelector("#subject").value;
      const b = books.find((x) => Number(x.grade) === g && x.subject === s) || book;
      const next = b.chapters[1] || b.chapters[0];
      const sel = root.querySelector("#ch");
      sel.outerHTML = chapterSelect(b, next.id);
      root.querySelector("#ch").onchange = fillTopics;
      fillTopics();
    };
    root.querySelector("#grade").onchange = applyBook;
    root.querySelector("#subject").onchange = applyBook;
    root.querySelector("#gen").onclick = async () => {
      const qtypes = [...root.querySelectorAll("#types input:checked")].map((i) => i.value);
      root.querySelector("#gen").disabled = true;
      try {
        const a = await api.generate({
          chapter_id: Number(root.querySelector("#ch").value),
          topic_id: root.querySelector("#tp").value ? Number(root.querySelector("#tp").value) : null,
          difficulty: root.querySelector("#df").value,
          assessment_type: root.querySelector("#ty").value,
          qtypes: qtypes.length ? qtypes : ["mcq"],
          n: Number(root.querySelector("#n").value),
        });
        root.querySelector("#preview").innerHTML = renderPaper(a, true) + `<div class="row mt"><button class="btn" id="pub">Publish for students</button><a class="btn ghost" href="#/review">Go to approval list</a></div>`;
        root.querySelector("#pub").onclick = async () => {
          await api.review(a.id, { status: "published", notes: "Approved from generator." });
          go("assess");
        };
      } catch (e) {
        root.querySelector("#preview").innerHTML = `<div class="err">${esc(e.message)}</div>`;
      } finally {
        root.querySelector("#gen").disabled = false;
      }
    };
    root.querySelectorAll("#presets button").forEach((b) => {
      b.onclick = () => {
        root.querySelector("#ty").value = b.dataset.ty;
        root.querySelector("#n").value = b.dataset.n;
        const want = b.dataset.q.split(",");
        root.querySelectorAll("#types input").forEach((i) => { i.checked = want.includes(i.value); });
        root.querySelector("#gen").click();
      };
    });
    return root;
  },

  async review() {
    const list = await api.assessments();
    const root = el(`<div>
      <h1 class="page-title">Teacher review</h1>
      <p class="lede">AI content is not shown to students until a teacher approves it. This is a government-facing control, not a demo extra.</p>
      <div class="table-wrap"><table class="table"><thead><tr><th>Title</th><th>Type</th><th>Status</th><th>Marks</th><th></th></tr></thead>
      <tbody>${list
        .map(
          (a) => `<tr>
          <td data-label="Title">${esc(a.title)}</td><td data-label="Type">${esc(a.type)}</td>
          <td data-label="Status"><span class="pill">${esc(a.status)}</span></td>
          <td data-label="Marks">${a.total_marks}</td>
          <td data-label="Action">${a.status !== "published" && PEIP.user.role !== "student" ? `<button class="btn" data-id="${a.id}">Publish</button>` : "Live"}</td>
        </tr>`
        )
        .join("")}</tbody></table></div>
    </div>`);
    root.querySelectorAll("button[data-id]").forEach((b) => {
      b.onclick = async () => {
        await api.review(b.dataset.id, { status: "published", notes: "Approved for class use." });
        go("review");
      };
    });
    return root;
  },

  async learn() {
    const tree = await ensureTree();
    const book = firstBook(tree);
    const photo = book.chapters.find((c) => /photo/i.test(c.title)) || book.chapters[1] || book.chapters[0];
    PEIP.learnChapter = PEIP.learnChapter || photo.id;
    const stage = PEIP.learnStage;
    const material = await api.learning(PEIP.learnChapter, null, stage >= 1);
    const dash = await api.myDash();
    const root = el(`<div>
      <h1 class="page-title">Smart learning loop</h1>
      <p class="lede">Learn → Understand → Practice → Assess → Identify gap → Recommend → Reassess. The loop is the product, not the question list.</p>
      <div class="row mt">${chapterSelect(book, PEIP.learnChapter)}</div>
      <div class="stepper mt" id="st">${STAGES.map((s, i) => `<button data-i="${i}" class="${i === stage ? "on" : ""}">${i + 1}. ${s}</button>`).join("")}</div>
      <div id="body"></div>
    </div>`);
    const body = root.querySelector("#body");
    body.append(learnBody(stage, material, dash, photo));
    root.querySelector("#ch").onchange = () => {
      PEIP.learnChapter = Number(root.querySelector("#ch").value);
      go("learn");
    };
    root.querySelectorAll("#st button").forEach((b) => {
      b.onclick = () => {
        PEIP.learnStage = Number(b.dataset.i);
        go("learn");
      };
    });
    return root;
  },

  async assess() {
    const list = await api.assessments();
    const root = el(`<div>
      <h1 class="page-title">Published assessments</h1>
      <p class="lede">Only teacher-approved papers appear here.</p>
      ${(list || [])
        .map(
          (a) => `<div class="card mt"><div class="row"><span class="pill">${esc(a.type)}</span><span class="pill ghost">${esc(a.difficulty)}</span></div>
          <h3 class="mt">${esc(a.title)}</h3>
          <p>${a.count} items · ${a.total_marks} marks · ${esc(a.chapter?.title || "")}</p>
          <button class="btn mt" data-id="${a.id}">Attempt</button></div>`
        )
        .join("") || "<p>No published assessments.</p>"}
    </div>`);
    root.querySelectorAll("button[data-id]").forEach((b) => {
      b.onclick = () => startAttempt(b.dataset.id);
    });
    return root;
  },

  async copilot() {
    const tree = await ensureTree();
    const book = firstBook(tree);
    const root = el(`<div>
      <h1 class="page-title">Teacher copilot</h1>
      <p class="lede">Natural-language requests, answered from the approved knowledge base — not from the open internet.</p>
      <div class="suggest">
        ${[
          "Generate a Grade 7 Mathematics quiz from Chapter 3.",
          "Create 10 medium-difficulty MCQs.",
          "Prepare homework from today's chapter.",
          "Create a 30-mark examination.",
          "Explain this concept for a weak student.",
          "Generate remedial exercises.",
          "Show which SLOs students are struggling with.",
        ]
          .map((s) => `<button type="button">${esc(s)}</button>`)
          .join("")}
      </div>
      <div class="row">${chapterSelect(book, book.chapters[1]?.id || book.chapters[0].id)}</div>
      <div class="chat mt">
        <div class="chat-log" id="log"></div>
        <form class="chat-form"><input id="prompt" placeholder="Ask the copilot…" /><button class="btn">Send</button></form>
      </div>
    </div>`);
    const log = root.querySelector("#log");
    const send = async (text) => {
      log.append(el(`<div class="bubble me">${esc(text)}</div>`));
      try {
        const r = await api.copilot({ prompt: text, chapter_id: Number(root.querySelector("#ch").value) });
        const extra = r.assessment_id
          ? `<div class="mt"><a class="btn" href="#/review">Review assessment #${r.assessment_id}</a></div>`
          : r.material
          ? `<p class="mt">${esc(r.material.concepts?.[0]?.simple_explanation || r.material.concepts?.[0]?.explanation || "")}</p>`
          : r.weak_slos
          ? `<ul>${(r.weak_slos || []).map((s) => `<li><b>${esc(s.code)}</b> ${esc(s.statement)} (${s.score}%)</li>`).join("")}</ul>`
          : "";
        log.append(el(`<div class="bubble bot"><b>${esc(r.intent)}</b><p>${esc(r.message)}</p>${extra}</div>`));
      } catch (e) {
        log.append(el(`<div class="bubble bot">${esc(e.message)}</div>`));
      }
      log.scrollTop = log.scrollHeight;
    };
    root.querySelector("form").onsubmit = (e) => {
      e.preventDefault();
      const v = root.querySelector("#prompt").value.trim();
      if (!v) return;
      root.querySelector("#prompt").value = "";
      send(v);
    };
    root.querySelectorAll(".suggest button").forEach((b) => (b.onclick = () => send(b.textContent)));
    return root;
  },

  async teacherDash() {
    const d = await api.teacher();
    const root = el(`<div>
      <h1 class="page-title">Class intelligence</h1>
      <p class="lede">Live mastery from assessment attempts in Grade 7-A, GGHS Model Town, Lahore.</p>
      <div class="grid-4">
        <div class="metric"><div class="k">Class average</div><div class="v">${d.class_average}</div></div>
        <div class="metric"><div class="k">Published papers</div><div class="v">${d.published}</div></div>
        <div class="metric"><div class="k">Pending review</div><div class="v">${d.pending}</div></div>
        <div class="metric"><div class="k">Students</div><div class="v">${d.students.length}</div></div>
      </div>
      <h3 class="mt-2">Roster</h3>
      <div class="table-wrap"><table class="table"><thead><tr><th>Student</th><th>Attempts</th><th>Average</th><th>Latest</th></tr></thead>
      <tbody>${d.students.map((s) => `<tr><td data-label="Student">${esc(s.name)}</td><td data-label="Attempts">${s.attempts}</td><td data-label="Average">${s.average}</td><td data-label="Latest">${s.latest ?? "—"}</td></tr>`).join("")}</tbody></table></div>
      <h3 class="mt-2">SLOs students are struggling with</h3>
      ${(d.weak_slos || []).map((s) => `<div class="card mt"><span class="pill">${esc(s.bloom)}</span> <b>${esc(s.code)}</b> — ${esc(s.statement)}<div class="bar mt"><i style="width:${s.mastery}%"></i></div><div class="hint">${s.mastery}% mastery</div></div>`).join("") || "<p>No weak SLOs yet.</p>"}
    </div>`);
    return root;
  },

  async studentDash() {
    const d = await api.myDash();
    const root = el(`<div>
      <h1 class="page-title">Student dashboard</h1>
      <p class="lede">Overall score, subject and chapter performance, topic/SLO mastery, difficulty, strong/weak areas, and a written recommendation.</p>
      <div class="grid-4">
        <div class="metric"><div class="k">Overall</div><div class="v">${d.overall}%</div></div>
        <div class="metric"><div class="k">Latest</div><div class="v">${d.latest_percent ?? "—"}</div></div>
        <div class="metric"><div class="k">Improvement</div><div class="v">${d.improvement ?? "—"}</div><div class="s">first → latest attempt</div></div>
        <div class="metric"><div class="k">Attempts</div><div class="v">${d.attempts.length}</div></div>
      </div>
      <h3 class="mt-2">Subject performance</h3>
      ${(d.subjects || []).map((s) => `<div class="card mt"><b>${esc(s.name)}</b> ${s.score}%<div class="bar mt"><i style="width:${s.score}%"></i></div></div>`).join("") || `<div class="card mt">General Science</div>`}
      <h3 class="mt-2">Chapter performance</h3>
      ${(d.chapters || []).map((c) => `<div class="card mt"><b>${esc(c.name)}</b> ${c.score}%<div class="bar mt"><i style="width:${c.score}%"></i></div></div>`).join("") || "<p>—</p>"}
      <h3 class="mt-2">Difficulty-level performance</h3>
      <div class="grid-3">${Object.entries(d.difficulty || {}).map(([k, v]) => `<div class="metric"><div class="k">${esc(k)}</div><div class="v">${v}%</div></div>`).join("") || "<p class='hint'>Attempt a test to fill this.</p>"}</div>
      <div class="grid-2 mt-2">
        <div class="card"><h3>Strong areas</h3>${(d.strong || []).map((c) => `<div class="mt"><b>${esc(c.name)}</b> ${c.score}% <span class="pill ghost">${esc(c.source_ref)}</span></div>`).join("") || "<p>—</p>"}</div>
        <div class="card"><h3>Weak areas</h3>${(d.weak || []).map((c) => `<div class="mt"><b>${esc(c.name)}</b> ${c.score}%</div>`).join("") || "<p>—</p>"}</div>
      </div>
      <div class="notice mt-2">${esc(d.recommendation || "Complete an assessment to generate a recommendation.")}</div>
      <h3 class="mt-2">Recommended activities</h3>
      <ul>${(d.activities || []).map((a) => `<li>${esc(a)}</li>`).join("")}</ul>
      <a class="btn mt" href="#/learn">Open targeted practice in the learning loop</a>
      <h3 class="mt-2">Topic / SLO mastery</h3>
      <div class="table-wrap"><table class="table"><thead><tr><th>SLO</th><th>Bloom</th><th>Mastery</th></tr></thead>
      <tbody>${(d.slos || []).map((s) => `<tr><td data-label="SLO"><b>${esc(s.code)}</b> ${esc(s.statement)}</td><td data-label="Bloom">${esc(s.bloom)}</td><td data-label="Mastery">${s.score}%</td></tr>`).join("")}</tbody></table></div>
      <h3 class="mt-2">Improvement across attempts</h3>
      <p>${(d.trend || []).map((p, i) => `Attempt ${i + 1}: ${p}%`).join(" → ") || "—"}</p>
      <p class="foot">Student privacy: scores are visible to the class teacher and school officers only. No public export in this prototype.</p>
    </div>`);
    return root;
  },

  async gov() {
    const d = await api.management();
    const h = d.hierarchy.punjab;
    const root = el(`<div>
      <h1 class="page-title">Punjab view</h1>
      <p class="lede">${esc(d.hierarchy.note)}</p>
      <div class="grid-4">
        <div class="metric"><div class="k">Curriculum coverage</div><div class="v">${h.curriculum_coverage}%</div></div>
        <div class="metric"><div class="k">SLO mastery</div><div class="v">${h.slo_mastery}</div></div>
        <div class="metric"><div class="k">Achievement</div><div class="v">${h.achievement}</div></div>
        <div class="metric"><div class="k">Districts modelled</div><div class="v">${h.districts}</div></div>
      </div>
      <h3 class="mt-2">Subject performance</h3>
      ${(d.subject_performance || []).map((s) => `<div class="card mt">Grade ${s.grade} · ${esc(s.subject)} · ${s.achievement}%</div>`).join("")}
      <h3 class="mt-2">Assessment performance</h3>
      <div class="grid-3">
        <div class="metric"><div class="k">Published papers</div><div class="v">${(d.assessment_performance || {}).published ?? "—"}</div></div>
        <div class="metric"><div class="k">Attempts</div><div class="v">${(d.assessment_performance || {}).attempts ?? "—"}</div></div>
        <div class="metric"><div class="k">Live average</div><div class="v">${(d.assessment_performance || {}).live_average ?? "—"}</div></div>
      </div>
      <h3 class="mt-2">Improvement trend (live class)</h3>
      <p>${(d.improvement_trend || []).map((x) => `${esc(x.label)}: ${x.percent}%`).join(" → ") || "—"}</p>
      <h3 class="mt-2">Student → Class → School → District → Punjab</h3>
      <div class="table-wrap"><table class="table"><thead><tr><th>District</th><th>Schools</th><th>Coverage</th><th>Achievement</th><th>SLO mastery</th><th>Weak topic</th></tr></thead>
      <tbody>${d.districts
        .map(
          (x) => `<tr><td data-label="District">${esc(x.name)}</td><td data-label="Schools">${x.schools}</td><td data-label="Coverage">${x.curriculum_coverage}%</td><td data-label="Achievement">${x.achievement}</td><td data-label="SLO">${x.slo_mastery}</td><td data-label="Weak topic">${esc(x.weak_topic)}</td></tr>`
        )
        .join("")}</tbody></table></div>
      <h3 class="mt-2">How this scales</h3>
      <div class="chain" style="margin-top:12px">${(d.scale_path || []).map((s) => `<span style="border-color:#ccc;color:#111;background:#fff">${esc(s)}</span>`).join("")}</div>
    </div>`);
    return root;
  },

  async audit() {
    const d = await api.audit();
    const root = el(`<div>
      <h1 class="page-title">Audit log</h1>
      <p class="lede">Uploads, generation, approval, attempts and copilot prompts are recorded for a future production deployment.</p>
      <div class="table-wrap"><table class="table"><thead><tr><th>When</th><th>Who</th><th>Action</th><th>Details</th></tr></thead>
      <tbody>${(d.logs || [])
        .map((l) => `<tr><td data-label="When">${esc((l.at || "").replace("T", " ").slice(0, 19))}</td><td data-label="Who">${esc(l.user)} <span class="pill ghost">${esc(l.role)}</span></td><td data-label="Action">${esc(l.action)}</td><td data-label="Details">${esc(l.details)}</td></tr>`)
        .join("")}</tbody></table></div>
    </div>`);
    return root;
  },

  async demo() {
    const steps = [
      ["01", "Upload curriculum", "#/ingest", "PDF, DOCX or TXT — textbook, syllabus or SLOs."],
      ["02", "AI structures Grade / Subject / Chapter / Topic / SLO", "#/curriculum", "Open the approved PCTB book tree with citations."],
      ["03", "Select chapter", "#/learn", "Choose Photosynthesis (Chapter 2)."],
      ["04", "Generate learning material", "#/learn", "Learn + Understand stages from the knowledge base."],
      ["05", "Generate MCQs / subjective / assignment / quiz", "#/generate", "Or tap 10 MCQs / homework / 30-mark exam."],
      ["06", "Student attempts assessment", "#/assess", "Sign in as Ahmed if needed, then Attempt."],
      ["07", "AI evaluates performance", "#/assess", "Score, marks and explanations appear on submit."],
      ["08", "Identify learning gaps", "#/studentDash", "Weak concepts and struggling SLOs."],
      ["09", "Recommend personalized learning", "#/studentDash", "Written recommendation + activities."],
      ["10", "Generate new practice", "#/learn", "Go to Recommend → targeted practice."],
      ["11", "Show student / teacher dashboard", "#/teacherDash", "Then open Punjab dashboard for scale."],
    ];
    const root = el(`<div>
      <h1 class="page-title">Required end-to-end demo</h1>
      <p class="lede">Tap each step in order. This is the 15–20 minute presentation journey. Prototype slice: Grade 7 · General Science · 5 PCTB chapters.</p>
      ${steps.map(([n, title, href, hint]) => `<a class="action mt" href="${href}"><div class="n">Step ${n}</div><h3>${esc(title)}</h3><p>${esc(hint)}</p></a>`).join("")}
      <div class="card mt-2">
        <h3>How it works</h3>
        <p>Curriculum documents → parsing → structured SQLite (Grade→SLO→Concept) → RAG search over textbook chunks → grounded generation → assessment engine → student scores → recommendation engine → dashboards (class → district → Punjab).</p>
        <p>AI output must cite a source excerpt. Students only see papers a teacher has published. Urdu/English, audit log, curriculum version, and age filter are in this prototype.</p>
      </div>
      <div class="card mt">
        <h3>Why this design</h3>
        <p>FastAPI + HTML so a teacher can run it on a laptop in 2–3 days. The schema is grade-agnostic: add Grade 8 Physics the same way. Optional cloud LLM; without a key the engine still generates from approved chunks so the demo never depends on a missing API.</p>
      </div>
      <div class="card mt">
        <h3>Problem and impact</h3>
        <p>Teachers spend hours writing aligned papers. Students practise the wrong items. Officers cannot see SLO gaps. This platform cuts paper-setting time, keeps items on the PCTB book, diagnoses gaps, and shows a path from one class in Lahore to Punjab-wide KPIs.</p>
      </div>
      <div class="card mt">
        <h3>Scale path</h3>
        <p>1 subject prototype → Grades 1–10 → more subjects → schools → districts → Punjab Education Intelligence Platform.</p>
      </div>
    </div>`);
    return root;
  },
};

function learnBody(stage, material, dash, chapter) {
  if (stage === 0) {
    return el(`<div class="card">
      <h3>Learn · ${esc(material.chapter.title)}</h3>
      <p>${esc(material.chapter.summary)}</p>
      <p class="hint">Expected level ${esc(material.chapter.expected_level)} · pages ${esc(material.chapter.pages)}</p>
      ${(material.concepts || []).map((c) => `<div class="mt"><b>${esc(c.name)}</b> <span class="pill ghost">${esc(c.source_ref)}</span><p>${esc(c.explanation)}</p></div>`).join("")}
      <button class="btn mt" id="nx">Continue to simpler explanation</button>
    </div>`);
  }
  if (stage === 1) {
    const box = el(`<div class="card">
      <h3>Understand · weaker-student explanation</h3>
      ${(material.concepts || []).map((c) => `<div class="mt"><b>${esc(c.name)}</b><p>${esc(c.simple_explanation)}</p><div class="excerpt">${esc(c.example)}</div></div>`).join("")}
      <button class="btn mt" id="nx">Practice</button>
    </div>`);
    box.querySelector("#nx").onclick = () => { PEIP.learnStage = 2; go("learn"); };
    return box;
  }
  if (stage === 2 || stage === 3) {
    const box = el(`<div class="card">
      <h3>${stage === 2 ? "Practice" : "Assess"} · published diagnostic</h3>
      <p>Use the Chapter 2 diagnostic already approved for class 7-A, or generate a new paper.</p>
      <div class="row mt"><button class="btn" id="att">Open assessments</button><button class="btn ghost" id="nx">I have attempted — show gaps</button></div>
    </div>`);
    box.querySelector("#att").onclick = () => { location.hash = "#/assess"; };
    box.querySelector("#nx").onclick = () => { PEIP.learnStage = 4; go("learn"); };
    return box;
  }
  if (stage === 4 || stage === 5) {
    const box = el(`<div class="card">
      <h3>${stage === 4 ? "Identify gap" : "Recommend improvement"}</h3>
      <div class="notice">${esc(dash.recommendation || "No attempt yet. Complete the diagnostic as Ahmed to see the photosynthesis application gap.")}</div>
      <h3 class="mt">Weak concepts</h3>
      ${(dash.weak || []).map((c) => `<div><b>${esc(c.name)}</b> — ${c.score}%</div>`).join("") || "<p>—</p>"}
      <ul>${(dash.activities || []).map((a) => `<li>${esc(a)}</li>`).join("")}</ul>
      <button class="btn mt" id="nx">Generate targeted practice</button>
    </div>`);
    box.querySelector("#nx").onclick = async () => {
      const a = await api.targeted({ chapter_id: PEIP.learnChapter, n: 5, difficulty: "medium" });
      PEIP.learnStage = 6;
      startAttempt(a.id);
    };
    return box;
  }
  const box = el(`<div class="card">
    <h3>Reassess</h3>
    <p>Targeted practice is generated from the same chapter knowledge base, focusing on weak concepts. After submission, return to the student dashboard to measure improvement.</p>
    <a class="btn" href="#/studentDash">Open student dashboard</a>
  </div>`);
  return box;
}

function bindNext(node) {
  if (PEIP.learnStage > 1) return node;
  const b = node.querySelector("#nx");
  if (b) b.onclick = () => { PEIP.learnStage = Math.min(6, PEIP.learnStage + 1); go("learn"); };
  return node;
}

function renderPaper(a, answers) {
  return `<div class="row"><span class="pill">${esc(a.status)}</span><span class="pill ghost">${esc(a.type)}</span><span class="pill ghost">${a.total_marks} marks</span></div>
    <h3 class="mt">${esc(a.title)}</h3>
    ${(a.questions || [])
      .map(
        (q, i) => `<div class="q"><div class="row"><b>Q${i + 1}</b> <span class="pill ghost">${esc(q.qtype)}</span> <span class="pill">${esc(q.bloom)}</span> <span class="pill ghost">${esc(q.difficulty)}</span> ${q.slo_code ? `<span class="pill ghost">${esc(q.slo_code)}</span>` : ""} <span class="pill ghost">${esc(q.source_ref)}</span></div>
        <p>${esc(q.stem)}</p>
        ${(q.options || []).map((o) => `<div class="opt">${esc(o)}</div>`).join("")}
        ${answers ? `<p><b>Answer:</b> ${esc(q.correct_answer)}</p><p class="hint">${esc(q.explanation)}</p><div class="excerpt">Source: ${esc(q.source_excerpt)}</div>` : ""}
      </div>`
      )
      .join("")}`;
}

async function startAttempt(id) {
  const started = await api.start(id);
  const a = started.assessment;
  const view = document.getElementById("view");
  const wrap = el(`<div>
    <h1 class="page-title">${esc(a.title)}</h1>
    <p class="lede">${a.total_marks} marks · grounded items · ${esc(a.chapter?.title || "")}</p>
    <form id="exam"></form>
    <button class="btn mt" id="sub">Submit for evaluation</button>
    <div id="done"></div>
  </div>`);
  const form = wrap.querySelector("#exam");
  (a.questions || []).forEach((q, i) => {
    const block = el(`<div class="q" data-id="${q.id}"><div class="row"><b>Q${i + 1}</b> <span class="pill">${esc(q.bloom)}</span> <span class="pill ghost">${q.marks} mark</span> <span class="pill ghost">${esc(q.source_ref)}</span></div><p>${esc(q.stem)}</p></div>`);
    if (q.options && q.options.length) {
      q.options.forEach((o) => {
        const lab = el(`<label class="opt"><input type="radio" name="q${q.id}" value="${esc(o)}" /> ${esc(o)}</label>`);
        lab.querySelector("input").oninput = () => {
          block.querySelectorAll(".opt").forEach((x) => x.classList.remove("sel"));
          lab.classList.add("sel");
        };
        block.append(lab);
      });
    } else {
      block.append(el(`<textarea name="q${q.id}" rows="3" placeholder="Answer from the textbook ideas…"></textarea>`));
    }
    form.append(block);
  });
  wrap.querySelector("#sub").onclick = async () => {
    const answers = {};
    (a.questions || []).forEach((q) => {
      const sel = form.querySelector(`[name="q${q.id}"]:checked`);
      const ta = form.querySelector(`textarea[name="q${q.id}"]`);
      answers[q.id] = sel ? sel.value : ta ? ta.value : "";
    });
    wrap.querySelector("#sub").disabled = true;
    const r = await api.submit(started.attempt_id, answers);
    wrap.querySelector("#done").innerHTML = `
      <div class="notice mt">Score ${r.score}/${r.max_score} (${r.percent}%).</div>
      <div class="card mt"><b>Diagnosis</b><p>${esc(r.analysis.recommendation)}</p>
      <ul>${(r.analysis.activities || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
      ${(r.review || []).map((x) => `<div class="q"><b>${x.is_correct ? "Correct" : "Incorrect"}</b> · ${esc(x.bloom)} · ${esc(x.source_ref)}<p>${esc(x.stem)}</p><p>Given: ${esc(x.given)}</p><p>Key: ${esc(x.correct)}</p><p class="hint">${esc(x.explanation)}</p></div>`).join("")}
      <div class="row mt"><a class="btn" href="#/studentDash">Student dashboard</a><a class="btn ghost" href="#/learn">Return to learning loop</a></div>`;
  };
  view.innerHTML = "";
  view.append(wrap);
}

// attach next buttons after learn body insert
const _learn = VIEWS.learn;
VIEWS.learn = async () => {
  const node = await _learn();
  bindNext(node);
  return node;
};

boot();
