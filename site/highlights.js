/** Parse HIGHLIGHTS.md and format catalog fields. No dates are invented. */

export function parseHighlights(markdown) {
  const titleMatch = markdown.match(/^#\s+(.+)$/m);
  const title = (titleMatch?.[1] || "20 Must-Know Lists")
    .replace(/^ListVerse Highlights:\s*/i, "")
    .trim();

  const introMatch = markdown.match(/^#\s+.+\n\n([\s\S]+?)\n\n---/);
  const intro = introMatch ? introMatch[1].trim() : "";

  const lists = [];
  const itemRe =
    /^##\s+(\d+)\.\s+\[([^\]]+)\]\(([^)]+)\)\s*\n+([\s\S]*?)(?=^##\s+\d+\.|\n---\s*$)/gm;
  let match;
  while ((match = itemRe.exec(markdown))) {
    lists.push({
      rank: Number(match[1]),
      name: match[2].trim(),
      github_url: match[3].trim(),
      blurb: match[4].trim().replace(/\s+/g, " "),
    });
  }
  return { title, intro, lists };
}

export function normalizeUrl(url) {
  return String(url || "")
    .trim()
    .replace(/\/+$/, "")
    .toLowerCase();
}

/** Format live stars_count only. Never use frozen stars_approx. */
export function formatStars(count) {
  if (typeof count !== "number" || !Number.isFinite(count)) return "—";
  if (count >= 1000) {
    const value = count / 1000;
    const digits = count >= 10000 ? 0 : 1;
    return `${value.toFixed(digits).replace(/\.0$/, "")}k`;
  }
  return String(count);
}

const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

/** Format a YYYY-MM-DD last_commit_date. Returns "" if the value is missing or unparseable. */
export function formatCommitDate(value) {
  if (!value || typeof value !== "string") return "";
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value.trim());
  if (!match) return "";
  const month = MONTHS[Number(match[2]) - 1];
  if (!month) return "";
  return `${Number(match[3])} ${month} ${match[1]}`;
}

export function hasFeaturedExample(list) {
  const example = list?.featured_example;
  if (!example || typeof example !== "object") return false;
  return Boolean(example.name || example.url || example.why);
}

export function joinHighlights(highlights, lists) {
  const byUrl = new Map();
  for (const list of lists) {
    byUrl.set(normalizeUrl(list.github_url), list);
  }
  return highlights.map((highlight) => ({
    ...highlight,
    list: byUrl.get(normalizeUrl(highlight.github_url)) || null,
  }));
}
