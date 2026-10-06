(async function () {
  const { el, api, store, LEVEL_COLOR, CAT_NAMES, chart } = window.PRA;
  const stats = await api("/dashboard/stats"), syn = stats.synthetic;
  const mine = store.load("pra_result"), sim = store.load("pra_sim");
  document.getElementById("source").textContent = mine
    ? "Showing YOUR latest assessment (this browser session) next to synthetic population data."
    : "No assessment yet - showing the synthetic population average. Start an assessment to see your own numbers.";
  const level = mine ? mine.risk_level : classify(syn.avg_score);
  function classify(s) { return s <= 20 ? "LOW" : s <= 40 ? "MODERATE" : s <= 70 ? "HIGH" : "CRITICAL"; }
  const score = mine ? mine.overall_score : Math.round(syn.avg_score);
  const catScores = mine ? mine.category_scores : syn.avg_category_scores;
  const high = Object.entries(catScores).filter(([, v]) => v >= 60).map(([k]) => CAT_NAMES[k]);
  const card = (title, value, extra) => el("div", { class: "card" }, el("div", { class: "muted" }, title), el("div", { class: "big" }, value), extra || "");
  const cards = document.getElementById("cards");
  cards.append(card("Overall risk score", score + "/100"),
    card("Risk level", "", el("span", { class: "badge " + level }, level)),
    card("High-risk categories", high.length, el("div", { class: "muted" }, high.join(", ") || "none")),
    card("Recommendations", mine ? mine.recommendations.length : "-", el("div", { class: "muted" }, mine ? "from your assessment" : "complete an assessment")),
    card("Security controls enabled", Math.round(syn.account_controls.reduce((a, c) => a + c.percent, 0) / syn.account_controls.length) + "%", el("div", { class: "muted" }, "avg across synthetic profiles")));

  const keys = Object.keys(catScores), color = v => v > 70 ? LEVEL_COLOR.CRITICAL : v > 40 ? LEVEL_COLOR.HIGH : v > 20 ? LEVEL_COLOR.MODERATE : LEVEL_COLOR.LOW;
  const hbar = (id, labels, data, colors) => chart(document.getElementById(id), { type: "bar",
    data: { labels, datasets: [{ data, backgroundColor: colors || "#1f4e79" }] },
    options: { maintainAspectRatio: false, indexAxis: "y", scales: { x: { min: 0, max: 100 } }, plugins: { legend: { display: false } } } });
  hbar("c-cat", keys.map(k => CAT_NAMES[k]), keys.map(k => catScores[k]), keys.map(k => color(catScores[k])));
  const lv = ["LOW", "MODERATE", "HIGH", "CRITICAL"];
  chart(document.getElementById("c-dist"), { type: "doughnut", data: { labels: lv,
    datasets: [{ data: lv.map(l => syn.level_distribution[l] || 0), backgroundColor: lv.map(l => LEVEL_COLOR[l]) }] }, options: { maintainAspectRatio: false } });
  hbar("c-weak", syn.top_weaknesses.map(w => w.label), syn.top_weaknesses.map(w => w.percent), LEVEL_COLOR.HIGH);
  hbar("c-acct", syn.account_controls.map(c => c.label), syn.account_controls.map(c => c.percent), LEVEL_COLOR.LOW);
  hbar("c-foot", syn.footprint_controls.map(c => c.label), syn.footprint_controls.map(c => c.percent), "#1f4e79");
  const labels = ["Synthetic average"], before = [syn.improvement.avg_before], after = [syn.improvement.avg_after];
  if (sim) { labels.push("Your simulation"); before.push(sim.before); after.push(sim.after); }
  chart(document.getElementById("c-imp"), { type: "bar", data: { labels, datasets: [
    { label: "Current", data: before, backgroundColor: LEVEL_COLOR.CRITICAL }, { label: "After improvements", data: after, backgroundColor: LEVEL_COLOR.LOW }] },
    options: { maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } } } });
  document.getElementById("imp-note").textContent = "Synthetic average assumes these fixes: " + syn.improvement.fixes.join(", ") + ". Framework simulation, not a guarantee.";
})();
