"""
WSB Hype Drop Warning: a small Gradio demo.

Run the notebook first (it saves demo_bundle.pkl), then in the terminal:
    python app.py
Codespaces forwards port 7860: open it from the pop-up or the Ports tab.

This project is a prototype and is not financial advice.
"""

import pickle

import numpy as np
import pandas as pd

BUNDLE_PATH = "demo_bundle.pkl"
HIGH, LOW = 75, 25          # percentiles that count as "unusual" compared with past spikes


def load_bundle(path=BUNDLE_PATH):
    with open(path, "rb") as f:
        return pickle.load(f)


def pct(train_x, col, value):
    """Percent of past (training) hype spikes with a value at or below this one."""
    return int(round((train_x[col] <= value).mean() * 100))


def than(p, word):
    """'more than 85% of past spikes', or 'than any past spike we studied' at the extremes."""
    if p >= 100:
        return f"{word} than any hype spike we studied"
    return f"{word} than {p}% of past spikes"


def signals(row, train_x):
    """
    Specific warning signs and calming signs for one spike, each compared with the
    hype spikes the model studied. Returns two lists of (strength, sentence), strongest first.
    """
    warn, calm = [], []

    # 1. How sudden the hype is (higher = riskier)
    p = pct(train_x, "spike_ratio", row.spike_ratio)
    if p >= HIGH:
        warn.append((p, f"**Sudden hype:** {row.mentions} posts in one day, {row.spike_ratio:.0f}× its usual "
                        f"Reddit attention. That's {than(p, 'a bigger jump')}."))
    elif p <= LOW:
        calm.append((100 - p, f"**Mild hype:** {row.spike_ratio:.0f}× its usual Reddit attention, "
                              f"{than(100 - p, 'a smaller jump')}."))

    # 2. Run-up over the past week (higher = riskier)
    p = pct(train_x, "ret_5d", row.ret_5d)
    if p >= HIGH:
        warn.append((p, f"**Already ran up {row.ret_5d:+.0%} in the past week,** {than(p, 'more')}. "
                        f"People buying now may be buying near the top."))
    elif p <= LOW:
        calm.append((100 - p, f"**No big run-up:** the price changed {row.ret_5d:+.0%} this week, so there's less "
                              f"of a jump to unwind."))

    # 3. Run-up over the past month (higher = riskier)
    p = pct(train_x, "ret_20d", row.ret_20d)
    if p >= HIGH:
        warn.append((p, f"**Up {row.ret_20d:+.0%} over the past month,** {than(p, 'a bigger climb')}."))
    elif p <= LOW:
        calm.append((100 - p, f"**Modest month:** {row.ret_20d:+.0%} over the past month, "
                              f"{than(100 - p, 'less')}."))

    # 4. How jumpy the stock is (higher = riskier); the model's strongest clue
    p = pct(train_x, "volatility_20d", row.volatility_20d)
    if p >= HIGH:
        warn.append((p + 1, f"**Very jumpy stock:** it usually moves about {row.volatility_20d:.0%} a day, "
                            f"{than(p, 'more')}. For a stock like this, a 10% fall can happen in a "
                            f"single bad day or two."))
    elif p <= LOW:
        calm.append((100 - p + 1, f"**Steady stock:** it usually moves only about {row.volatility_20d:.1%} a day, "
                                  f"{than(100 - p, 'calmer')}. A 10% fall in a week would be unusual "
                                  f"for it."))

    # 5. Trading volume (higher = riskier)
    p = pct(train_x, "volume_ratio", row.volume_ratio)
    if p >= HIGH:
        warn.append((p, f"**Trading frenzy:** {row.volume_ratio:.1f}× its normal number of shares traded, "
                        f"{than(p, 'busier')}. Frenzies like this often fade."))
    elif p <= LOW:
        calm.append((100 - p, f"**Normal trading:** volume was {row.volume_ratio:.1f}× usual, "
                              f"{than(100 - p, 'quieter')}."))

    # 6. Share price (lower = riskier)
    price = float(np.exp(row.log_price))
    p = pct(train_x, "log_price", row.log_price)
    if p <= LOW and price < 20:
        warn.append((100 - p, f"**Cheap stock at ${price:.2f} a share,** {than(100 - p, 'cheaper')}. "
                              f"Low-priced stocks are easier to pump and dump."))
    elif p >= HIGH and price > 50:
        calm.append((p, f"**Higher-priced stock at ${price:,.0f} a share,** usually a larger, more established "
                        f"company that moves less on Reddit hype."))

    # 7. The whole market (falling = riskier)
    p = pct(train_x, "market_ret_5d", row.market_ret_5d)
    if p <= LOW:
        warn.append((100 - p, f"**The whole market was falling:** the S&P 500 changed {row.market_ret_5d:+.1%} "
                              f"this week."))
    elif p >= HIGH:
        calm.append((p, f"**The whole market was rising:** the S&P 500 changed {row.market_ret_5d:+.1%} "
                        f"this week."))

    warn.sort(key=lambda t: -t[0])
    calm.sort(key=lambda t: -t[0])
    return [s for _, s in warn], [s for _, s in calm]


def make_warn_text(bundle):
    model, test = bundle["model"], bundle["test"]
    features, cutoff, train_x = bundle["features"], bundle["cutoff"], bundle["train_x"]

    # How the model did on the test months at this cutoff (used in the wording below)
    flagged = model.predict_proba(test[features])[:, 1] >= cutoff
    dropped_all = (test["min_future_ret"] <= -0.10).to_numpy()
    n_warn, n_warn_right = int(flagged.sum()), int((flagged & dropped_all).sum())
    n_quiet, n_quiet_dropped = int((~flagged).sum()), int((~flagged & dropped_all).sum())

    def warn_text(choice):
        if not choice:
            return "Pick a stock from the list."
        ticker, date = choice.split(" — ")
        rows = test[(test["ticker"] == ticker) & (test["date"] == pd.Timestamp(date))]
        row = rows.iloc[0]
        risk = model.predict_proba(rows[features])[:, 1][0]
        warn, calm = signals(row, train_x)

        day = pd.Timestamp(date).strftime("%B %-d, %Y")
        lines = [f"## {ticker} · {day}",
                 f"{row.mentions} r/wallstreetbets posts mentioned {ticker} that day, "
                 f"{row.spike_ratio:.0f}× its usual attention.", ""]

        if risk >= cutoff:
            level = "High" if risk >= 0.6 else "Elevated"
            lines += [f"### ⚠️ {level} risk of a sharp drop: {risk:.0%}",
                      f"Our model thinks {ticker} has a {risk:.0%} chance of falling 10% or more within the next "
                      f"5 trading days. When it warned during testing, the stock dropped that much "
                      f"{n_warn_right} times out of {n_warn}, so a warning means *be careful*, not *it will "
                      f"definitely fall*.", ""]
        else:
            lines += [f"### ✅ Lower risk: {risk:.0%}",
                      f"Our model gives {ticker} a {risk:.0%} chance of falling 10% or more within the next "
                      f"5 trading days. In testing, "
                      + (f"none of the {n_quiet}" if n_quiet_dropped == 0 else f"{n_quiet_dropped} of the {n_quiet}")
                      + f" spikes below our {cutoff:.0%} line dropped that much, but lower risk isn't no risk.", ""]

        warn_block = (["**Warning signs** (compared with the hype spikes our model studied):"]
                      + [f"- {s}" for s in warn[:3]] + [""]) if warn else []
        calm_block = (["**Calming signs** (compared with the hype spikes our model studied):"]
                      + [f"- {s}" for s in calm[:3]] + [""]) if calm else []
        # Lead with the signs that explain the verdict
        lines += (warn_block + calm_block) if risk >= cutoff else (calm_block + warn_block)
        if not warn and not calm:
            lines += ["Nothing about this spike stands out from a typical Reddit hype spike.", ""]

        fell = row.min_future_ret
        dropped = fell <= -0.10
        right = (risk >= cutoff) == dropped
        lines += ["---",
                  f"**What actually happened:** over the next 5 trading days, {ticker}'s lowest price was "
                  f"{fell:+.0%} from that day's close → " + ("**a sharp drop**." if dropped else "**no sharp drop**."),
                  "",
                  "✅ The model got this one right." if right else
                  ("❌ False alarm: the model warned, but the stock held up." if risk >= cutoff else
                   "❌ Missed: the model didn't warn, but the stock dropped."),
                  "",
                  "*Prototype, not financial advice. These spikes are from June–August 2021, months the model "
                  "never trained on.*"]
        return "\n".join(lines)

    return warn_text


def build_demo(bundle):
    import gradio as gr

    test = bundle["test"].sort_values("date")
    choices = [f"{r.ticker} — {r.date.date()}" for r in test.itertuples()]

    return gr.Interface(
        fn=make_warn_text(bundle),
        inputs=gr.Dropdown(choices, label="Pick a hyped stock (June–August 2021)"),
        outputs=gr.Markdown(),
        title="WSB Hype Drop Warning",
        description="When a stock suddenly gets hyped on r/wallstreetbets, how likely is it to drop "
                    "10% or more within a week? Pick a real spike to see the warning, the reasons, "
                    "and what actually happened.",
    )


if __name__ == "__main__":
    build_demo(load_bundle()).launch(server_name="0.0.0.0", server_port=7860)