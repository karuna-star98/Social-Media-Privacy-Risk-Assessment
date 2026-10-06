(async function () {
  const { el, api, store, LEVEL_COLOR, CAT_NAMES, nice, chart } = window.PRA;
  const $ = id => document.getElementById(id);
  const quiz = await api("/questionnaire");
  let current = null;

  // ---- render questionnaire ----
  quiz.categories.forEach(cat => {
    const box = el("div", { class: "card" }, el("h3", {}, `Category ${cat.letter}: ${cat.name}`));
    cat.questions.forEach(q => {
      const opts = el("div", { class: "opts" });
      q.options.forEach(o => opts.append(el("label", {}, el("input", { type: "radio", name: q.id, value: o }), " " + nice(o))));
      box.append(el("div", { class: "q", id: "q-" + q.id }, el("div", {}, q.text), opts));
    });
    $("questions").append(box);
  });
  const answers = () => Object.fromEntries(quiz.categories.flatMap(c => c.questions).map(q => {
    const r = document.querySelector(`input[name="${q.id}"]:checked`); return [q.id, r ? r.value : null]; }));
  function progress() {
    const done = Object.values(answers()).filter(Boolean).length;
    $("progress").style.width = (100 * done / quiz.total_questions) + "%";
    $("progress-text").textContent = `${done} / ${quiz.total_questions} answered`;
  }
  $("questions").addEventListener("change", progress); progress();

  $("demo").addEventListener("click", async () => {
    const demo = await api("/demo-profile");
    Object.entries(demo.answers).forEach(([id, v]) => { const r = document.querySelector(`input[name="${id}"][value="${v}"]`); if (r) r.checked = true; });
    progress();
  });

  // ---- submit ----
  $("submit").addEventListener("click", async () => {
    const a = answers(), missing = Object.keys(a).filter(k => !a[k]);
    document.querySelectorAll(".q").forEach(n => n.classList.remove("missing"));
    if (missing.length) {
      missing.forEach(id => $("q-" + id).classList.add("missing"));
      $("error").textContent = `Please answer all questions (${missing.length} left).`; $("error").classList.remove("hidden");
      $("q-" + missing[0]).scrollIntoView({ behavior: "smooth", block: "center" }); return;
    }
    $("error").classList.add("hidden");
    try {
      current = await api("/assessment", { body: { answers: a } });
      store.save("pra_answers", a); store.save("pra_result", current); store.clear("pra_sim");
      showResults(current);
    } catch (err) { $("error").textContent = err.message; $("error").classList.remove("hidden"); }
  });

  function showResults(r) {
    $("form-section").classList.add("hidden"); $("results").classList.remove("hidden"); window.scrollTo(0, 0);
    $("score").textContent = r.overall_score + "/100";
    $("level").textContent = r.risk_level; $("level").className = "badge " + r.risk_level;
    $("assessment-id").textContent = `ID ${r.assessment_id} - ${r.created_at}`;
    $("disclaimer").textContent = r.disclaimer;
    const hc = $("high-cats"); hc.replaceChildren();
    (r.high_risk_categories.length ? r.high_risk_categories : ["None - no category at or above 60"]).forEach(c => hc.append(el("li", {}, c)));
    $("report-view").href = `/api/assessment/${r.assessment_id}/report`;
    $("report-dl").href = `/api/assessment/${r.assessment_id}/report?download=1`;
    const keys = Object.keys(r.category_scores), labels = keys.map(k => CAT_NAMES[k]), vals = keys.map(k => r.category_scores[k]);
    chart($("radar"), { type: "radar", data: { labels, datasets: [{ label: "Risk (higher = worse)", data: vals,
      backgroundColor: "rgba(192,57,43,.25)", borderColor: "#c0392b" }] }, options: { maintainAspectRatio: false, scales: { r: { min: 0, max: 100 } } } });
    chart($("bars"), { type: "bar", data: { labels, datasets: [{ label: "Risk score", data: vals,
      backgroundColor: vals.map(v => v > 70 ? LEVEL_COLOR.CRITICAL : v > 40 ? LEVEL_COLOR.HIGH : v > 20 ? LEVEL_COLOR.MODERATE : LEVEL_COLOR.LOW) }] },
      options: { maintainAspectRatio: false, indexAxis: "y", scales: { x: { min: 0, max: 100 } }, plugins: { legend: { display: false } } } });
    const fl = $("findings"); fl.replaceChildren();
    if (!r.findings.length) fl.append(el("li", {}, "No significant findings - nice work!"));
    r.findings.slice(0, 10).forEach(f => fl.append(el("li", {}, el("b", {}, f.severity + ": "), f.description)));
    const rc = $("recs"); rc.replaceChildren();
    r.recommendations.forEach(x => rc.append(el("p", {}, el("span", { class: "tag p-" + x.priority.split(" ")[0] }, x.priority), x.recommendation)));
    loadSimulator();
  }

  // ---- simulator ----
  async function loadSimulator() {
    const box = $("sim-options"); if (box.childElementCount) return;
    (await api("/improvement-options")).options.forEach(o =>
      box.append(el("label", {}, el("input", { type: "checkbox", value: o.key }), " " + o.label)));
  }
  $("simulate").addEventListener("click", async () => {
    const changes = [...document.querySelectorAll("#sim-options input:checked")].map(i => i.value);
    if (!changes.length) { alert("Tick at least one improvement."); return; }
    const sim = await api("/assessment/simulate-improvement", { body: { answers: store.load("pra_answers"), changes } });
    $("sim-before").textContent = sim.before.overall_score; $("sim-after").textContent = sim.after.overall_score;
    $("sim-delta").textContent = "-" + sim.risk_reduction + " pts";
    [["sim-before-level", sim.before.risk_level], ["sim-after-level", sim.after.risk_level]].forEach(([id, l]) => { $(id).textContent = l; $(id).className = "badge " + l; });
    $("sim-disclaimer").textContent = sim.disclaimer; $("sim-result").classList.remove("hidden");
    store.save("pra_sim", { before: sim.before.overall_score, after: sim.after.overall_score });
  });

  $("delete").addEventListener("click", async () => {
    if (!current || !confirm("Delete the stored scores for this assessment?")) return;
    await api(`/assessment/${current.assessment_id}`, { method: "DELETE" });
    store.clear("pra_result"); store.clear("pra_answers"); alert("Deleted."); location.reload();
  });
})();
