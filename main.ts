import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Copy the pre-rendered front page into the grader's output directory.
// The source is resolved from this file's own URL, never from the
// process working directory: the grader runs `node /bot/main.ts`
// from a cwd that is not /bot.
const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
