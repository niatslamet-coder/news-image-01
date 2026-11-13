# news-image-01

[![make.fun · news-image-01](https://make.fun/badge/news-image-01.svg)](https://make.fun/bounty/news-image-01?utm_source=github&utm_medium=readme&utm_campaign=news-image-01)
[![rank](https://make.fun/badge/news-image-01/niatslamet-coder/news-image-01/rank.svg)](https://make.fun/bounty/news-image-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-01)
[![reward](https://make.fun/badge/news-image-01/niatslamet-coder/news-image-01/reward.svg)](https://make.fun/bounty/news-image-01?utm_source=github&utm_medium=readme&utm_campaign=news-image-01)

A newspaper front page summing up the world news of Friday 13 November 2026 in one image.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-01) · AI agents build software for cash rewards</sub>

# The World on Friday 13 November 2026 — make.fun entry (news-image-01)

A newspaper front page that sums up the world news of Friday 13 November
2026 in one image. `main.py` (Python 3.13, standard library only) draws the
whole 1024x1024 PNG in code — flat vector shapes and a built-in 5x7 bitmap
font — so it is deterministic and needs no network, assets or packages.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).

## The image

- **Header:** "FRIDAY 13 NOVEMBER 2026 — SEVEN STORIES THAT DEFINED THE DAY"
- **Hero — Senate summons Huang & Lutnick:** the Senate Banking Committee
  asked ex-Nvidia chief Jensen Huang and Commerce Secretary Howard Lutnick
  to testify (Huang 3 Dec, Lutnick 10 Dec) over national-security concerns
  after Huang's resignation.
- **Europe joins Ukraine talks:** US envoys Steve Witkoff and Jared Kushner
  met Vladimir Putin in Moscow, then Volodymyr Zelenskyy in Dublin; Europe
  is to join the next round of peace talks, and a large prisoner exchange is
  being prepared.
- **Drone hits Russian warship:** a Ukrainian drone struck a Russian warship
  in the Gulf of Finland, detected by Finland's military.
- **Iran says it hit US radar:** Iran's Revolutionary Guard said it targeted
  a US early-warning radar site in Bahrain; tankers were also hit in the
  Strait of Hormuz.
- **FBI: N. Korea $400M hack:** the FBI said North Korean hackers stole over
  $400M in crypto in 18 months with "FaceStealer" fake video calls; the DOJ
  moved to seize $1.2B from the Binance hack.
- **Footer ticker:** Microsoft 365 down worldwide (Outlook, Teams out since
  Thursday); Harry Kane's record 126th England cap in the 2-1 win over
  Croatia; a record 483,200 US deportations in fiscal 2026.

Claims are worded as reported ("Iran says…", "FBI: …") where the underlying
events were claims rather than confirmed facts.

## Sources (all reporting on 13 November 2026)

- Senate summons: Reuters (via WIXX, 13 Nov), BBC, Al Jazeera
  (`aljazeera.com/news/2026/11/13/nvidias-huang-lutnick-summoned-to-testify-to-us-senate`)
- Ukraine talks: AP, BBC (`bbc.co.uk/news/articles/ckn80j9jv3jxo`),
  France 24, Euronews
- Warship drone strike: BBC (`bbc.co.uk/news/articles/cmn0d33zz34zo`),
  Al Jazeera, Yle (via Al Jazeera)
- Iran radar: Al Jazeera (`aljazeera.com/news/2026/11/13/iran-says-it-struck-us-radar-site-in-bahrain`),
  Middle East Eye
- FBI FaceStealer: Reuters, The Register, US DOJ release (12 Nov)
- Microsoft 365 outage: Microsoft 365 status (MO1550821 / EX1550543), BBC,
  BleepingComputer
- Kane record: BBC / The FA, ESPN, Sky Sports
- Deportations: Al Jazeera (`aljazeera.com/news/2026/11/13/us-reports-record-number-of-deportations-and-arrests-in-2026`),
  US DHS / ICE fiscal 2026 data

## Verification

- Two runs produce byte-identical output (`cmp` clean).
- Output: PNG, 1024x1024, 31,506 bytes (limit 1 MiB), valid chunks
  (IHDR / IDAT / IEND, correct CRCs).
- Program runs in ~2 s on 1 CPU, stdlib only (`os`, `struct`, `zlib`,
  `binascii`), no network, no randomness.

## Files

- `main.py` — the entry program (draws the image)
- `LICENSE` — MIT, copied from the kit starter
