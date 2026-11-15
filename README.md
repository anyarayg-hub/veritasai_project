# WSB Hype Crash Warning

**Veritas AI International High School Hackathon 2026 · AI + Finance track**

> When a stock suddenly gets hyped on r/wallstreetbets, can we predict whether it drops 10% or more within the next 5 trading days?

**This project is a prototype and is not financial advice.**

---

## At a glance

### 1. Who is it for?
A teenager with a new investing account. **The moment:** they see a stock flooded with rocket emojis on r/wallstreetbets and are about to buy into the hype. Before they do, they check our tool.

This fits the Finance track's challenge: helping a person make a **safer money decision**.

### 2. What goes in, and what comes out?
**In:** a Reddit hype spike, when a stock suddenly gets at least 5 posts in a day and 5× its usual attention.
**Out:** the chance the stock falls 10% or more within the next 5 trading days, a ⚠️ warning if that chance is 40% or higher, and specific reasons compared with past spikes.

**Real example: NEGG (Newegg), July 8, 2021.** 16× its usual Reddit attention, price already up 136% in a week, an extremely jumpy stock → **⚠️ 71% risk of a sharp drop.** It fell **45%** within 5 trading days.

### 3. Does it beat a simple baseline?
Yes, but only just against the best one. On the 24 test spikes (8 followed by a sharp drop):

| Method | Warnings | Drops caught | False alarms |
| --- | --- | --- | --- |
| Baseline: always warn | 24 | 8 of 8 | 16 |
| Baseline: warn if the stock is volatile | 7 | 6 of 8 | 1 |
| **Our model (warn at 40%+)** | 16 | **8 of 8** | 8 |

Our model catches every drop with half the false alarms of always warning. The volatility rule gives fewer false alarms but misses 2 drops. That a one-question rule comes this close is our main finding: volatility explains most drops after hype, and Reddit hype adds a little.

### 4. Where does it fail?
- **False alarm: PLTR, Aug 12, 2021** (54% risk, fell only 4.9%). A popular, moderately jumpy stock that didn't drop. The model leans heavily on volatility, so it over-warns on stocks like this.
- **Near miss: ASO, Jun 14, 2021** (43% risk, fell 10.7%). A calm stock that just crossed the 10% line. The model expects drops from jumpy stocks, so calm ones that drop get low scores.
- **Overall:** half its warnings were false alarms, and on the training months it was only slightly better than always warning, so our test result is probably optimistic.

## Status

| Step | Status |
| --- | --- |
| Load Reddit posts, find stock symbols, count mentions | ✅ Done |
| Detect hype spikes | ✅ Done (123 spikes) |
| Download prices, label sharp drops, build features | ✅ Done (82 examples) |
| Split by date, score simple rules, train models | ✅ Done |
| Checks: random seeds, shuffled labels, volatility rule, Reddit vs. no Reddit | ✅ Done |
| Warning cutoff chosen on training months (40%), final test result | ✅ Done |
| Plain-language warnings with specific reasons | ✅ Done |
| Interactive demo (Gradio app) | ✅ Done |
| Write-up and demo video | ⏳ In progress |

## Main finding

> **After a sudden Reddit hype spike, how volatile the stock already is explains most sharp drops.** Ranking spikes by volatility alone scores almost as well as our full model. Adding Reddit hype clues improved the model slightly (PR-AUC 0.90 → 0.93, catching about one more drop out of eight), but our test set is too small to be sure that improvement is real.

**Final result:** with a 40% warning cutoff chosen on the training months only, our model caught **all 8 sharp drops** in the test months with 16 warnings: half the false alarms of warning on every spike. It never missed a drop, but it was over-cautious: half its warnings were stocks that turned out fine.

**For a beginner investor:** if a stock is suddenly hyped on Reddit **and** it's already a wild, jumpy stock, be very careful. There's a high chance it falls 10% within a week.

## Results

Scored on the **test months (June 11 – August 16, 2021)**, which the models never saw during training: **24 hype spikes, 8 of which were followed by a sharp drop** (a fall of 10%+ within 5 trading days).

### Final result: the model vs. simple rules

A **simple rule** (baseline) is a single, hand-picked yes/no question that uses no AI, like "is the stock jumpier than usual?" Our model has to beat these to show it adds anything. If one obvious question gets the same answers, the model isn't needed.

The model gives every spike a **risk %** (the share of its 300 trees that vote "drop"). The **warning cutoff** turns that into a decision: risk of 40% or more → warn.

| Method (24 test spikes, 8 drops) | Warnings | Drops caught | False alarms | Precision | Recall |
| --- | --- | --- | --- | --- | --- |
| **Random forest, warn at 40%+ (final)** | 16 | **8 of 8** | 8 | 0.50 | **1.00** |
| Rule: volatile stock (above the median training spike) | 7 | 6 of 8 | 1 | 0.86 | 0.75 |
| Rule: volume 3× normal | *TODO* | *TODO* | *TODO* | *TODO* | *TODO* |
| Rule: already up 50%+ this week | *TODO* | *TODO* | *TODO* | *TODO* | *TODO* |
| Always warn | 24 | 8 of 8 | 16 | 0.33 | 1.00 |

- **Precision:** of the warnings, how many were real drops.
- **Recall:** of the real drops, how many got a warning.

**In plain words:**
- Against **always warning**, the model is a clear win: it catches the same 8 drops with half the false alarms.
- Against the **volatile-stock rule**, it's a trade-off: the rule gives far fewer false alarms (1) but **misses 2 drops**. The model misses nothing.
- None of the 8 spikes the model left unflagged dropped. So in the test months, **"no warning" was a reliable sign of safety**, while a warning meant "be careful" (a 50/50 chance of a sharp drop, up from 1 in 3).

### How we chose the 40% cutoff

We chose the cutoff **using only the training months** (46 spikes, about 18 drops). Each training spike was guessed by a forest that hadn't studied it (5-fold cross-validation), so the test months stayed untouched. Our rule, set in advance: **the highest cutoff that still catches about 80% of drops.**

| Cutoff | Warns on | Catches (recall) | Warnings right (precision) |
| --- | --- | --- | --- |
| 30% | 43 of 46 | 1.00 | 0.42 |
| 35% | 37 of 46 | 0.94 | 0.46 |
| **40%** | **30 of 46** | **0.78** | **0.47** |
| 45% | 24 of 46 | 0.61 | 0.46 |
| 50% | 19 of 46 | 0.56 | 0.53 |
| 55% | 11 of 46 | 0.33 | 0.55 |
| 60% | 7 of 46 | 0.17 | 0.43 |

We applied 40% **once** to the test months and didn't change it after seeing the result. Changing it afterwards would be tuning to the test.

### Why a false alarm is better than a missed drop (for a beginner)

| Mistake | What happens to the beginner | Cost |
| --- | --- | --- |
| False alarm (warned, but no drop) | Skips or waits on a stock that turned out fine | A missed gain; **no money lost** |
| Missed drop (no warning, but it fell) | Buys into the hype and loses 10%+ in a week | **Real money lost** |

A missed drop costs more, so the tool leans toward warning: better safe than sorry. But a tool that warns about everything gets ignored, like a car alarm that goes off every day. That's why we didn't pick 30% or 35%, which warn on 80–95% of spikes.

### Does Reddit hype add anything?

We trained the same random forest with and without the Reddit clues (10 random seeds each). **PR-AUC** measures how well a method ranks risky spikes above safe ones; random guessing scores about 0.33 here.

| What the model sees | PR-AUC (range over 10 seeds) | Recall |
| --- | --- | --- |
| **All 8 clues (Reddit + price)** | **0.93 (0.91–0.95)** | **0.88** |
| Price clues only, no Reddit | 0.90 (0.88–0.91) | 0.79 |
| Volatility only | 0.86 (0.86–0.87) | 0.50 |
| *No model: just sort by volatility* | *0.91* | |

Removing the Reddit clues makes the model slightly worse: about one fewer drop caught out of eight. Even the full model's worst seed (0.91) matches the price-only model's best (0.91). With only 8 drops in the test pile, this is a hint that hype helps, not proof.

### What the model relies on

Logistic regression weights (clues put on the same scale first; **+** raises risk, **−** lowers it):

| Clue | Weight | Meaning |
| --- | --- | --- |
| Volatility (20 days) | **+0.91** | Jumpy stocks drop 10% more easily (strongest clue) |
| Spike ratio (hype vs. normal) | **+0.73** | More sudden Reddit hype → more risk (second strongest) |
| Price change, last 20 days | +0.58 | Already up a lot this month → more risk |
| Price change, last 5 days | −0.44 | Overlaps with the clues above; read loosely |
| Share price (log) | −0.33 | Cheaper stocks are riskier |
| Market change, last 5 days | −0.27 | Rising market → less risk |
| Volume vs. normal | +0.09 | Barely matters |
| Number of posts (log) | +0.08 | Barely matters: how *sudden* the hype is matters, not the raw count |

### Why we kept all the clues

Volatility does most of the work, but we kept the Reddit clues in the final model:

1. **They still help:** recall 0.79 → 0.88 with them.
2. **Hype is the setting:** every example is already a Reddit hype spike. The question is *which* hyped stocks drop, and the answer needs both clue types.
3. **Removing clues after seeing test results would be tuning to the test.** Our clues were chosen before testing, and we kept it that way.

### Can we trust these results?

| Check | What we did | Result |
| --- | --- | --- |
| **Luck** | Retrained the random forest with 10 different random seeds | Precision 0.78–0.88, recall 0.88 every time, PR-AUC 0.91–0.95: stable |
| **Leakage** | Trained on shuffled (nonsense) labels, 20 times | PR-AUC 0.48 on average (best 0.87) vs. **0.94** with the real labels: the model learned something real |
| **Small test set** | 24 test spikes, 8 drops | One example moves recall by 12.5 points; even a nonsense model reached 0.87 once. We present the results modestly |
| **Harder training months** | Fair practice guesses on the training months (Feb–May) | Warnings were right 47% of the time vs. 39% for always warning: only slightly better. The test months (Jun–Aug) were much easier, so **our test result is probably optimistic** |

### Example: a textbook pump and dump

**NEGG (Newegg), July 8, 2021:** Reddit mentions spiked, the price was **up 136% in 5 days**, and the stock was extremely volatile. The model gave a **71% drop risk** and warned. **It fell 45% within 5 trading days.**

## Where it fails

| Spike | Model risk | What happened | Why we think it went wrong |
| --- | --- | --- | --- |
| **ASO**, Jun 14, 2021 | 0.43 | Fell 10.7%: a sharp drop | **Borderline.** A calm stock (low volatility) that only just crossed the 10% line. Missed at a 50% cutoff; caught at our 40% cutoff. The model expects drops from jumpy stocks |
| **PLTR**, Aug 12, 2021 | 0.54 | Fell only 4.9% | **False alarm.** Popular and moderately volatile, but nothing happened |
| **AMD**, Aug 3, 2021 | 0.51 | Up 24% the week before, then fell 7% | **False alarm.** It saw the run-up, but large companies rarely drop 10% in a week |

**Pattern:** the model relies heavily on volatility, so it misses drops in calm stocks and over-warns on popular, moderately jumpy ones.

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
7. **Split by date:** train on spikes before June 11, 2021, test on spikes after (24 spikes, 8 drops), with a 7-day gap. Never random.
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

## Limitations

- **One unusual period:** Jan–Aug 2021, dominated by the GameStop mania.
- **The data thins out:** ~4,200 posts a day in late January, ~80 by summer.
- **Small test pile:** 24 spikes with 8 drops; one example moves recall by 12.5 points.
- **The test result is probably optimistic:** the model was only slightly better than always warning on the training months; the summer test months were easier.
- **Over-cautious by design:** half the warnings in the test months were false alarms.
- **Drops mostly reflect jumpiness, not hype:** volatility alone nearly matches the full model; Reddit clues add only a little.
- **Big, quiet stocks count as spikes too:** a few posts about AAPL or NVDA can count; they're easy "safe" examples.
- **Delisted stocks are missing:** our symbol list and yfinance only cover stocks that still exist, so some of the worst drops may be left out.
- **Shouted posts are skipped** except for `$` tickers.
- **Mondays collect three days of posts**, so they may spike more often.
- **A warning sign, not a cause:** Reddit hype doesn't cause drops; we look for a signal that comes before them.

## Future work

- **Live Reddit data:** with Reddit's API, the tool could count mentions as they happen and warn about new hype spikes in real time. Prices and the 8 clues already work for any stock.
- **More time periods:** our data covers one unusual period (the 2021 meme-stock mania). Testing on other years would show whether the patterns hold in calmer markets.
- **More hype sources:** other subreddits, X/Twitter or StockTwits could catch hype that r/wallstreetbets misses.
- **More examples:** with more spikes, the test results would be less sensitive to a few lucky or unlucky cases.

## Repo layout

```
project.ipynb      the full pipeline, step by step, with results
wsb_utils.py       post-side helpers: tickers, trading days, mentions, spikes
model_utils.py     model-side helpers: prices, labels, features
app.py             the Gradio demo (loads the model the notebook saves)
requirements.txt   libraries to install
```

## How to run

1. Open `project.ipynb` in GitHub Codespaces (or Colab, with `wsb_utils.py` and `model_utils.py` in the same folder).
2. Install the libraries: `pip install -r requirements.txt`
3. Restart the kernel and **Run All**. No API keys are needed. Takes about a minute. The last cell saves the trained model to `demo_bundle.pkl`.
4. **To open the demo:** in a terminal, run `python app.py`, then open port 7860 (in Codespaces: the pop-up, or the **Ports** tab). Press Ctrl+C to stop it.

## Credits

- **Data:** Reddit WallStreetBets Posts (Gabriel Preda, Kaggle; OpenML ID 43373) · NASDAQ Trader symbol directory · Yahoo Finance via yfinance
- **Libraries:** pandas, NumPy, scikit-learn, yfinance, Gradio
- **AI tools:** Claude (Anthropic) was used to help write and debug code, review our pipeline for data leakage, and explain concepts. Every part of the code was reviewed and is understood by the team.