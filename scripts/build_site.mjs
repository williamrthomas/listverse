import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, rmSync, cpSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const site = join(root, "site");
const dist = join(root, "dist");
const lists = join(root, "data", "lists.json");
const meta = join(root, "data", "catalog_meta.json");

function catalogGeneratedAt() {
  try {
    const payload = JSON.parse(readFileSync(meta, "utf8"));
    if (payload && typeof payload.generated_at === "string" && payload.generated_at.trim()) {
      return payload.generated_at.trim();
    }
  } catch {
    // Fall through to git history for the catalog file.
  }
  try {
    const date = execFileSync("git", ["log", "-1", "--format=%cs", "--", "data/lists.json"], {
      cwd: root,
      encoding: "utf8",
    }).trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(date)) return date;
  } catch {
    // No date persisted; the UI must omit as-of rather than invent one.
  }
  return null;
}

const listsData = JSON.parse(readFileSync(lists, "utf8"));
if (!Array.isArray(listsData)) {
  throw new Error("data/lists.json must be an array of lists");
}

const payload = { lists: listsData };
const generatedAt = catalogGeneratedAt();
if (generatedAt) payload.generated_at = generatedAt;

rmSync(dist, { recursive: true, force: true });
cpSync(site, dist, { recursive: true });
mkdirSync(join(dist, "data"), { recursive: true });
writeFileSync(join(dist, "data", "lists.json"), `${JSON.stringify(payload)}\n`);
console.log(
  `Built ${dist} (${statSync(lists).size} bytes of catalog data${
    generatedAt ? `, generated_at ${generatedAt}` : ""
  })`
);
