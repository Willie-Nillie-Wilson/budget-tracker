"use strict";

// Color per category (dots + bars). Falls back to a neutral accent.
const CAT_COLORS = {
  Food: "#e8b04b",
  Transport: "#6fb1fc",
  Shopping: "#e07ac0",
  Bills: "#7c9ff0",
  Entertainment: "#c08bf0",
  Health: "#5fd0a0",
  Other: "#9aa7a0",
  Uncategorized: "#6b7a73",
};

let AVAILABLE_CATEGORIES = [];

const $ = (id) => document.getElementById(id);
const money = (n) =>
  "$" + Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const colorFor = (name) => CAT_COLORS[name] || "#9aa7a0";

// Tiny DOM builder: safe by construction (text goes through textContent).
function el(tag, opts = {}, kids = []) {
  const node = document.createElement(tag);
  if (opts.class) node.className = opts.class;
  if (opts.text != null) node.textContent = opts.text;
  if (opts.style) Object.assign(node.style, opts.style);
  if (opts.attrs) for (const [k, v] of Object.entries(opts.attrs)) node.setAttribute(k, v);
  for (const kid of kids) if (kid) node.appendChild(kid);
  return node;
}

// ---------- Rendering ----------
function renderPeriod() {
  const now = new Date();
  $("period").textContent = now.toLocaleString(undefined, { month: "long", year: "numeric" });
}

function animateTotal(target) {
  const node = $("total");
  const start = performance.now();
  const dur = 700;
  function frame(t) {
    const p = Math.min((t - start) / dur, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    node.textContent = money(target * eased);
    if (p < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function renderCategories(categories, total) {
  const list = $("category-list");
  list.replaceChildren();

  if (!categories.length) {
    $("categories-empty").hidden = false;
    return;
  }
  $("categories-empty").hidden = true;

  categories.forEach((cat, i) => {
    const pct = total > 0 ? (cat.amount / total) * 100 : 0;
    const row = el("li", {
      class: "cat-row",
      style: { animationDelay: `${i * 0.05}s` },
    });
    row.style.setProperty("--cat", colorFor(cat.name));
    row.style.setProperty("--pct", pct.toFixed(1) + "%");

    const name = el("span", { class: "cat-row__name" }, [
      el("span", { class: "cat-row__dot" }),
      document.createTextNode(cat.name),
    ]);
    const top = el("div", { class: "cat-row__top" }, [
      name,
      el("span", { class: "cat-row__amount", text: money(cat.amount) }),
    ]);

    row.append(
      el("div", { class: "cat-row__bar" }),
      top,
      el("div", { class: "cat-row__pct", text: `${pct.toFixed(0)}% of spend` })
    );
    list.appendChild(row);
  });
}

function buildSelect(selected, id) {
  const sel = el("select", { class: "recent-row__select", attrs: { "data-id": id } });
  AVAILABLE_CATEGORIES.forEach((c) => {
    const opt = el("option", { text: c, attrs: { value: c } });
    if (c === selected) opt.selected = true;
    sel.appendChild(opt);
  });
  sel.addEventListener("change", (e) => fixCategory(id, e.target.value));
  return sel;
}

function renderRecent(recent, newId) {
  const list = $("recent-list");
  list.replaceChildren();

  if (!recent.length) {
    $("recent-empty").hidden = false;
    return;
  }
  $("recent-empty").hidden = true;

  recent.forEach((tx, i) => {
    const note = el("div", {
      class: "recent-row__note" + (tx.note ? "" : " is-empty"),
      text: tx.note || "no note",
    });
    const catWrap = el("div", { class: "recent-row__cat" }, [buildSelect(tx.category, tx.id)]);
    const main = el("div", { class: "recent-row__main" }, [note, catWrap]);
    const amount = el("div", { class: "recent-row__amount", text: money(tx.amount) });

    const row = el(
      "li",
      {
        class: "recent-row" + (tx.id === newId ? " is-new" : ""),
        style: { animationDelay: `${i * 0.04}s` },
      },
      [main, amount]
    );
    list.appendChild(row);
  });
}

// ---------- Data ----------
async function loadSummary(newId) {
  const res = await fetch("/api/summary");
  const data = await res.json();
  AVAILABLE_CATEGORIES = data.available_categories || [];
  animateTotal(data.total);
  renderCategories(data.categories, data.total);
  renderRecent(data.recent, newId);
}

async function logTransaction(text) {
  const res = await fetch("/api/log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return { ok: res.ok, body: await res.json() };
}

async function fixCategory(id, category) {
  await fetch(`/api/transaction/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ category }),
  });
  await loadSummary();
  showToast("Moved to ", category);
}

// ---------- UI helpers ----------
let toastTimer;
function showToast(label, accent) {
  const t = $("toast");
  t.replaceChildren(document.createTextNode(label));
  if (accent != null) t.appendChild(el("strong", { text: accent }));
  t.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("is-visible"), 2600);
}

function setHint(text, isError) {
  const hint = $("log-hint");
  hint.textContent = text;
  hint.classList.toggle("is-error", !!isError);
}

// ---------- Wire up ----------
$("log-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("log-input");
  const text = input.value.trim();
  if (!text) return;

  const { ok, body } = await logTransaction(text);
  if (!ok) {
    setHint(body.error || "Could not log that.", true);
    return;
  }

  input.value = "";
  setHint("Type what you spent, then the amount.", false);
  await loadSummary(body.id);
  showToast(`Added ${money(body.amount)} to `, body.category);
});

renderPeriod();
loadSummary();
