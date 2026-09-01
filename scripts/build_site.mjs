import { cpSync, mkdirSync, rmSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const site = join(root, "site");
const dist = join(root, "dist");
const lists = join(root, "data", "lists.json");
const highlights = join(root, "HIGHLIGHTS.md");

rmSync(dist, { recursive: true, force: true });
cpSync(site, dist, { recursive: true });
mkdirSync(join(dist, "data"), { recursive: true });
cpSync(lists, join(dist, "data", "lists.json"));
cpSync(highlights, join(dist, "HIGHLIGHTS.md"));
console.log(`Built ${dist} (${statSync(lists).size} bytes of catalog data)`);
