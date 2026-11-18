/**
 * entry.png: a 1024x1024 newspaper front page for 18 November 2026 —
 * 36 headlines from six continents under a large date block and map strip.
 * Validates the PNG is whole, then copies it to MAKEFUN_OUTPUT_DIR (/output).
 */
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const SIZE_WARN = 1048576;
const IHDR_LEN = 13;

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const dest = join(outDir, "entry.png");

/** Throw unless `p` is a whole, well-formed PNG. Returns width * height. */
function assertWholePng(p: string): number {
  const buf = readFileSync(p);
  if (buf.length < 8 + 12 + IHDR_LEN + 12) {
    throw new Error(`${p}: too short to be a PNG (${buf.length} bytes)`);
  }
  if (!buf.subarray(0, 8).equals(SIG)) {
    throw new Error(`${p}: bad PNG signature`);
  }
  // IHDR must come first, with its required 13 bytes of payload.
  if (buf.toString("latin1", 12, 16) !== "IHDR") {
    throw new Error(`${p}: first chunk is not IHDR`);
  }
  if (buf.readUInt32BE(8) !== IHDR_LEN) {
    throw new Error(`${p}: IHDR length ${buf.readUInt32BE(8)}, expected ${IHDR_LEN}`);
  }

  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  const bitDepth = buf[24];
  const colorType = buf[25];
  if (!width || !height) {
    throw new Error(`${p}: IHDR declares zero dimension (${width}x${height})`);
  }
  if (bitDepth !== 8) {
    throw new Error(`${p}: bit depth ${bitDepth}, expected 8`);
  }
  if (![0, 2, 3, 4, 6].includes(colorType)) {
    throw new Error(`${p}: invalid colour type ${colorType}`);
  }

  // Chunks must tile the file exactly and IEND must land on EOF.
  let at = 8;
  let last = "";
  while (at + 12 <= buf.length) {
    const len = buf.readUInt32BE(at);
    const type = buf.toString("latin1", at + 4, at + 8);
    at += 12 + len;
    if (at > buf.length) {
      throw new Error(`${p}: ${type} chunk overruns EOF (${len} bytes declared)`);
    }
    last = type;
    if (type === "IEND") break;
  }
  if (last !== "IEND") {
    throw new Error(`${p}: no IEND chunk (last chunk was ${last || "none"})`);
  }
  if (at !== buf.length) {
    throw new Error(`${p}: ${buf.length - at} trailing byte(s) after IEND`);
  }
  return width * height;
}

const pixels = assertWholePng(src);
mkdirSync(outDir, { recursive: true });
copyFileSync(src, dest);

const bytes = statSync(dest).size;
console.log(`entry.png -> ${dest} (${bytes} bytes, ${pixels} px)`);
if (bytes > SIZE_WARN) {
  console.error(`warning: entry.png is ${bytes} bytes, over ${SIZE_WARN}`);
}
