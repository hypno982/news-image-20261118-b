#!/usr/bin/env python3
"""Render card.html to a deterministic 1024x1024 entry.png.

Asserts that all 36 headlines are present and fully inside the frame,
that the page does not overflow, and that no page/console error fired.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
CARD = HERE / "card.html"
OUT = HERE / "entry.png"
SIZE = 1024
HEADLINES = 36

# Count .hl elements fully inside the 1024x1024 frame; report overflow.
PROBE = """
() => {
  const vw = 1024, vh = 1024;
  const els = Array.from(document.querySelectorAll('.hl'));
  let inside = 0, worst = null;
  for (const el of els) {
    const r = el.getBoundingClientRect();
    const ok = r.width > 0 && r.height > 0 &&
               r.top >= -0.5 && r.left >= -0.5 &&
               r.bottom <= vh + 0.5 && r.right <= vw + 0.5;
    if (ok) inside++; else if (!worst) worst = el.textContent.trim().slice(0, 60);
  }
  return {
    inside, total: els.length, worst,
    scrollH: document.body.scrollHeight,
    scrollW: document.body.scrollWidth,
    docH: document.documentElement.scrollHeight,
    docW: document.documentElement.scrollWidth,
  };
}
"""


def main() -> int:
    errors = []

    def on_console(msg):
        if msg.type in ("error", "warning"):
            errors.append(f"console.{msg.type}: {msg.text}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=["--force-color-profile=srgb", "--disable-lcd-text"])
        page = browser.new_page(
            viewport={"width": SIZE, "height": SIZE},
            device_scale_factor=1,
        )
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        page.on("console", on_console)

        page.goto(CARD.as_uri(), wait_until="load")
        page.wait_for_timeout(700)

        probe = page.evaluate(PROBE)
        print(f"headlines inside frame: {probe['inside']}/{probe['total']}")
        print(f"body scrollHeight: {probe['scrollH']}  scrollWidth: {probe['scrollW']}")
        print(f"doc  scrollHeight: {probe['docH']}  scrollWidth: {probe['docW']}")

        if probe["total"] != HEADLINES:
            raise RuntimeError(
                f"expected {HEADLINES} headlines in DOM, found {probe['total']}")
        if probe["inside"] != HEADLINES:
            raise RuntimeError(
                f"{HEADLINES - probe['inside']} headline(s) cut off; "
                f"first: {probe['worst']}")
        if max(probe["scrollH"], probe["scrollW"],
               probe["docH"], probe["docW"]) > SIZE:
            raise RuntimeError(
                f"page overflows the {SIZE}x{SIZE} frame: "
                f"{probe['docW']}x{probe['docH']}")

        page.screenshot(path=str(OUT), clip={"x": 0, "y": 0,
                                            "width": SIZE, "height": SIZE})
        browser.close()

    if errors:
        raise RuntimeError("page reported errors:\n  " + "\n  ".join(errors))

    data = OUT.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("output is not a PNG")
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    if (w, h) != (SIZE, SIZE):
        raise RuntimeError(f"output is {w}x{h}, expected {SIZE}x{SIZE}")

    print(f"wrote {OUT}")
    print(f"bytes: {len(data)}  pixels: {w}x{h}")
    if len(data) >= 1048576:
        print("WARNING: over 1 MiB", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
