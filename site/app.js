import {
  formatCommitDate,
  formatStars,
  hasFeaturedExample,
  joinHighlights,
  parseHighlights,
} from "./highlights.js";

const DATA_URL = "/data/lists.json";
const HIGHLIGHTS_URL = "/HIGHLIGHTS.md";
const SORTS = [
  { id: "pushed", label: "Recently pushed" },
  { id: "stars", label: "Stars" },
  { id: "name", label: "Name" },
  { id: "quality", label: "Quality" },
];

const JOURNEYS = {
  agents: {
    title: "Agents",
    intro:
      "A short trail through agent lists in the catalog — directories, frameworks, coding agents, and RAG.",
    ids: [
      "awesome-ai-agents",
      "ai-agents-for-beginners",
      "awesome-langchain",
      "awesome-ai-sdks",
      "autonomous-agents",
      "awesome-gpt-agents",
      "rag-from-scratch",
      "awesome-rag",
      "crewai",
      "awesome-copilot",
      "awesome-cursorrules",
      "awesome-llm-apps",
    ],
  },
  learn: {
    title: "Learn",
    intro:
      "A short trail through lists people use to learn — primers, project-based work, roadmaps, and courses.",
    ids: [
      "prompt-engineering-guide",
      "learn-prompting",
      "build-your-own-x",
      "project-based-learning",
      "free-programming-books",
      "system-design-primer",
      "developer-roadmap",
      "machine-learning-tutorials",
      "generative-ai-for-beginners",
      "llms-from-scratch",
      "data-engineer-roadmap",
      "ai-for-beginners",
    ],
  },
};

const page = document.body.dataset.page || "front";

const els = {
  stats: document.getElementById("stats"),
  search: document.getElementById("q"),
  chips: document.getElementById("category-filters"),
  sorts: document.getElementById("sort-filters"),
  meta: document.getElementById("result-meta"),
  results: document.getElementById("results"),
  error: document.getElementById("error"),
  doorTitle: document.getElementById("door-title"),
  doorIntro: document.getElementById("door-intro"),
  journeyTitle: document.getElementById("journey-title"),
  journeyIntro: document.getElementById("journey-intro"),
};

/** @type {{ lists: object[], categories: string[], query: string, category: string, sort: string }} */
const state = {
  lists: [],
  categories: [],
  query: "",
  category: "",
  sort: "pushed",
};

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

function compareLists(a, b, sort) {
  if (sort === "stars") {
    return (b.stars_count || 0) - (a.stars_count || 0);
  }
  if (sort === "name") {
    return (a.name || "").localeCompare(b.name || "", undefined, { sensitivity: "base" });
  }
  if (sort === "quality") {
    return (
      (b.quality_score || 0) - (a.quality_score || 0) ||
      (a.name || "").localeCompare(b.name || "", undefined, { sensitivity: "base" })
    );
  }
  return (
    (b.last_commit_date || "").localeCompare(a.last_commit_date || "") ||
    (b.stars_count || 0) - (a.stars_count || 0)
  );
}

function parseParams() {
  const params = new URLSearchParams(window.location.search);
  const sort = params.get("sort") || "pushed";
  const known = SORTS.some((item) => item.id === sort);
  return {
    query: (params.get("q") || "").trim(),
    category: params.get("category") || "",
    sort: known ? sort : "pushed",
  };
}

function writeParams() {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.category) params.set("category", state.category);
  if (state.sort && state.sort !== "pushed") params.set("sort", state.sort);
  const next = params.toString();
  const url = next ? `?${next}` : window.location.pathname;
  history.replaceState(null, "", url);
}

function renderChips() {
  if (!els.chips) return;
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

function renderSorts() {
  if (!els.sorts) return;
  els.sorts.innerHTML = SORTS.map(
    (item) =>
      `<button type="button" class="chip" data-sort="${escapeAttr(item.id)}" aria-pressed="${
        state.sort === item.id
      }">${escapeHtml(item.label)}</button>`
  ).join("");
}

function listHref(list) {
  return list?.id ? `/lists/${encodeURIComponent(list.id)}/` : "";
}

function repoPath(githubUrl) {
  const match = String(githubUrl || "").match(/github\.com\/([^/]+\/[^/]+)/i);
  return match ? match[1].replace(/\/+$/, "") : "";
}

function inboundRelated(lists, id) {
  return lists.filter((list) => (list.related_lists || []).includes(id) && list.id !== id);
}

function featuredExampleHtml(list) {
  if (!hasFeaturedExample(list)) return "";
  const example = list.featured_example;
  const label = example.name || example.url;
  const linked = example.url
    ? `<a href="${escapeAttr(example.url)}" rel="noopener noreferrer">${escapeHtml(label)}</a>`
    : escapeHtml(label);
  const why = example.why ? ` — ${escapeHtml(example.why)}` : "";
  return `${linked}${why}`;
}

function interiorsHtml(list) {
  const blocks = [];
  if (list.getting_started) {
    blocks.push(
      `<div class="interior-block"><h3>Start here</h3><p>${escapeHtml(
        list.getting_started
      )}</p></div>`
    );
  }
  const featured = featuredExampleHtml(list);
  if (featured) {
    blocks.push(
      `<div class="interior-block"><h3>A featured entry</h3><p>${featured}</p></div>`
    );
  }
  if (Array.isArray(list.best_sections) && list.best_sections.length) {
    const items = list.best_sections.map((section) => `<li>${escapeHtml(section)}</li>`).join("");
    blocks.push(
      `<div class="interior-block"><h3>Best sections</h3><ul class="sections">${items}</ul></div>`
    );
  }
  if (Array.isArray(list.suggested_projects) && list.suggested_projects.length) {
    const items = list.suggested_projects.map((project) => `<li>${escapeHtml(project)}</li>`).join("");
    blocks.push(
      `<div class="interior-block"><h3>Suggested projects</h3><ul class="projects">${items}</ul></div>`
    );
  }
  if (list.editorial_notes) {
    blocks.push(
      `<div class="interior-block"><h3>Editorial note</h3><p>${escapeHtml(
        list.editorial_notes
      )}</p></div>`
    );
  }
  return blocks.join("");
}

function trailHtml(list) {
  const steps = [];
  if (list.getting_started) {
    steps.push({
      title: "Start here",
      body: `<p>${escapeHtml(list.getting_started)}</p>`,
    });
  }
  const featured = featuredExampleHtml(list);
  if (featured) {
    steps.push({
      title: "A featured entry",
      body: `<p>${featured}</p>`,
    });
  }
  if (Array.isArray(list.best_sections) && list.best_sections.length) {
    const items = list.best_sections.map((section) => `<li>${escapeHtml(section)}</li>`).join("");
    steps.push({
      title: "Best sections",
      body: `<ul class="sections">${items}</ul>`,
    });
  }
  if (!steps.length) return "";
  return `<ol class="trail">${steps
    .map(
      (step, index) =>
        `<li class="interior-block"><h3>${index + 1}. ${escapeHtml(step.title)}</h3>${step.body}</li>`
    )
    .join("")}</ol>`;
}

function cousinLinks(lists, ids) {
  const byId = new Map(lists.map((list) => [list.id, list]));
  const items = [];
  for (const id of ids) {
    const list = byId.get(id);
    if (!list) continue;
    items.push(
      `<li><a href="${escapeAttr(listHref(list))}">${escapeHtml(list.name)}</a></li>`
    );
  }
  return items;
}

function objectHtml(list, lists) {
  const stars = formatStars(list.stars_count);
  const subcategory = list.subcategory ? `<span>${escapeHtml(list.subcategory)}</span>` : "";
  const meta = `<div class="meta">
      <span class="category-label">${escapeHtml(list.category || "")}</span>
      ${subcategory}
    </div>`;
  const trail = trailHtml(list);
  const essay = [];
  if (list.editorial_notes) {
    essay.push(
      `<div class="interior-block"><h3>Editorial note</h3><p>${escapeHtml(
        list.editorial_notes
      )}</p></div>`
    );
  }
  if (Array.isArray(list.suggested_projects) && list.suggested_projects.length) {
    const items = list.suggested_projects
      .map((project) => `<li>${escapeHtml(project)}</li>`)
      .join("");
    essay.push(
      `<div class="interior-block"><h3>Suggested projects</h3><ul class="projects">${items}</ul></div>`
    );
  }

  const also = cousinLinks(lists, list.related_lists || []);
  const shownIn = cousinLinks(
    lists,
    inboundRelated(lists, list.id).map((other) => other.id)
  );
  const cousins = [
    also.length
      ? `<section class="cousins"><h3>Also in the catalog</h3><ul>${also.join("")}</ul></section>`
      : "",
    shownIn.length
      ? `<section class="cousins"><h3>Shows up in</h3><ul>${shownIn.join("")}</ul></section>`
      : "",
  ]
    .filter(Boolean)
    .join("");

  const repo = repoPath(list.github_url);
  const pushed = formatCommitDate(list.last_commit_date);
  const citation = `<footer class="citation">
    <p class="catalog-id">${escapeHtml(list.id)}</p>
    ${repo ? `<p>${escapeHtml(repo)}</p>` : ""}
    ${list.maintainer ? `<p>@${escapeHtml(list.maintainer)}</p>` : ""}
    ${list.license ? `<p>${escapeHtml(list.license)}</p>` : ""}
    ${pushed ? `<p>Last pushed ${escapeHtml(pushed)}</p>` : ""}
    ${
      list.github_url
        ? `<p><a href="${escapeAttr(list.github_url)}" rel="noopener noreferrer">On GitHub ↗</a></p>`
        : ""
    }
  </footer>`;

  return `<div class="card-top">
      <h2>${escapeHtml(list.name)}</h2>
      <span class="stars" title="GitHub stars">★ ${escapeHtml(stars)}</span>
    </div>
    ${meta}
    <p class="description">${escapeHtml(list.description || "")}</p>
    ${trail}
    ${essay.join("")}
    ${cousins}
    ${citation}`;
}

function cardMeta(list) {
  const stars = formatStars(list.stars_count);
  const pushed = formatCommitDate(list.last_commit_date);
  const subcategory = list.subcategory ? `<span>${escapeHtml(list.subcategory)}</span>` : "";
  const pushedHtml = pushed ? `<span>Last pushed ${escapeHtml(pushed)}</span>` : "";
  return {
    stars,
    meta: `<div class="meta">
      <span class="category-label">${escapeHtml(list.category || "")}</span>
      ${subcategory}
      <span>@${escapeHtml(list.maintainer || "")}</span>
      ${pushedHtml}
    </div>`,
  };
}

function highlightCardHtml(entry) {
  const list = entry.list;
  const name = list?.name || entry.name;
  const url = list?.github_url || entry.github_url;
  const { stars, meta } = list
    ? cardMeta(list)
    : { stars: "—", meta: "" };
  const interiors = list ? interiorsHtml(list) : "";
  const href = list ? listHref(list) : url;
  return `<li class="card">
    <div class="card-top">
      <h2><span class="rank">${escapeHtml(String(entry.rank))}</span><a href="${escapeAttr(
        href
      )}">${escapeHtml(name)}</a></h2>
      <span class="stars" title="GitHub stars">★ ${escapeHtml(stars)}</span>
    </div>
    ${meta}
    <p class="description">${escapeHtml(entry.blurb)}</p>
    ${interiors ? `<div class="interiors">${interiors}</div>` : ""}
  </li>`;
}

function cardHtml(list) {
  const { stars, meta } = cardMeta(list);
  const tags = (list.tags || [])
    .slice(0, 6)
    .map((tag) => `<li>${escapeHtml(tag)}</li>`)
    .join("");
  const interiors = interiorsHtml(list);
  const toggle = interiors
    ? `<button type="button" class="toggle-notes" aria-expanded="false" data-id="${escapeAttr(
        list.id
      )}">List interior</button>
       <div class="interiors" id="notes-${escapeAttr(list.id)}" hidden>${interiors}</div>`
    : "";
  return `<li class="card">
    <div class="card-top">
      <h2><a href="${escapeAttr(listHref(list))}">${escapeHtml(list.name)}</a></h2>
      <span class="stars" title="GitHub stars">★ ${escapeHtml(stars)}</span>
    </div>
    ${meta}
    <p class="description">${escapeHtml(list.description || "")}</p>
    ${tags ? `<ul class="tags">${tags}</ul>` : ""}
    ${toggle}
  </li>`;
}

function sortLabel(sort) {
  return SORTS.find((item) => item.id === sort)?.label || "Recently pushed";
}

function renderBrowse() {
  const query = state.query.toLowerCase();
  const filtered = state.lists
    .filter((list) => matches(list, query, state.category))
    .sort((a, b) => compareLists(a, b, state.sort));

  const sortNote = `Sorted by ${sortLabel(state.sort)}`;
  els.meta.textContent =
    filtered.length === state.lists.length
      ? `Showing all ${filtered.length} lists. ${sortNote}.`
      : `Showing ${filtered.length} of ${state.lists.length} lists. ${sortNote}.`;

  if (filtered.length === 0) {
    els.results.innerHTML = `<li class="empty">No lists match that search.</li>`;
    return;
  }

  els.results.innerHTML = filtered.map(cardHtml).join("");
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

function bindBrowseEvents() {
  els.search?.addEventListener("input", () => {
    state.query = els.search.value.trim();
    writeParams();
    renderBrowse();
  });

  els.chips?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) return;
    state.category = button.getAttribute("data-category") || "";
    writeParams();
    renderChips();
    renderBrowse();
  });

  els.sorts?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-sort]");
    if (!button) return;
    state.sort = button.getAttribute("data-sort") || "pushed";
    writeParams();
    renderSorts();
    renderBrowse();
  });

  els.results.addEventListener("click", (event) => {
    const button = event.target.closest(".toggle-notes");
    if (!button) return;
    const interiors = document.getElementById(`notes-${button.dataset.id}`);
    if (!interiors) return;
    const open = interiors.hidden;
    interiors.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    button.textContent = open ? "Hide list interior" : "List interior";
  });
}

async function loadLists() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`Could not load catalog (${response.status})`);
  }
  const lists = await response.json();
  if (!Array.isArray(lists)) {
    throw new Error("Catalog data is not a list");
  }
  return lists;
}

async function initFront() {
  const [lists, highlightsRes] = await Promise.all([loadLists(), fetch(HIGHLIGHTS_URL)]);
  if (!highlightsRes.ok) {
    throw new Error(`Could not load highlights (${highlightsRes.status})`);
  }
  const parsed = parseHighlights(await highlightsRes.text());
  const joined = joinHighlights(parsed.lists, lists);
  state.lists = lists;

  const categories = uniqueCategories(lists).length;
  els.stats.textContent = `${lists.length} lists · ${categories} categories`;
  if (els.doorTitle) els.doorTitle.textContent = parsed.title || "20 must-know lists";
  if (els.doorIntro) els.doorIntro.textContent = parsed.intro;
  els.meta.textContent = `${joined.length} essential lists, in editorial order`;
  els.results.innerHTML = joined.map(highlightCardHtml).join("");
}

async function initBrowse() {
  const params = parseParams();
  state.query = params.query;
  state.category = params.category;
  state.sort = params.sort;
  if (els.search) els.search.value = state.query;
  bindBrowseEvents();

  const lists = await loadLists();
  state.lists = lists;
  const categories = uniqueCategories(lists).length;
  els.stats.textContent = `${lists.length} lists · ${categories} categories`;
  renderChips();
  renderSorts();
  renderBrowse();
}

function listIdFromPath() {
  const match = window.location.pathname.match(/\/lists\/([^/]+)\/?$/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function initList() {
  const lists = await loadLists();
  state.lists = lists;
  const categories = uniqueCategories(lists).length;
  els.stats.textContent = `${lists.length} lists · ${categories} categories`;

  const root = document.getElementById("list-root");
  const id = listIdFromPath();
  const list = lists.find((item) => item.id === id);
  if (!list) {
    document.title = "Not found — ListVerse";
    if (els.error) {
      els.error.hidden = false;
      els.error.textContent = "That list isn’t in the catalog.";
    }
    if (root) root.innerHTML = "";
    return;
  }

  document.title = `${list.name} — ListVerse`;
  if (root) root.innerHTML = objectHtml(list, lists);
}

async function initAbout() {
  const lists = await loadLists();
  state.lists = lists;
  const categories = uniqueCategories(lists).length;
  els.stats.textContent = `${lists.length} lists · ${categories} categories`;
}

function journeyIdFromPath() {
  const match = window.location.pathname.match(/\/journeys\/([^/]+)\/?$/);
  return match ? decodeURIComponent(match[1]) : "";
}

function journeyCardHtml(list, rank) {
  const { stars, meta } = cardMeta(list);
  return `<li class="card">
    <div class="card-top">
      <h2><span class="rank">${escapeHtml(String(rank))}</span><a href="${escapeAttr(
        listHref(list)
      )}">${escapeHtml(list.name)}</a></h2>
      <span class="stars" title="GitHub stars">★ ${escapeHtml(stars)}</span>
    </div>
    ${meta}
    <p class="description">${escapeHtml(list.description || "")}</p>
  </li>`;
}

async function initJourney() {
  const lists = await loadLists();
  state.lists = lists;
  const categories = uniqueCategories(lists).length;
  els.stats.textContent = `${lists.length} lists · ${categories} categories`;

  const slug = journeyIdFromPath();
  const journey = JOURNEYS[slug];
  if (!journey) {
    document.title = "Not found — ListVerse";
    if (els.error) {
      els.error.hidden = false;
      els.error.textContent = "That journey isn’t in the catalog.";
    }
    if (els.results) els.results.innerHTML = "";
    return;
  }

  document.title = `${journey.title} — ListVerse`;
  if (els.journeyTitle) els.journeyTitle.textContent = journey.title;
  if (els.journeyIntro) els.journeyIntro.textContent = journey.intro;

  const byId = new Map(lists.map((list) => [list.id, list]));
  const cards = [];
  for (const id of journey.ids) {
    const list = byId.get(id);
    if (!list) continue;
    cards.push(journeyCardHtml(list, cards.length + 1));
  }
  if (els.meta) {
    els.meta.textContent = `${cards.length} lists, in trail order`;
  }
  if (els.results) els.results.innerHTML = cards.join("");
}

async function init() {
  try {
    if (page === "browse") {
      await initBrowse();
    } else if (page === "list") {
      await initList();
    } else if (page === "about") {
      await initAbout();
    } else if (page === "journey") {
      await initJourney();
    } else {
      await initFront();
    }
  } catch (error) {
    if (els.error) {
      els.error.hidden = false;
      els.error.textContent =
        error instanceof Error ? error.message : "Could not load the catalog.";
    }
    if (els.stats) els.stats.textContent = "Catalog unavailable";
    if (els.meta) els.meta.textContent = "";
  }
}

init();
