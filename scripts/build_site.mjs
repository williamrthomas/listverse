import { cpSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const site = join(root, "site");
const dist = join(root, "dist");
const listsPath = join(root, "data", "lists.json");
const highlights = join(root, "HIGHLIGHTS.md");

rmSync(dist, { recursive: true, force: true });
cpSync(site, dist, { recursive: true });
mkdirSync(join(dist, "data"), { recursive: true });
cpSync(listsPath, join(dist, "data", "lists.json"));
cpSync(highlights, join(dist, "HIGHLIGHTS.md"));

const template = readFileSync(join(site, "list.html"), "utf8");
const catalog = JSON.parse(readFileSync(listsPath, "utf8"));
if (!Array.isArray(catalog)) {
  throw new Error("Catalog data is not a list");
}
mkdirSync(join(dist, "lists"), { recursive: true });
for (const list of catalog) {
  if (!list?.id) continue;
  const dir = join(dist, "lists", String(list.id));
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "index.html"), template);
}
rmSync(join(dist, "list.html"), { force: true });

function emitStatic(template, destDir, destFile) {
  mkdirSync(destDir, { recursive: true });
  writeFileSync(join(destDir, "index.html"), template);
  writeFileSync(destFile, template);
}

const about = readFileSync(join(site, "about.html"), "utf8");
emitStatic(about, join(dist, "about"), join(dist, "about.html"));

const journey = readFileSync(join(site, "journey.html"), "utf8");
emitStatic(journey, join(dist, "journeys", "agents"), join(dist, "journeys", "agents.html"));
emitStatic(journey, join(dist, "journeys", "learn"), join(dist, "journeys", "learn.html"));
rmSync(join(dist, "journey.html"), { force: true });

console.log(
  `Built ${dist} (${statSync(listsPath).size} bytes of catalog data, ${catalog.length} interiors, about + 2 journeys)`
);
