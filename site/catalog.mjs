const LEFT_QUOTE = "\u201c";
const RIGHT_QUOTE = "\u201d";

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function escapeAttr(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}

export function haystack(list) {
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

export function uniqueCategories(lists) {
  const counts = new Map();
  for (const list of lists) {
    const name = list.category || "Uncategorized";
    counts.set(name, (counts.get(name) || 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

export function matches(list, { query = "", category = "", tags = [], subcategory = "" } = {}) {
  if (category && list.category !== category) return false;
  if (subcategory && list.subcategory !== subcategory) return false;
  if (tags.length) {
    const have = new Set(list.tags || []);
    for (const tag of tags) {
      if (!have.has(tag)) return false;
    }
  }
  if (!query) return true;
  return haystack(list).includes(query.toLowerCase());
}

/** Category chip counts follow the current search and ignore the selected category. */
export function categoryCountsForSearch(lists, query) {
  const q = (query || "").trim().toLowerCase();
  const counts = new Map();
  let total = 0;
  for (const list of lists) {
    if (q && !haystack(list).includes(q)) continue;
    total += 1;
    const name = list.category || "Uncategorized";
    counts.set(name, (counts.get(name) || 0) + 1);
  }
  return { total, counts };
}

export function sortLists(lists, sort) {
  const copy = lists.slice();
  if (sort === "name") {
    copy.sort((a, b) =>
      (a.name || "").localeCompare(b.name || "", undefined, { sensitivity: "base" })
    );
  } else {
    copy.sort(
      (a, b) =>
        (b.stars_count || 0) - (a.stars_count || 0) ||
        (a.name || "").localeCompare(b.name || "", undefined, { sensitivity: "base" })
    );
  }
  return copy;
}

function quote(value) {
  return `${LEFT_QUOTE}${value}${RIGHT_QUOTE}`;
}

function taggedPhrase(tags) {
  if (!tags.length) return "";
  if (tags.length === 1) return ` tagged ${tags[0]}`;
  if (tags.length === 2) return ` tagged ${tags[0]} and ${tags[1]}`;
  const head = tags.slice(0, -1).join(", ");
  return ` tagged ${head}, and ${tags.at(-1)}`;
}

function placePhrase(category, subcategory) {
  if (category && subcategory) return ` in ${category} (${subcategory})`;
  if (category) return ` in ${category}`;
  if (subcategory) return ` in ${subcategory}`;
  return "";
}

export function resultLine({
  shown,
  total,
  query = "",
  category = "",
  tags = [],
  subcategory = "",
  sort = "stars",
} = {}) {
  const hasFilters = Boolean(query || category || subcategory || tags.length);
  let text;
  if (!hasFilters) {
    text = `Showing all ${total} lists.`;
  } else {
    const queryPart = query ? ` for ${quote(query)}` : "";
    text = `Showing ${shown} of ${total}${queryPart}${placePhrase(category, subcategory)}${taggedPhrase(tags)}.`;
  }
  text += sort === "name" ? " Sorted by name." : " Sorted by GitHub stars.";
  return text;
}

export function emptyMessage({ query = "", category = "", tags = [], subcategory = "" } = {}) {
  if (query && category) {
    return `No lists in ${category} match ${quote(query)}.`;
  }
  if (query && subcategory) {
    return `No lists in ${subcategory} match ${quote(query)}.`;
  }
  if (query && tags.length) {
    return `No lists${taggedPhrase(tags)} match ${quote(query)}.`;
  }
  if (query) {
    return `No lists match ${quote(query)}.`;
  }
  if (category) {
    return `No lists in ${category}.`;
  }
  if (subcategory) {
    return `No lists in ${subcategory}.`;
  }
  if (tags.length) {
    return `No lists${taggedPhrase(tags)}.`;
  }
  return "No lists match that search.";
}

export function emptyActions({ query = "", category = "", tags = [], subcategory = "" } = {}) {
  const hasOther = Boolean(category || subcategory || tags.length);
  if (query && category) {
    return [
      { action: "clear-search", label: "Clear search" },
      { action: "clear-search", label: `Show all in ${category}` },
      { action: "clear-filters", label: "Clear filters" },
    ];
  }
  const actions = [];
  if (query) actions.push({ action: "clear-search", label: "Clear search" });
  if (query || hasOther) actions.push({ action: "clear-filters", label: "Clear filters" });
  return actions;
}

export function parseParams(search) {
  const raw = search.startsWith("?") ? search.slice(1) : search;
  const params = new URLSearchParams(raw);
  const tags = [
    ...new Set(
      params
        .getAll("tag")
        .flatMap((value) => value.split(","))
        .map((value) => value.trim())
        .filter(Boolean)
    ),
  ];
  return {
    query: (params.get("q") || "").trim(),
    category: params.get("category") || "",
    subcategory: params.get("subcategory") || "",
    tags,
    sort: params.get("sort") === "name" ? "name" : "stars",
  };
}

export function serializeParams({
  query = "",
  category = "",
  subcategory = "",
  tags = [],
  sort = "stars",
} = {}) {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (category) params.set("category", category);
  if (subcategory) params.set("subcategory", subcategory);
  for (const tag of tags) params.append("tag", tag);
  if (sort === "name") params.set("sort", "name");
  return params.toString();
}

export function normalizeCatalog(payload) {
  if (Array.isArray(payload)) {
    return { lists: payload, generatedAt: null };
  }
  if (payload && Array.isArray(payload.lists)) {
    const generatedAt =
      typeof payload.generated_at === "string" && payload.generated_at.trim()
        ? payload.generated_at.trim()
        : null;
    return { lists: payload.lists, generatedAt };
  }
  throw new Error("Catalog data is not a list");
}

/** Return a YYYY-MM-DD date from catalog metadata, or null — never invent one. */
export function asOfDate(generatedAt) {
  if (!generatedAt || typeof generatedAt !== "string") return null;
  const match = generatedAt.trim().match(/^(\d{4}-\d{2}-\d{2})/);
  return match ? match[1] : null;
}

export function toggleValue(list, value) {
  if (!value) return list.slice();
  const next = list.filter((item) => item !== value);
  if (next.length === list.length) next.push(value);
  return next;
}
