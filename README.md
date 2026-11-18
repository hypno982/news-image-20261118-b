[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/hypno982/news-image-20261118-b/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/hypno982/news-image-20261118-b/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

# The World in One Day — 18 November 2026

A single 1024x1024 PNG that reads as one newspaper front page for Wednesday
18 November 2026. The date is the loudest element on the page, and all 36
stories reported that day are on it, grouped under six continent labels:
**Americas · Europe · Africa · Middle East · Asia · Oceania**.

The page is built top to bottom as a masthead, a short inline world map strip
with six amber continent markers, a three-column grid of all 36 headlines
(worded exactly as reported, nothing dropped), and a footer repeating the date
and the six continents. Pure HTML and CSS with a hand-drawn inline SVG map —
no script, no network, no external font, no remote image.

Everything is deterministic: rendering is a fixed viewport, a fixed clip and no
animation or randomness, so the same card always produces the same bytes.

## Build

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` checks that `entry.png` is a whole PNG (8-byte signature, IHDR first,
IEND chunk ending exactly at EOF) before copying it into the output directory,
and warns on stderr if it exceeds 1 MiB.

To regenerate the PNG itself from `card.html`:

```sh
python3 render.py
```

`render.py` renders with Playwright at a 1024x1024 viewport and `device_scale_factor 1`,
raises on any page or console error, and asserts that all 36 headlines sit inside
the frame and that the page does not overflow.

## Files

| File | Role |
| --- | --- |
| `card.html` | The front page: 36 headlines, six continents, world map strip |
| `render.py` | Renders `card.html` to `entry.png`, with layout assertions |
| `main.ts` | Validates the PNG and publishes it to `MAKEFUN_OUTPUT_DIR` |
| `entry.png` | The submission image, 1024x1024 |
