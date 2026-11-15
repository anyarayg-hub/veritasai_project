# WSB Hype Drop Warning

**Track:** Finance

*This project is a prototype and is not financial advice. Full details, tables and code are in the [README](README.md).*

## The problem

Beginners who buy a stock because it's suddenly hyped on Reddit's r/wallstreetbets often buy right before it falls. They have no quick way to tell which hyped stocks are dangerous.

## What we built

A tool that takes a Reddit hype spike and tells a beginner how likely the stock is to fall 10% or more within a week, with a warning and plain-language reasons. A demo app lets you pick a real spike and see the warning next to what actually happened.

## What we added

Our own idea. We also asked our own question: is it the Reddit hype that predicts a drop, or just how jumpy the stock already is? And we checked whether the model is harsher on cheap stocks.

## How it works

We turned 53,187 r/wallstreetbets posts from 2021 into 82 hype spikes, gave each one 8 clues from Reddit and price data, and trained a random forest on the earlier months. We tested it on later months it never saw, and chose its warning cutoff without looking at the test.

## Results

The best simple rule ("warn if the stock is volatile") caught 6 of 8 sharp drops in the test months. Our model caught all 8, but half its warnings were false alarms. Volatility explains most drops; Reddit hype adds a little. The model leans on volatility, so it over-warns on popular, moderately jumpy stocks like PLTR, and the test months were easier than the training months.
