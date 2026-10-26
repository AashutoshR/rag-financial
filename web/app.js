// Audit Console — reviewer front end for the financial investigation platform.
// All document-derived text is inserted with textContent (via h()); filings are untrusted input.
"use strict";

const $ = (sel, root = document) => root.querySelector(sel);

function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "text") el.textContent = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "dataset") Object.assign(el.dataset, v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid == null || kid === false) continue;
    el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch { /* not JSON */ }
    throw new Error(detail);
  }
  return res.json();
}

function toast(msg) {
  const t = h("div", { class: "toast", role: "status", text: msg });
  document.body.append(t);
  setTimeout(() => t.remove(), 4000);
}

const store = {
  get(k, d) { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* storage unavailable */ } },
};

const state = { status: null, questions: [], qById: {}, docs: {}, reports: null, asOf: null, job: null };

// ---- formatting ---------------------------------------------------------------------------
const fmtDate = (iso) => (iso ? iso.slice(0, 10) : "—");
const isPostCutoff = (docId) => state.asOf && state.docs[docId] && fmtDate(state.docs[docId].published_at) > state.asOf;
const docLabel = (docId) => {
  const d = state.docs[docId];
  return d ? `${d.form_type} · ${d.fiscal_label}` : docId;
};

function fmtValue(value, unit) {
  const v = Number(value);
  if (unit === "USD" && Number.isFinite(v)) {
    return `${v < 0 ? "−" : ""}$${(Math.abs(v) / 1e6).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}M`;
  }
  if (unit === "ratio" && Number.isFinite(v)) return `${(v * 100).toFixed(2)}%`;
  return `${value} ${unit || ""}`.trim();
}

const FAILURE_LABELS = {
  retrieval_miss: "Required evidence not retrieved",
  citation_not_supporting: "Citations miss the required evidence",
  temporal_leakage: "Post-cutoff evidence cited",
  answered_instead_of_abstaining: "Answered instead of abstaining",
  false_abstention: "Abstained on an answerable question",
  missing_or_wrong_calculation: "Calculation missing or wrong",
  wrong_or_missing_value: "Value missing or wrong",
  wrong_direction: "Wrong direction of change",
  direction_unstated: "Direction of change not stated",
  approximation_not_stated: "Approximate value stated as exact",
  forbidden_value_stated: "Forbidden value stated",
  check_failed: "Check failed",
  artifact_structure: "Artifact structure invalid",
};
function failureChip(f) {
  const [kind, ...rest] = f.split(":");
  const detail = rest.join(":");
  return h("span", { class: "chip bad", title: f }, h("span", { class: "dot" }),
    `${FAILURE_LABELS[kind] || kind}${detail ? ` · ${detail.replaceAll("_", " ")}` : ""}`);
}

const OUTCOME_CLASS = { answer: "accent", abstention: "info", partial_answer: "warn", clarification: "warn" };
const SUPPORT_CLASS = { supported: "ok", partially_supported: "warn", contradicted: "bad", unsupported: "bad", not_verifiable: "" };

function ratioParts(s) {
  const m = /^(\d+)\/(\d+)/.exec(s || "");
  return m ? [Number(m[1]), Number(m[2])] : null;
}

// ---- status bar ---------------------------------------------------------------------------
function renderStatus() {
  const s = state.status;
  const bar = $("#status");
  bar.replaceChildren(
    ...Object.entries(s.generators).map(([, g]) =>
      h("span", { class: `chip ${g.available ? "ok" : ""}`, title: g.detail || "" }, h("span", { class: "dot" }), g.label)),
    h("span", { class: "chip", title: `Parser ${s.parser}` }, `CSN ${s.csn} · ${s.documents} docs`),
  );
}

function renderGenerators() {
  const fs = $("#generators");
  const saved = store.get("generator", "extractive");
  const seg = h("div", { class: "seg", role: "radiogroup" });
  for (const [key, g] of Object.entries(state.status.generators)) {
    const input = h("input", { type: "radio", name: "generator", value: key, disabled: !g.available,
      checked: g.available && key === saved });
    input.addEventListener("change", () => store.set("generator", key));
    seg.append(h("label", { title: g.detail || "" }, input, g.label));
  }
  if (!seg.querySelector("input:checked")) seg.querySelector("input:not(:disabled)").checked = true;
  fs.append(seg);
}

// ---- composer -----------------------------------------------------------------------------
function renderBenchSelect() {
  const sel = $("#bench-select");
  const groups = { Core: h("optgroup", { label: "Core" }), Frontier: h("optgroup", { label: "Frontier" }) };
  for (const q of state.questions) {
    const g = q.id.startsWith("h") ? groups.Frontier : groups.Core;
    g.append(h("option", { value: q.id, text: `${q.id} · ${q.question.slice(0, 80)}${q.question.length > 80 ? "…" : ""}` }));
  }
  sel.append(groups.Core, groups.Frontier);
  sel.addEventListener("change", () => {
    const q = state.qById[sel.value];
    const ta = $("#question");
    if (q) {
      ta.value = q.question;
      ta.readOnly = true;
      $("#as-of").value = q.as_of || "";
      $("#as-of").disabled = true;
      const expect = q.expected_outcome === "abstention" ? "should abstain" : "should answer";
      $("#composer-hint").textContent =
        `Benchmark item ${q.id} (${q.category.join(", ")}) — ${expect}. The run is scored automatically.` +
        (q.flags.length ? ` Looks for: ${q.flags.join("; ")}` : "");
    } else {
      ta.readOnly = false;
      $("#as-of").disabled = false;
      $("#composer-hint").textContent =
        "The baseline has no as-of filter: the date is recorded and post-cutoff evidence is flagged, not removed.";
    }
  });
}

async function submitInvestigation(ev) {
  ev.preventDefault();
  const generator = document.querySelector('input[name="generator"]:checked')?.value;
  const body = {
    question: $("#question").value,
    as_of: $("#as-of").value || null,
    generator,
    item_id: $("#bench-select").value || null,
  };
  const btn = $("#run-btn");
  btn.disabled = true;
  try {
    const { id } = await api("/api/investigations", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
    $("#result").replaceChildren();  // the previous answer must not look like this run's result
    pollJob(id);
  } catch (err) {
    toast(err.message);
    btn.disabled = false;
  }
}

const STAGES = [["queued", "Queued"], ["retrieving", "Retrieving"], ["generating", "Generating"], ["done", "Done"]];

function renderProgress(job) {
  const box = $("#progress");
  box.hidden = false;
  const idx = STAGES.findIndex(([k]) => k === job.stage);
  const steps = h("div", { class: "steps" });
  STAGES.forEach(([key, label], i) => {
    if (i) steps.append(h("span", { class: "step-sep" }));
    const cls = job.stage === "done" || i < idx ? "done" : i === idx ? "now" : "";
    steps.append(h("span", { class: `step ${cls}` }, h("span", { class: "ring" }, cls === "done" ? "✓" : ""), label));
  });
  const p = job.progress || {};
  const running = job.status === "running" || job.status === "queued";
  const local = job.request.generator === "ollama";
  let note = null;
  if (job.status === "error") note = h("div", { class: "callout bad", style: "margin:0;flex-basis:100%" }, h("strong", {}, "Run stopped"), job.error);
  else if (job.status === "cancelled") note = h("span", { class: "chip warn" },
    local ? "Cancelled — the local model is being reset, so the next run reloads it (1–3 min)" : "Cancelled");
  else if (job.status === "queued" && job.queue_position) note = h("span", { class: "muted" }, `${job.queue_position} ahead in queue`);
  else if (job.stage === "generating" && local) {
    note = h("span", { class: "muted" }, p.phase === "writing_answer"
      ? `Writing answer · ${p.tokens} tokens`
      : "Loading the model and reading the evidence — this can take a few minutes on CPU, longer right after a cancel");
  }
  const slow = running && local && job.elapsed_s > 180 && !(p.phase === "writing_answer")
    ? h("div", { class: "callout warn", style: "margin:0;flex-basis:100%" }, h("strong", {}, "Slower than usual"),
      "The local model hasn't started answering yet. Loading it can take a few minutes; other apps using the CPU, GPU " +
      "or memory slow it further. The run stops automatically if there is no progress for 7 minutes; you can also cancel it.") : null;
  const cancel = running ? h("button", { type: "button", class: "btn", onclick: async (e) => {
    e.target.disabled = true;
    try { await api(`/api/investigations/${job.id}/cancel`, { method: "POST" }); } catch (err) { toast(err.message); }
  } }, "Cancel") : null;
  box.replaceChildren(...[steps, note, h("span", { class: "elapsed" }, `${job.elapsed_s.toFixed(0)} s`), cancel, slow].filter(Boolean));
}

async function pollJob(id) {
  try {
    const job = await api(`/api/investigations/${id}`);
    renderProgress(job);
    if (job.status === "done") {
      $("#run-btn").disabled = false;
      const onWorkspace = !location.hash || location.hash === "#/investigate";
      renderArtifact(job.artifact, { score: job.score, source: "Live run", asOf: job.request.as_of, navigate: false });
      if (onWorkspace) $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
      else toast("Investigation finished — open the Investigate tab to review it.");
      return;
    }
    if (job.status === "error" || job.status === "cancelled") { $("#run-btn").disabled = false; return; }
    setTimeout(() => pollJob(id), 1000);
  } catch (err) {
    toast(err.message);
    $("#run-btn").disabled = false;
  }
}

// ---- artifact -----------------------------------------------------------------------------
function section(title, ...kids) {
  return h("div", { class: "section" }, h("h3", { text: title }), ...kids);
}

function citeChip(c, label) {
  const b = h("button", { type: "button", class: `chip cite ${isPostCutoff(c.document_id) ? "warn" : ""}`,
    title: `${docLabel(c.document_id)} — ${c.locator?.table_caption || c.locator?.heading || ""}`,
    dataset: { unit: c.unit_id } }, label || c.id);
  b.addEventListener("click", () => inspect(c.unit_id, b));
  return b;
}

function scoreSection(score) {
  const stat = (k, num, den, okWhenFull = true) => {
    const cls = den === 0 ? "" : num === den ? (okWhenFull ? "ok" : "") : "bad";
    return h("div", { class: `stat ${cls}` }, h("div", { class: "k", text: k }), h("div", { class: "v", text: den ? `${num}/${den}` : "—" }));
  };
  return section(`Scored against benchmark item ${score.id}`,
    h("div", { class: "score-grid" },
      stat("Evidence @8", score.req_hit_at_k, score.requirements),
      stat("Values", score.values_correct, score.values_expected),
      stat("Direction", score.directions_correct, score.directions_expected),
      stat("Checks", score.checks_passed, score.checks_expected),
      h("div", { class: `stat ${score.outcome_ok ? "ok" : "bad"}` }, h("div", { class: "k", text: "Outcome" }),
        h("div", { class: "v", text: score.outcome_ok ? "correct" : "wrong" }))),
    score.failures.length ? h("div", { class: "chips" }, score.failures.map(failureChip))
      : h("span", { class: "chip ok" }, h("span", { class: "dot" }), "Passed every check"));
}

function renderArtifact(art, ctx = {}) {
  state.asOf = ctx.asOf ?? art.as_of?.date ?? null;
  const cites = Object.fromEntries(art.citations.map((c) => [c.id, c]));
  const usage = art.trace?.usage || {};
  const card = h("article", { class: "card" });

  const meta = h("div", { class: "artifact-meta" },
    h("span", { class: `chip ${OUTCOME_CLASS[art.outcome] || ""}` }, art.outcome.replace("_", " ")),
    art.status !== "valid" ? h("span", { class: "chip warn" }, art.status) : null,
    art.versions?.generator ? h("span", { class: "chip" }, art.versions.model || art.versions.generator) : null,
    art.trace?.latency_ms != null ? h("span", { class: "chip" }, `${(art.trace.latency_ms / 1000).toFixed(1)} s`) : null,
    usage.input_tokens != null ? h("span", { class: "chip" }, `${usage.input_tokens} in / ${usage.output_tokens} out tokens`) : null,
    ctx.source ? h("span", { class: "source-label" }, ctx.source) : null,
    h("a", { class: "mono muted", style: "margin-left:auto", href: `#/artifact/${art.artifact_id}`,
      title: "Shareable link to this artifact" }, art.artifact_id));
  card.append(h("div", { class: "artifact-head" }, meta,
    h("div", { class: "artifact-q" }, art.question),
    h("div", { class: "muted", style: "font-size:12.5px" },
      art.as_of ? `As of: ${art.as_of.interpretation}` : "No as-of constraint — latest available evidence",
      ` · snapshot CSN ${art.snapshot.csn} · principal ${art.principal}`),
    h("p", { class: "answer" }, art.answer_summary || "—")));

  if (ctx.score) card.append(scoreSection(ctx.score));

  if (art.claims.length) {
    card.append(section(`Claims (${art.claims.length})`, art.claims.map((c) =>
      h("div", { class: "claim" },
        h("div", { class: "claim-top" },
          h("span", { class: "chip" }, c.type.replaceAll("_", " ")),
          h("span", { class: `chip ${SUPPORT_CLASS[c.support] ?? ""}` }, c.support.replaceAll("_", " "))),
        h("p", { class: "claim-text" }, c.text),
        c.verification_note ? h("div", { class: "verify" }, c.verification_note) : null,
        h("div", { class: "chips" },
          c.citation_ids.map((id) => cites[id] && citeChip(cites[id])),
          c.calculation_ids.map((k) => h("button", { type: "button", class: "chip info cite",
            onclick: () => { const el = document.getElementById(`calc-${k}`); el?.scrollIntoView({ behavior: "smooth", block: "center" });
              el?.classList.add("flash"); setTimeout(() => el?.classList.remove("flash"), 1600); } }, `ƒ ${k}`)))))));
  }

  if (art.calculations.length) {
    card.append(section(`Calculations (${art.calculations.length}) — executed in code, every input cited`,
      art.calculations.map((k) => h("div", { class: "calc", id: `calc-${k.id}` },
        h("div", { class: "calc-top" }, h("span", { class: "mono" }, k.id), h("span", { class: "calc-result" }, k.result.display)),
        h("div", { class: "formula" }, k.formula),
        k.inputs.length ? h("div", { class: "table-wrap" }, h("table", { class: "grid" },
          h("thead", {}, h("tr", {}, h("th", { text: "Input" }), h("th", { class: "num", text: "Value" }), h("th", { text: "Period" }), h("th", { text: "Source" }))),
          h("tbody", {}, k.inputs.map((i) => h("tr", {},
            h("td", {}, i.name), h("td", { class: "num mono" }, fmtValue(i.value, i.unit)), h("td", { class: "mono muted" }, i.period),
            h("td", {}, cites[i.citation_id] ? citeChip(cites[i.citation_id]) : i.citation_id)))))) : null,
        k.contributions ? h("div", { class: "table-wrap", style: "margin-top:8px" }, h("table", { class: "grid" },
          h("thead", {}, h("tr", {}, h("th", { text: "Line" }), h("th", { class: "num", text: "Share new" }), h("th", { class: "num", text: "Share old" }), h("th", { class: "num", text: "Δ margin (pp)" }))),
          h("tbody", {}, k.contributions.map((r) => h("tr", {},
            h("td", {}, r.line), h("td", { class: "num" }, `${(r.share_of_revenue_new * 100).toFixed(2)}%`),
            h("td", { class: "num" }, `${(r.share_of_revenue_old * 100).toFixed(2)}%`),
            h("td", { class: "num", style: `color:var(${Number(r.contribution_to_margin_change_pp) < 0 ? "--bad" : "--ok"})` },
              r.contribution_to_margin_change_pp)))))) : null,
        (k.notes || []).map((n) => h("div", { class: "muted", style: "font-size:12.5px;margin-top:4px" }, n))))));
  }

  const callouts = [
    ...art.conflicts.map((c) => h("div", { class: "callout warn" }, h("strong", {}, `Conflict · ${c.type?.replaceAll("_", " ")}`),
      `${c.fact}: ${Object.entries(c.values || {}).map(([k, v]) => `${k} = ${v}`).join("; ")}. ${c.resolution || ""}`)),
    ...art.definition_checks.map((d) => h("div", { class: "callout info" }, h("strong", {}, `Definition check · ${d.metric}`), d.finding)),
    ...art.abstentions.map((a) => h("div", { class: "callout info" }, h("strong", {}, "Abstention"), `${a.requirement}: ${a.reason}`)),
    ...art.security_flags.map((s) => h("div", { class: "callout bad" }, h("strong", {}, "Security flag"), JSON.stringify(s))),
    ...art.limitations.map((l) => h("div", { class: "callout" , style: "background:var(--surface-2)" }, h("strong", {}, "Limitation"), l)),
  ];
  if (callouts.length) card.append(section("Conflicts, definitions and limitations", callouts));

  const retrieval = art.trace?.retrieval?.[0];
  if (retrieval) {
    const cited = new Set(art.citations.map((c) => c.unit_id));
    const post = retrieval.results.filter(([u]) => isPostCutoff(u.split(":")[0])).length;
    card.append(section(`Retrieval trace — ${retrieval.strategy.toUpperCase()} top-${retrieval.k}, ${retrieval.filters ? "filtered" : "no filters"}`,
      post ? h("div", { class: "callout warn", style: "margin:0 0 10px" }, h("strong", {}, `${post} of ${retrieval.results.length} retrieved units were published after the ${state.asOf} cutoff`),
        "The baseline shows them to the generator anyway. Phase 4 adds the as-of filter that removes them.") : null,
      h("div", { class: "table-wrap" }, h("table", { class: "grid trace" },
        h("thead", {}, h("tr", {}, h("th", { class: "num", text: "#" }), h("th", { text: "Unit" }), h("th", { text: "Document" }), h("th", { text: "Published" }), h("th", { class: "num", text: "BM25" }), h("th", { text: "" }))),
        h("tbody", {}, retrieval.results.map(([unitId, sc], i) => {
          const docId = unitId.split(":")[0];
          const tr = h("tr", { class: `clickable ${isPostCutoff(docId) ? "post-cutoff" : ""}` },
            h("td", { class: "num" }, i + 1), h("td", { class: "mono" }, unitId.split(":").slice(2).join(":")),
            h("td", {}, docLabel(docId)), h("td", { class: "mono" }, fmtDate(state.docs[docId]?.published_at)),
            h("td", { class: "num mono" }, sc.toFixed(2)),
            h("td", {}, h("div", { class: "flags" }, cited.has(unitId) ? h("span", { class: "chip accent" }, "cited") : null,
              isPostCutoff(docId) ? h("span", { class: "chip warn" }, "post-cutoff") : null)));
          tr.addEventListener("click", () => inspect(unitId));
          return tr;
        }))))));
  }

  card.append(h("div", { class: "section versions" }, Object.entries(art.versions || {})
    .filter(([, v]) => v != null).map(([k, v]) => `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`).join(" · ")));
  $("#result").replaceChildren(card);
  if (ctx.navigate === false) return;
  if (location.hash !== "#/investigate") location.hash = "#/investigate";
  card.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---- inspector ----------------------------------------------------------------------------
function miniTable(table, selectedId) {
  const rows = [], cols = [], grid = {};
  for (const c of table.cells) {
    const r = (c.row_path || []).join(" › ") || "—";
    const col = c.col_header || "?";
    if (!rows.includes(r)) rows.push(r);
    if (!cols.includes(col)) cols.push(col);
    (grid[r] ||= {})[col] ||= c;
  }
  const shownRows = rows.slice(0, 40);
  return h("div", { class: "table-wrap" }, h("table", { class: "grid mini-table" },
    h("thead", {}, h("tr", {}, h("th", {}, ""), cols.map((c) => h("th", { class: "num" }, c)))),
    h("tbody", {}, shownRows.map((r) => h("tr", {}, h("th", { class: "rowh" }, r), cols.map((col) => {
      const c = grid[r][col];
      if (!c) return h("td", {});
      const td = h("td", { class: `num cell ${c.unit_id === selectedId ? "sel" : ""}`, title: c.unit_id }, c.raw_text);
      td.addEventListener("click", () => inspect(c.unit_id));
      return td;
    }))))),
    rows.length > shownRows.length ? h("div", { class: "muted", style: "padding:6px 8px" }, `${rows.length - shownRows.length} more rows`) : null);
}

async function inspect(unitId, fromBtn) {
  document.querySelectorAll(".cite.active").forEach((b) => b.classList.remove("active"));
  fromBtn?.classList.add("active");
  const box = $("#inspector");
  box.replaceChildren(h("div", { class: "empty" }, "Loading…"));
  let data;
  try { data = await api(`/api/units/${encodeURIComponent(unitId)}`); }
  catch (err) { box.replaceChildren(h("div", { class: "empty" }, err.message)); return; }
  const { unit: u, document: d } = data;
  const ix = u.ixbrl;
  const post = isPostCutoff(d.document_id);

  const head = h("div", { class: "insp-head" },
    h("div", { class: "chips" }, h("span", { class: "chip accent" }, u.kind),
      post ? h("span", { class: "chip warn" }, `published after ${state.asOf} cutoff`) : null,
      h("span", { class: "chip" }, d.role)),
    h("div", { class: "insp-title" }, `${d.form_type} ${d.fiscal_label}`),
    h("div", { class: "muted", style: "font-size:12.5px" }, `Published ${d.published_at} · accession ${d.accession}`),
    h("div", { class: "mono muted" }, u.unit_id));

  const kv = (pairs) => h("dl", { class: "kv" }, pairs.filter(([, v]) => v != null && v !== "").map(([k, v]) => [h("dt", {}, k), h("dd", {}, v)]));
  const body = h("div", { class: "inspector-body" });

  if (u.kind === "cell") {
    body.append(h("div", { class: "section" },
      h("div", { class: "big-value" }, u.raw_text),
      h("div", { class: "muted", style: "margin-bottom:10px" }, [u.scale_hint && `in ${u.scale_hint}`, u.negative_display && "shown as negative"].filter(Boolean).join(" · ")),
      kv([["Row", u.row_path.join(" › ")], ["Column", u.col_header], ["Table", data.table?.caption], ["Section", u.section],
        ["Page", u.printed_page ? `${u.printed_page} (HTML page ${u.html_page})` : `HTML page ${u.html_page}`],
        ...(ix ? [["XBRL concept", ix.concept], ["Period", ix.period.instant || `${ix.period.start} → ${ix.period.end}`],
          ["Dimensions", Object.values(ix.dims || {}).map((m) => m.split(":").pop()).join(", ") || "none (consolidated)"],
          ["XBRL value", ix.value != null ? fmtValue(ix.value, (ix.unit || "").toUpperCase()) : null],
          ["Decimals / sign", `${ix.decimals ?? "—"} / ${ix.sign || "+"}`]] : [["XBRL", "not tagged"]])])));
  } else {
    body.append(h("div", { class: "section" }, kv([["Section", u.section], ["Heading", u.caption || u.heading],
      ["Page", u.printed_page ? `${u.printed_page} (HTML page ${u.html_page})` : `HTML page ${u.html_page}`]])));
    if (u.kind === "passage" && data.paragraphs) {
      body.append(section("Text", data.paragraphs.map((p) => h("p", { class: "quote", style: "margin-bottom:6px" }, p.text))));
    } else if (u.kind !== "table") {
      body.append(section("Text", h("p", { class: "quote" }, u.text)));
    }
  }
  if (data.table) body.append(section(`Table · ${data.table.cells.length} cells`, miniTable(data.table, u.unit_id)));

  const els = [ix?.element_id, u.dom_anchor].filter(Boolean);
  const target = els[0];
  if (target) {
    const src = `/source/${encodeURIComponent(d.document_id)}?el=${encodeURIComponent(els.join(","))}#${encodeURIComponent(target)}`;
    const frameSlot = h("div");
    body.append(section("Original filing",
      h("div", { class: "chips", style: "margin-bottom:8px" },
        h("button", { type: "button", class: "btn", onclick: () => frameSlot.replaceChildren(
          h("iframe", { class: "source", src, sandbox: "", referrerpolicy: "no-referrer", title: `Original ${d.form_type} ${d.fiscal_label}` })) },
          "Show at this location"),
        h("a", { class: "btn", href: src, target: "_blank", rel: "noopener noreferrer", style: "text-decoration:none" }, "Open in new tab"),
        h("a", { class: "btn", href: d.origin_url, target: "_blank", rel: "noopener noreferrer", style: "text-decoration:none" }, "SEC EDGAR")),
      frameSlot,
      h("div", { class: "muted", style: "font-size:12px;margin-top:6px" }, `Stored copy, sha256 ${d.sha256.slice(0, 16)}… — rendered with scripts and external loads blocked.`)));
  }
  box.replaceChildren(head, body);
}

// ---- benchmark ----------------------------------------------------------------------------
async function renderBenchmark() {
  const view = $("#view-benchmark");
  view.replaceChildren(h("div", { class: "muted" }, "Loading reports…"));
  state.reports = await api("/api/reports");
  if (!state.reports.length) {
    view.replaceChildren(h("div", { class: "card empty" }, "No benchmark runs yet. Run: python -m bench.run_b0 --generator extractive"));
    return;
  }
  let current = store.get("reportGen", state.reports[0].generator);
  if (!state.reports.some((r) => r.generator === current)) current = state.reports[0].generator;

  const draw = () => {
    const rep = state.reports.find((r) => r.generator === current);
    const tabs = h("div", { class: "tabs" }, state.reports.map((r) => h("a", {
      href: "#/benchmark", class: r.generator === current ? "active" : "",
      onclick: (e) => { e.preventDefault(); current = r.generator; store.set("reportGen", current); draw(); } }, r.generator)));
    const fails = {};
    rep.rows.forEach((r) => new Set(r.failures.map((f) => f.split(":")[0])).forEach((k) => { fails[k] = (fails[k] || 0) + 1; }));
    view.replaceChildren(
      h("div", { class: "page-head" },
        h("div", {}, h("h1", {}, "Benchmark — baseline B0"),
          h("p", {}, `Run ${rep.run_id} · ${rep.rows.length} dev questions (20 Core + 7 Frontier). Every metric is measured separately; click a question to open its artifact.`)),
        tabs),
      h("div", { class: "metrics" }, rep.metrics.map(([k, v]) => {
        const p = ratioParts(v);
        return h("div", { class: "card metric" }, h("div", { class: "k" }, k), h("div", { class: "v" }, v.replace(/\s*\(.*\)/, "")),
          p ? h("div", { class: "bar" }, h("span", { style: `width:${p[1] ? (100 * p[0]) / p[1] : 0}%` })) : null);
      })),
      h("div", { class: "card", style: "margin-bottom:16px" }, section("Failure categories (questions affected)",
        h("div", { class: "chips" }, Object.entries(fails).sort((a, b) => b[1] - a[1]).map(([k, n]) =>
          h("span", { class: "chip bad" }, `${FAILURE_LABELS[k] || k} · ${n}`))))),
      h("div", { class: "card table-wrap" }, h("table", { class: "grid" },
        h("thead", {}, h("tr", {}, ["Q", "Question", "Outcome", "Evidence @8", "Values", "Checks", "Failures"].map((t) => h("th", { text: t })))),
        h("tbody", {}, rep.rows.map((r) => {
          const q = state.qById[r.id];
          const tr = h("tr", { class: "clickable" },
            h("td", { class: "mono" }, r.id),
            h("td", {}, q?.question || "", h("div", { class: "chips", style: "margin-top:4px" }, r.category.map((c) => h("span", { class: "chip" }, c)))),
            h("td", {}, h("span", { class: `chip ${r.outcome_ok ? "ok" : "bad"}` }, r.outcome)),
            h("td", { class: "mono" }, `${r.req_hit_at_k}/${r.requirements}`),
            h("td", { class: "mono" }, `${r.values_correct}/${r.values_expected}`),
            h("td", { class: "mono" }, `${r.checks_passed}/${r.checks_expected}`),
            h("td", {}, h("div", { class: "chips" }, r.failures.slice(0, 3).map(failureChip),
              r.failures.length > 3 ? h("span", { class: "chip" }, `+${r.failures.length - 3}`) : null,
              !r.failures.length ? h("span", { class: "chip ok" }, "passed") : null)));
          tr.addEventListener("click", async () => {
            try {
              const art = await api(`/api/runs/${rep.run_id}/artifacts/b0_${rep.generator}_${r.id}`);
              renderArtifact(art, { score: r, source: `Benchmark run ${rep.run_id}`, asOf: q?.as_of || null });
            } catch (err) { toast(err.message); }
          });
          return tr;
        })))));
  };
  draw();
}

// ---- gold & corpus ------------------------------------------------------------------------
async function renderGold() {
  const view = $("#view-gold");
  const gold = await api("/api/gold");
  view.replaceChildren(
    h("div", { class: "page-head" }, h("div", {}, h("h1", {}, "Gold answers"),
      h("p", {}, "Hand-written reference artifacts. Claims and support judgements are written by hand; every number is computed in code from cited cells. They show what a complete answer looks like."))),
    h("div", { class: "gold-list" }, gold.map((g) => h("button", { type: "button", class: "card gold-card", onclick: async () => {
      try { const art = await api(`/api/artifacts/${g.artifact_id}`); renderArtifact(art, { source: "Gold answer (hand-written)" }); }
      catch (err) { toast(err.message); }
    } }, h("span", { class: "chip accent" }, g.artifact_id), h("p", { class: "q" }, g.question)))));
}

function renderCorpus() {
  const view = $("#view-corpus");
  view.replaceChildren(
    h("div", { class: "page-head" }, h("div", {}, h("h1", {}, "Corpus"),
      h("p", {}, "Immutable, content-addressed source versions. 'trap' documents are deliberately included to test temporal and definition handling."))),
    h("div", { class: "card table-wrap" }, h("table", { class: "grid" },
      h("thead", {}, h("tr", {}, ["Document", "Form", "Period", "Published (UTC)", "Role", "Evidence units", "iXBRL linked", "Source"].map((t) => h("th", { text: t })))),
      h("tbody", {}, Object.values(state.docs).map((d) => h("tr", {},
        h("td", { class: "mono" }, d.document_id),
        h("td", {}, `${d.form_type}`, h("div", { class: "muted" }, d.fiscal_label)),
        h("td", { class: "mono" }, d.period_end),
        h("td", { class: "mono" }, d.published_at.replace("T", " ").slice(0, 16)),
        h("td", {}, h("span", { class: `chip ${d.role === "trap" ? "warn" : "accent"}` }, d.role)),
        h("td", { class: "mono" }, d.units ? Object.entries(d.units).map(([k, v]) => `${v} ${k}`).join(" · ") : "—"),
        h("td", { class: "mono" }, d.ixbrl_total ? `${d.ixbrl_linked}/${d.ixbrl_total}` : "not iXBRL"),
        h("td", {}, h("a", { href: `/source/${d.document_id}`, target: "_blank", rel: "noopener noreferrer" }, "stored copy"), " · ",
          h("a", { href: d.origin_url, target: "_blank", rel: "noopener noreferrer" }, "EDGAR"))))))));
}

// ---- routing & init -----------------------------------------------------------------------
const rendered = new Set();
const RENDER = { benchmark: renderBenchmark, gold: renderGold, corpus: renderCorpus };

async function openArtifactLink(artifactId, unitId) {
  try {
    const art = await api(`/api/artifacts/${encodeURIComponent(artifactId)}`);
    // Benchmark run artifacts (b0_<generator>_<item>) open with their score from the latest report.
    let score = null;
    const m = /^b0_(\w+?)_([qh]\d+)$/.exec(artifactId);
    if (m) {
      const report = (await api("/api/reports")).find((r) => r.generator === m[1]);
      score = report?.rows.find((r) => r.id === m[2]) || null;
    }
    renderArtifact(art, { source: score ? "Benchmark run (opened from link)" : "Opened from link", score, navigate: false });
    if (unitId) await inspect(unitId);
  } catch (err) {
    toast(`Could not open ${artifactId}: ${err.message}`);
  }
}

function route() {
  // Shareable links: #/artifact/<artifact id> or #/artifact/<artifact id>/<evidence unit id>
  const deep = location.hash.match(/^#\/artifact\/([A-Za-z0-9_.:-]+)(?:\/(.+))?$/);
  const view = deep ? "investigate" : (location.hash.match(/^#\/(\w+)/) || [, "investigate"])[1];
  document.querySelectorAll(".view").forEach((v) => { v.hidden = v.id !== `view-${view}`; });
  document.querySelectorAll(".tabs a[data-view]").forEach((a) => a.classList.toggle("active", a.dataset.view === view));
  if (RENDER[view] && !rendered.has(view)) {
    rendered.add(view);
    Promise.resolve().then(RENDER[view]).catch((err) => toast(err.message));
  }
  if (deep) openArtifactLink(deep[1], deep[2] && decodeURIComponent(deep[2]));
}

async function init() {
  try {
    const [status, questions, docs] = await Promise.all([api("/api/status"), api("/api/questions"), api("/api/documents")]);
    state.status = status;
    state.questions = questions;
    state.qById = Object.fromEntries(questions.map((q) => [q.id, q]));
    state.docs = Object.fromEntries(docs.map((d) => [d.document_id, d]));
    renderStatus();
    renderGenerators();
    renderBenchSelect();
  } catch (err) {
    toast(`Could not reach the server: ${err.message}`);
  }
  $("#composer").addEventListener("submit", submitInvestigation);
  window.addEventListener("hashchange", route);
  route();
}

init();
