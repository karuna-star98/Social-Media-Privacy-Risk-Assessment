(async function () {
  const { el, api } = window.PRA;
  const data = await api("/privacy-checklist");
  const ul = document.getElementById("checklist");
  data.items.forEach(i => ul.append(el("li", {}, "\u25A1 " + i)));
  document.getElementById("print").addEventListener("click", () => window.print());
})();
