const DATA_URL = "/data/lists.json";

const els = {
  stats: document.getElementById("stats"),
  search: document.getElementById("q"),
  chips: document.getElementById("category-filters"),
  meta: document.getElementById("result-meta"),
  results: document.getElementById("results"),
  error: document.getElementById("error"),
};

/** @type {{ lists: object[], categories: string[], query: string, category: string }} */
const state = {
  lists: [],
  categories: [],
  query: "",
  category: "",
};

function formatStars(count, approx) {
  if (typeof count === "number" && Number.isFinite(count)) {
    if (count >= 1000) {
      const value = count / 1000;
      const digits = count >= 10000 ? 0 : 1;
      return `${value.toFixed(digits).replace(/\.0$/, "")}k`;
    }
    return String(count);
  }
  return approx || "—";
}

function uniqueCategories(lists) {
  const counts = new Map();
  for (const list of lists) {
    const name = list.category || "Uncategorized";
    counts.set(name, (counts.get(name) || 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

function haystack(list) {
  return [
    list.name,
    list.description,
    list.editorial_notes,
    list.maintainer,
    list.subcategory,
    ...(list.tags || []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function matches(list, query, category) {
  if (category && list.category !== category) return false;
  if (!query) return true;
  return haystack(list).includes(query);
}

function parseParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    query: (params.get("q") || "").trim(),
    category: params.get("category") || "",
  };
}

function writeParams() {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.category) params.set("category", state.category);
  const next = params.toString();
  const url = next ? `?${next}` : window.location.pathname;
  history.replaceState(null, "", url);
}

function renderChips() {
  const counts = uniqueCategories(state.lists);
  state.categories = counts.map(([name]) => name);
  const total = state.lists.length;
  const allPressed = state.category === "";
  const buttons = [
    `<button type="button" class="chip" data-category="" aria-pressed="${allPressed}">All (${total})</button>`,
    ...counts.map(
      ([name, count]) =>
        `<button type="button" class="chip" data-category="${escapeAttr(name)}" aria-pressed="${
          state.category === name
        }">${escapeHtml(name)} (${count})</button>`
    ),
  ];
  els.chips.innerHTML = buttons.join("");
}

function render() {
  const query = state.query.toLowerCase();
  const filtered = state.lists
    .filter((list) => matches(list, query, state.category))
    .sort((a, b) => (b.stars_count || 0) - (a.stars_count || 0));

  els.meta.textContent =
    filtered.length === state.lists.length
      ? `Showing all ${filtered.length} lists`
      : `Showing ${filtered.length} of ${state.lists.length} lists`;

  if (filtered.length === 0) {
    els.results.innerHTML = `<li class="empty">No lists match that search.</li>`;
    return;
  }

  els.results.innerHTML = filtered.map(cardHtml).join("");
}

function cardHtml(list) {
  const stars = formatStars(list.stars_count, list.stars_approx);
  const tags = (list.tags || [])
    .slice(0, 6)
    .map((tag) => `<li>${escapeHtml(tag)}</li>`)
    .join("");
  const notes = list.editorial_notes
    ? `<button type="button" class="toggle-notes" aria-expanded="false" data-id="${escapeAttr(
        list.id
      )}">Editorial note</button>
       <p class="notes" id="notes-${escapeAttr(list.id)}" hidden>${escapeHtml(
          list.editorial_notes
        )}</p>`
    : "";
  const subcategory = list.subcategory
    ? `<span>${escapeHtml(list.subcategory)}</span>`
    : "";
  return `<li class="card">
    <div class="card-top">
      <h2><a href="${escapeAttr(list.github_url)}" rel="noopener noreferrer">${escapeHtml(
        list.name
      )}</a></h2>
      <span class="stars" title="GitHub stars">★ ${escapeHtml(stars)}</span>
    </div>
    <div class="meta">
      <span class="category-label">${escapeHtml(list.category || "")}</span>
      ${subcategory}
      <span>@${escapeHtml(list.maintainer || "")}</span>
    </div>
    <p class="description">${escapeHtml(list.description || "")}</p>
    ${tags ? `<ul class="tags">${tags}</ul>` : ""}
    ${notes}
  </li>`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}

function bindEvents() {
  els.search.addEventListener("input", () => {
    state.query = els.search.value.trim();
    writeParams();
    render();
  });

  els.chips.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) return;
    state.category = button.getAttribute("data-category") || "";
    writeParams();
    renderChips();
    render();
  });

  els.results.addEventListener("click", (event) => {
    const button = event.target.closest(".toggle-notes");
    if (!button) return;
    const notes = document.getElementById(`notes-${button.dataset.id}`);
    if (!notes) return;
    const open = notes.hidden;
    notes.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    button.textContent = open ? "Hide editorial note" : "Editorial note";
  });
}

async function init() {
  const params = parseParams();
  state.query = params.query;
  state.category = params.category;
  els.search.value = state.query;
  bindEvents();

  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) {
      throw new Error(`Could not load catalog (${response.status})`);
    }
    const lists = await response.json();
    if (!Array.isArray(lists)) {
      throw new Error("Catalog data is not a list");
    }
    state.lists = lists;
    const categories = uniqueCategories(lists).length;
    els.stats.textContent = `${lists.length} lists · ${categories} categories`;
    renderChips();
    render();
  } catch (error) {
    els.error.hidden = false;
    els.error.textContent =
      error instanceof Error ? error.message : "Could not load the catalog.";
    els.stats.textContent = "Catalog unavailable";
    els.meta.textContent = "";
  }
}

init();
