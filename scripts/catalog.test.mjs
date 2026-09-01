import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import {
  asOfDate,
  categoryCountsForSearch,
  emptyActions,
  emptyMessage,
  matches,
  normalizeCatalog,
  parseParams,
  resultLine,
  serializeParams,
  sortLists,
} from "../site/catalog.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const lists = JSON.parse(readFileSync(join(root, "data", "lists.json"), "utf8"));

describe("result line", () => {
  it("names no filters as showing all", () => {
    assert.equal(
      resultLine({ shown: 195, total: 195 }),
      "Showing all 195 lists. Sorted by GitHub stars."
    );
  });

  it("names a search query", () => {
    assert.equal(
      resultLine({ shown: 4, total: 195, query: "kubernetes" }),
      "Showing 4 of 195 for \u201ckubernetes\u201d. Sorted by GitHub stars."
    );
  });

  it("names a category", () => {
    assert.equal(
      resultLine({ shown: 10, total: 195, category: "Data Visualization" }),
      "Showing 10 of 195 in Data Visualization. Sorted by GitHub stars."
    );
  });

  it("names search AND category", () => {
    assert.equal(
      resultLine({
        shown: 0,
        total: 195,
        query: "kubernetes",
        category: "Data Visualization",
      }),
      "Showing 0 of 195 for \u201ckubernetes\u201d in Data Visualization. Sorted by GitHub stars."
    );
  });
});

describe("empty copy", () => {
  it("quotes a query-only miss", () => {
    assert.equal(emptyMessage({ query: "zzzzqqq" }), "No lists match \u201czzzzqqq\u201d.");
  });

  it("names category when both filters miss", () => {
    assert.equal(
      emptyMessage({ query: "kubernetes", category: "Data Visualization" }),
      "No lists in Data Visualization match \u201ckubernetes\u201d."
    );
  });

  it("offers clear-search (keep category) and clear-filters", () => {
    const actions = emptyActions({
      query: "kubernetes",
      category: "Data Visualization",
    });
    assert.deepEqual(
      actions.map((item) => [item.action, item.label]),
      [
        ["clear-search", "Clear search"],
        ["clear-search", "Show all in Data Visualization"],
        ["clear-filters", "Clear filters"],
      ]
    );
  });
});

describe("live catalog: kubernetes", () => {
  it("matches four lists by substring search", () => {
    const filtered = lists.filter((list) => matches(list, { query: "kubernetes" }));
    assert.equal(lists.length, 195);
    assert.equal(filtered.length, 4);
  });

  it("ANDs search with category", () => {
    const filtered = lists.filter((list) =>
      matches(list, { query: "kubernetes", category: "Data Visualization" })
    );
    assert.equal(filtered.length, 0);
  });

  it("counts chips from search and ignores selected category", () => {
    const { total, counts } = categoryCountsForSearch(lists, "kubernetes");
    assert.equal(total, 4);
    assert.equal(counts.get("Data Visualization") || 0, 0);
    assert.equal(counts.get("Developer Tools & Coding"), 3);
    const unfiltered = categoryCountsForSearch(lists, "");
    assert.equal(unfiltered.total, 195);
    assert.equal(unfiltered.counts.get("Data Visualization"), 10);
  });
});

describe("tags, subcategory, and sort", () => {
  it("ANDs multiple tags and keeps the URL shareable", () => {
    const query = serializeParams({ tags: ["llm", "python"], query: "guide" });
    assert.equal(query, "q=guide&tag=llm&tag=python");
    const parsed = parseParams(`?${query}`);
    assert.deepEqual(parsed.tags, ["llm", "python"]);
    assert.equal(parsed.query, "guide");
  });

  it("ANDs subcategory with the rest of the filters", () => {
    const filtered = lists.filter((list) =>
      matches(list, { subcategory: "Public Datasets", category: "Data Sources & Datasets" })
    );
    assert.ok(filtered.length > 0);
    assert.ok(filtered.every((list) => list.subcategory === "Public Datasets"));
  });

  it("sorts by stars descending by default and by name when asked", () => {
    const byStars = sortLists(lists, "stars");
    assert.ok((byStars[0].stars_count || 0) >= (byStars[1].stars_count || 0));
    const byName = sortLists(lists, "name");
    assert.ok(byName[0].name.localeCompare(byName[1].name, undefined, { sensitivity: "base" }) <= 0);
    assert.notEqual(byStars[0].name, byName[0].name);
  });
});

describe("catalog payload", () => {
  it("reads generated_at when present and refuses to invent a date", () => {
    const wrapped = normalizeCatalog({ generated_at: "2026-09-01", lists });
    assert.equal(wrapped.generatedAt, "2026-09-01");
    assert.equal(asOfDate(wrapped.generatedAt), "2026-09-01");
    assert.equal(asOfDate(null), null);
    assert.equal(asOfDate(""), null);
    const legacy = normalizeCatalog(lists);
    assert.equal(legacy.generatedAt, null);
  });

  it("persists generated_at on the catalog metadata", () => {
    const meta = JSON.parse(readFileSync(join(root, "data", "catalog_meta.json"), "utf8"));
    assert.match(meta.generated_at, /^\d{4}-\d{2}-\d{2}$/);
  });
});
