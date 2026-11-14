# WSB Hype Crash Warning

**Veritas AI International High School Hackathon 2026 · AI + Finance track**

> When a stock suddenly gets hyped on r/wallstreetbets, can we predict whether it drops 10% or more within the next 5 trading days?

**This project is a prototype and is not financial advice.**

---

## Who it's for

A teenager with a new investing account who sees a stock flooded with rocket emojis on Reddit and is about to buy. Our tool looks at a hype spike and returns a sharp-drop risk with plain-language reasons (for example: "mentions 29× normal, price already up 70% this week"), so they can think twice before buying into the hype.

This fits the finance track's challenge: helping a person make a **safer money decision**, and showing the model beats simple rules.

## Status

| Step | Status |
| --- | --- |
| Load Reddit posts, find stock symbols, count mentions | ✅ Done |
| Detect hype spikes | ✅ Done (123 spikes) |
| Download prices, label sharp drops, build features | ✅ Done (82 examples) |
| Split by date, score simple rules, train models | ✅ Done (first results below) |
| Checks: random seeds, shuffled labels, volatility rule | ⏳ Saturday night |
| Warning cutoff, failure analysis, plain-language reasons | ⏳ Sunday morning |
| Write-up and demo video | ⏳ Sunday afternoon |

## First results (preliminary)

Scored on the **test months (June 11 – August 16, 2021)**, which the models never saw during training: 28 hype spikes, 9 of which were followed by a sharp drop.

| Method | Precision | Recall | Warnings | PR-AUC |
| --- | --- | --- | --- | --- |
| Always warn | 0.32 | 1.00 | 28 of 28 | |
| Rule: volume 3× normal | 0.71 | 0.56 | 7 of 28 | |
| Rule: already up 50%+ this week | 1.00 | 0.22 | 2 of 28 | |
| Logistic regression | 0.57 | 0.44 | 7 of 28 | 0.65 |
| **Random forest** | **0.80** | **0.89** | 10 of 28 | **0.92** |

- **Precision:** of the spikes we warned about, how many actually dropped.
- **Recall:** of the spikes that dropped, how many we warned about.
- **PR-AUC:** how well the model ranks risky spikes above safe ones. Random guessing scores about 0.32 here.

**In plain words:** the random forest gave 10 warnings, 8 of them correct, and caught 8 of the 9 sharp drops. The best simple rule (volume 3× normal) caught 5 of 9.

**Why "preliminary":** results this far above the baselines can mean information from the future leaked into training, and with only 9 drops in the test pile, one example moves recall by 11 points. Before we trust these numbers we are checking:

1. **Luck:** rerun the random forest with 10 different random seeds.
2. **Leakage:** train on shuffled labels; the score should fall to about random (0.32).
3. **What it learns:** feature importance, plus a fairer simple rule, "warn if the stock is more volatile than usual." We suspect much of the signal is that jumpy stocks drop 10% more easily, hype or not.

## Data

| Source | What we use it for |
| --- | --- |
| [Reddit WallStreetBets Posts](https://www.kaggle.com/datasets/gpreda/reddit-wallstreetsbets-posts) (Gabriel Preda, Kaggle), loaded from the [OpenML mirror, ID 43373](https://www.openml.org/d/43373) | 53,187 posts: title, body, score, comments, time |
| [NASDAQ Trader symbol directory](https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt) | 13,285 real US stock symbols, to tell real tickers from words |
| [yfinance](https://github.com/ranaroussi/yfinance) | Daily prices and volume for each hyped stock, plus SPY for the market |

**Date range:** one stray post from Sept 29, 2020, then continuous posts from **Jan 28 to Aug 16, 2021**. The data thins out a lot: about 4,200 posts a day in late January, about 80 a day by summer.

## How it works

1. **Find stock symbols in each post.** We look for `$TICKER` (any case) and 2–5 letter capital words, keep only real symbols, and drop slang and English words (`DD`, `YOLO`, `RH` = Robinhood, `HF` = hedge funds, `ALL`, `NOW`...). Single letters need a `$`. Posts written mostly in capitals only count `$` tickers. Each stock counts once per post.
2. **Put each post on the right trading day.** Posts after the 4 PM ET close move to the next day; weekend posts move to Monday.
3. **Count mentions** per stock per trading day.
4. **Find hype spikes:** at least **5 posts** about a stock in a day and at least **5×** its average over the previous **14 calendar days**. Result: **123 spikes**.
5. **Download prices** for the spiked stocks (50 of 51; HOOD only listed on July 29, 2021).
6. **Build one example per spike,** keeping only the first spike per stock per week (one hype wave = one example): **82 examples**.
   - **Label:** a **sharp drop** = the lowest price in the next 5 trading days is 10%+ below the spike day's close. 28 of 82 spikes (34%).
   - **Features** (all known at the spike day's close): mentions, spike size, 5- and 20-day price change, volume vs. normal, 20-day volatility, share price, S&P 500 change.
7. **Split by date:** train on spikes before June 11, 2021 (47 spikes, 18 drops), test on spikes after (28 spikes, 9 drops), with a 7-day gap. Never random.
8. **Score simple rules, then train** logistic regression and a random forest with balanced class weights.

### Choices we made, and why

| Choice | Why |
| --- | --- |
| Spike = 5× normal with at least 5 posts | 5× keeps spikes clearly sudden. A 10-post minimum gave only 46 spikes, because later months have ~80 posts a day |
| Sharp drop = 10%+ in 5 trading days | At 20%, only 7 of 82 spikes counted, too few to test fairly. A 10% loss in one week is about a year's average market return. Chosen **before** training any model |
| Split by date with a 7-day gap | Like real use: learn from the past, predict the future. The gap stops training labels from peeking into the test period |
| Use the `created` timestamp (UTC) | The time zone of the `timestamp` column is unknown |

### Mistakes we found and fixed

| Problem | What we saw | Fix |
| --- | --- | --- |
| Fake spikes at the start of the data | GME, AMC, BB and NOK "spiked" on Jan 28 from an average of 0, because collection only started that day | Start at the first day with 100+ posts and use the next 14 days only as history |
| Words counted as stocks | `AIN` (from "AIN'T"), `AWAY`, `BEAT`, single letters, `RH` (Robinhood), `HF` (hedge funds), `SPY`, `AKA`, `PC`, `IP` (intellectual property)... | More stopwords after each top-40 check, single letters need `$`, apostrophes don't split words, shouted posts only count `$` tickers |
| Wrong baseline average | Days with zero mentions were skipped, so averages were too high | Average over a full calendar-day grid with zeros |
| Hype counted too early | Posts after the 4 PM close counted toward that day's closing price | Move them to the next trading day |
| Too few spikes | Only 46 with a 10-post minimum | Lowered the minimum to 5 posts, kept the 5× jump (123 spikes) |
| Too few drops | 7 of 82 at a 20% line | 10% line (28 drops), fixed before training |
| Wrong labels in the split | The split ran before the relabel cell, so it used the old 20% labels | Reordered the notebook so every cell runs top to bottom |

## Where it fails

*TODO: 2–3 real test examples the model got wrong, and why.*

## Limitations

- **One unusual period:** Jan–Aug 2021, dominated by the GameStop mania.
- **The data thins out:** ~4,200 posts a day in late January, ~80 by summer.
- **Small test pile:** 28 spikes with 9 drops; one example moves recall by 11 points.
- **Drops may reflect jumpiness, not hype:** volatile stocks fall 10% in a week more easily; our volatility check will show how much this explains.
- **Big, quiet stocks count as spikes too:** a few posts about AAPL or NVDA can count; they're easy "safe" examples.
- **Delisted stocks are missing:** our symbol list and yfinance only cover stocks that still exist, so some of the worst drops may be left out.
- **Shouted posts are skipped** except for `$` tickers.
- **Mondays collect three days of posts**, so they may spike more often.
- **A warning sign, not a cause:** Reddit hype doesn't cause drops; we look for a signal that comes before them.

## Repo layout

```
project.ipynb      the full pipeline, step by step, with results
wsb_utils.py       post-side helpers: tickers, trading days, mentions, spikes
model_utils.py     model-side helpers: prices, labels, features
requirements.txt   libraries to install
```

## How to run

1. Open `project.ipynb` in GitHub Codespaces (or Colab, with `wsb_utils.py` and `model_utils.py` in the same folder).
2. Install the libraries: `pip install -r requirements.txt`
3. Restart the kernel and **Run All**. No API keys are needed. Takes about a minute.


## Credits

- **Data:** Reddit WallStreetBets Posts (Gabriel Preda, Kaggle; OpenML ID 43373) · NASDAQ Trader symbol directory · Yahoo Finance via yfinance
- **Libraries:** pandas, NumPy, scikit-learn, yfinance
- **AI tools:** Claude (Anthropic) was used to help clean up functions,debug code, review our pipeline for data leakage, and explain concepts. Every part of the code was reviewed and is understood by the team.