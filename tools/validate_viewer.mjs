import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const toolsDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(toolsDir);
const htmlPath = path.join(root, "index.html");
const dataPath = path.join(root, "database-data.js");
const managerPath = path.join(root, "app-manager.js");

const html = fs.readFileSync(htmlPath, "utf8");
const dataSource = fs.readFileSync(dataPath, "utf8");
const managerSource = fs.readFileSync(managerPath, "utf8");
const inlineScripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)];

if (inlineScripts.length !== 1) {
  throw new Error(`Expected 1 inline application script, found ${inlineScripts.length}`);
}

new vm.Script(inlineScripts[0][1], { filename: "index-inline.js" });
new vm.Script(managerSource, { filename: "app-manager.js" });

const sandbox = { window: {} };
vm.createContext(sandbox);
new vm.Script(dataSource, { filename: "database-data.js" }).runInContext(sandbox);
const database = sandbox.window.AI_VIDEO_PROMPT_DB;

if (!database || !Array.isArray(database.prompts) || !database.prompts.length) {
  throw new Error("Browser data contains no prompts");
}

for (const id of [
  "app", "search", "category", "ratio", "collection", "promptList", "detail", "toast",
  "openImportButton", "exportButton", "manageModal", "fileInput", "promptForm",
  "exportModal", "exportData", "copyExportButton", "downloadExportButton",
  "openImageImportButton", "exportImageButton", "editMediaType", "durationField",
  "openCollectionManager", "quickCreateCollection", "collectionModal", "closeCollectionModal",
  "collectionForm", "collectionName", "collectionList",
]) {
  if (!html.includes(`id="${id}"`)) {
    throw new Error(`Missing required element #${id}`);
  }
}

const shotCount = database.prompts.reduce(
  (sum, prompt) => sum + (Array.isArray(prompt.shots) ? prompt.shots.length : 0),
  0,
);

console.log(JSON.stringify({
  htmlBytes: Buffer.byteLength(html),
  dataBytes: Buffer.byteLength(dataSource),
  managerBytes: Buffer.byteLength(managerSource),
  prompts: database.prompts.length,
  shots: shotCount,
  sources: database.sources.length,
  inlineJavaScript: "syntax-ok",
  managerJavaScript: "syntax-ok",
  requiredElements: "ok",
}));
