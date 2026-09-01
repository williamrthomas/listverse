import {
  asOfDate,
  categoryCountsForSearch,
  emptyActions,
  emptyMessage,
  escapeAttr,
  escapeHtml,
  matches,
  normalizeCatalog,
  parseParams,
  resultLine,
  serializeParams,
  sortLists,
  toggleValue,
  uniqueCategories,
} from "./catalog.mjs";

const DATA_URL = "/data/lists.json";

const els = {
  stats: document.getElementById("stats"),
  search: document.getElementById("q"),
  chips: document.getElementById("category-filters"),
  filters: document.getElementById("active-filters"),
  meta: document.getElementById("result-meta"),
  sort: document.getElementById("sort"),
  results: document.getElementById("results"),
  error: document.getElementById("error"),
  asOf: document.getElementById("as-of"),
};

/** @type {{ lists: object[], categories: string[], query: string, category: string, subcategory: string, tags: string[], sort: "stars" | "name", generatedAt: string | null }} */
const state = {
  lists: [],
  categories: [],
  query: "",
  category: "",
  subcategory: "",
  tags: [],
  sort: "stars",
  generatedAt: null,
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

function writeParams() {
  const next = serializeParams(state);
  const url = next ? `?${next}` : window.location.pathname;
  history.replaceState(null, "", url);
}

function applyParams(search = window.location.search) {
  const params = parseParams(search);
  state.query = params.query;
  state.category = params.category;
  state.subcategory = params.subcategory;
  state.tags = params.tags;
  state.sort = params.sort;
  els.search.value = state.query;
}

function starTitle() {
  const date = asOfDate(state.generatedAt);
  return date ? `GitHub stars as of ${date}` : "GitHub stars";
}

function renderChips() {
  const order = uniqueCategories(state.lists);
  state.categories = order.map(([name]) => name);
  const { total, counts } = categoryCountsForSearch(state.lists, state.query);
  const scrollLeft = els.chips.scrollLeft;
  const allPressed = state.category === "";
  const allZero = total === 0 ? " is-zero" : "";
  const buttons = [
    `<button type="button" class="chip${allZero}" data-category="" aria-pressed="${allPressed}">All (${total})</button>`,
    ...order.map(([name]) => {
      const count = counts.get(name) || 0;
      const zero = count === 0 ? " is-zero" : "";
      return `<button type="button" class="chip${zero}" data-category="${escapeAttr(
        name
      )}" aria-pressed="${state.category === name}">${escapeHtml(name)} (${count})</button>`;
    }),
  ];
  els.chips.innerHTML = buttons.join("");
  els.chips.scrollLeft = scrollLeft;
}

function renderActiveFilters() {
  const pills = [];
  if (state.query) {
    pills.push(
      filterPill({
        key: "q",
        value: state.query,
        label: state.query,
        aria: `Clear search ${state.query}`,
      })
    );
  }
  if (state.category) {
    pills.push(
      filterPill({
        key: "category",
        value: state.category,
        label: state.category,
        aria: `Remove category ${state.category}`,
      })
    );
  }
  if (state.subcategory) {
    pills.push(
      filterPill({
        key: "subcategory",
        value: state.subcategory,
        label: state.subcategory,
        aria: `Remove subcategory ${state.subcategory}`,
      })
    );
  }
  for (const tag of state.tags) {
    pills.push(
      filterPill({
        key: "tag",
        value: tag,
        label: tag,
        aria: `Remove tag ${tag}`,
      })
    );
  }
  els.filters.hidden = pills.length === 0;
  els.filters.innerHTML = pills.join("");
}

function filterPill({ key, value, label, aria }) {
  return `<button type="button" class="filter-pill" data-clear="${escapeAttr(key)}" data-value="${escapeAttr(
    value
  )}" aria-label="${escapeAttr(aria)}">${escapeHtml(label)} <span aria-hidden="true">×</span></button>`;
}

function renderSort() {
  const starsPressed = state.sort !== "name";
  els.sort.innerHTML = `
    <button type="button" data-sort="stars" aria-pressed="${starsPressed}">Stars</button>
    <button type="button" data-sort="name" aria-pressed="${!starsPressed}">Name A–Z</button>
  `;
}

function renderTrust() {
  const date = asOfDate(state.generatedAt);
  if (!date) {
    els.asOf.hidden = true;
    els.asOf.textContent = "";
    return;
  }
  els.asOf.hidden = false;
  els.asOf.textContent = `Catalog and star counts as of ${date}.`;
}

function render() {
  const filtered = sortLists(
    state.lists.filter((list) =>
      matches(list, {
        query: state.query,
        category: state.category,
        tags: state.tags,
        subcategory: state.subcategory,
      })
    ),
    state.sort
  );

  els.meta.textContent = resultLine({
    shown: filtered.length,
    total: state.lists.length,
    query: state.query,
    category: state.category,
    tags: state.tags,
    subcategory: state.subcategory,
    sort: state.sort,
  });

  renderChips();
  renderActiveFilters();
  renderSort();

  if (filtered.length === 0) {
    const message = emptyMessage({
      query: state.query,
      category: state.category,
      tags: state.tags,
      subcategory: state.subcategory,
    });
    const actions = emptyActions({
      query: state.query,
      category: state.category,
      tags: state.tags,
      subcategory: state.subcategory,
    });
    const actionHtml = actions.length
      ? `<p class="empty-actions">${actions
          .map(
            (item) =>
              `<button type="button" data-empty-action="${escapeAttr(item.action)}">${escapeHtml(
                item.label
              )}</button>`
          )
          .join("")}</p>`
      : "";
    els.results.innerHTML = `<li class="empty"><p>${escapeHtml(message)}</p>${actionHtml}</li>`;
    return;
  }

  els.results.innerHTML = filtered.map(cardHtml).join("");
}

function cardHtml(list) {
  const stars = formatStars(list.stars_count, list.stars_approx);
  const tags = (list.tags || [])
    .slice(0, 6)
    .map((tag) => {
      const pressed = state.tags.includes(tag);
      return `<li><button type="button" data-tag="${escapeAttr(tag)}" aria-pressed="${pressed}">${escapeHtml(
        tag
      )}</button></li>`;
    })
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
    ? `<button type="button" class="subcategory" title="Subcategory" data-subcategory="${escapeAttr(
        list.subcategory
      )}" aria-pressed="${state.subcategory === list.subcategory}">${escapeHtml(list.subcategory)}</button>`
    : "";
  const url = escapeAttr(list.github_url);
  return `<li class="card">
    <div class="card-top">
      <h2><a href="${url}" target="_blank" rel="noopener noreferrer">${escapeHtml(
        list.name
      )}<span class="exit-mark" aria-hidden="true">↗</span></a></h2>
      <span class="stars" title="${escapeAttr(starTitle())}">★ ${escapeHtml(stars)}</span>
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

function clearSearch() {
  state.query = "";
  els.search.value = "";
}

function clearFilters() {
  clearSearch();
  state.category = "";
  state.subcategory = "";
  state.tags = [];
}

function bindEvents() {
  els.search.form?.addEventListener("submit", (event) => {
    event.preventDefault();
  });

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
    render();
  });

  els.filters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-clear]");
    if (!button) return;
    const key = button.getAttribute("data-clear");
    const value = button.getAttribute("data-value") || "";
    if (key === "q") clearSearch();
    if (key === "category") state.category = "";
    if (key === "subcategory") state.subcategory = "";
    if (key === "tag") state.tags = state.tags.filter((tag) => tag !== value);
    writeParams();
    render();
  });

  els.sort.addEventListener("click", (event) => {
    const button = event.target.closest("[data-sort]");
    if (!button) return;
    state.sort = button.getAttribute("data-sort") === "name" ? "name" : "stars";
    writeParams();
    render();
  });

  els.results.addEventListener("click", (event) => {
    const emptyAction = event.target.closest("[data-empty-action]");
    if (emptyAction) {
      const action = emptyAction.getAttribute("data-empty-action");
      if (action === "clear-search") clearSearch();
      if (action === "clear-filters") clearFilters();
      writeParams();
      render();
      return;
    }

    const tagButton = event.target.closest("[data-tag]");
    if (tagButton) {
      state.tags = toggleValue(state.tags, tagButton.getAttribute("data-tag") || "");
      writeParams();
      render();
      return;
    }

    const subButton = event.target.closest("[data-subcategory]");
    if (subButton) {
      const value = subButton.getAttribute("data-subcategory") || "";
      state.subcategory = state.subcategory === value ? "" : value;
      writeParams();
      render();
      return;
    }

    const noteButton = event.target.closest(".toggle-notes");
    if (!noteButton) return;
    const notes = document.getElementById(`notes-${noteButton.dataset.id}`);
    if (!notes) return;
    const open = notes.hidden;
    notes.hidden = !open;
    noteButton.setAttribute("aria-expanded", String(open));
    noteButton.textContent = open ? "Hide editorial note" : "Editorial note";
  });

  window.addEventListener("popstate", () => {
    applyParams();
    render();
  });
}

async function init() {
  applyParams();
  bindEvents();

  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) {
      throw new Error(`Could not load catalog (${response.status})`);
    }
    const payload = await response.json();
    const catalog = normalizeCatalog(payload);
    state.lists = catalog.lists;
    state.generatedAt = catalog.generatedAt;
    const categories = uniqueCategories(catalog.lists).length;
    els.stats.textContent = `${catalog.lists.length} lists · ${categories} categories`;
    renderTrust();
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
