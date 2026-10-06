/* Shared helpers. All dynamic text goes through textContent / createTextNode => no XSS via innerHTML. */
window.PRA = (function () {
  function el(tag, props, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(props || {})) {
      if (k === "class") n.className = v;
      else if (k === "style") Object.assign(n.style, v);
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    }
    kids.flat().forEach(c => { if (c !== null && c !== undefined) n.append(c instanceof Node ? c : document.createTextNode(String(c))); });
    return n;
  }
  async function api(path, opts) {
    const init = opts && opts.body !== undefined
      ? { method: opts.method || "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(opts.body) }
      : (opts || {});
    const res = await fetch("/api" + path, init);
    const data = await res.json();
    if (!res.ok) throw new Error((data.details || [data.message || data.error]).join("; "));
    return data;
  }
  const store = {
    save(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* ignore */ } },
    load(k) { try { return JSON.parse(sessionStorage.getItem(k)); } catch (e) { return null; } },
    clear(k) { sessionStorage.removeItem(k); }
  };
  const LEVEL_COLOR = { LOW: "#1e8449", MODERATE: "#b7950b", HIGH: "#d35400", CRITICAL: "#c0392b" };
  const CAT_NAMES = { profile: "Profile", personal: "Personal Info", location: "Location", content: "Content",
    connections: "Connections", tagging: "Tagging", account: "Account Security", apps: "Third-Party Apps",
    social_eng: "Social Engineering", footprint: "Digital Footprint" };
  const nice = s => s.replace(/_/g, " ").toLowerCase().replace(/^./, c => c.toUpperCase());
  function chart(canvas, config) {
    if (typeof Chart === "undefined") { canvas.replaceWith(el("p", { class: "muted" }, "Chart library not loaded (needs internet for Chart.js CDN).")); return null; }
    return new Chart(canvas, config);
  }
  return { el, api, store, LEVEL_COLOR, CAT_NAMES, nice, chart };
})();
