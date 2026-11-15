# WSB Hype Drop Warning

Track: Finance

This project is a prototype and is not financial advice. Full details, tables and code are in the README.

## The problem

Beginners buy stocks because they're suddenly hyped on Reddit's r/wallstreetbets. Then they watch them fall. Here's the thing: they've got no quick way to spot which hyped stocks are actually dangerous. That's the real problem.

## What we built

We made a tool. You feed it a Reddit hype spike and it tells a beginner how likely the stock is to drop 10% or more within a week. You get a warning and plain-language reasons why. The demo app is pretty straightforward. Pick a real spike, see the warning, compare it to what actually happened.

## What we added

Our own idea came first. We dug into a bigger question: is it the Reddit hype that predicts a drop, or is it just how jumpy the stock already is? We also checked whether the model treats cheap stocks more harshly.

## How it works

We took 53,187 r/wallstreetbets posts from 2021 and turned them into 82 hype spikes. Each spike got 8 clues pulled from Reddit and price data. We trained a random forest on the earlier months. The later months? We tested on those without the model ever seeing them. And the warning cutoff was chosen blind, no peeking at the test results.

## Results

A simple rule worked okay. Just check volatility and warn if it's high. That caught 6 of 8 sharp drops in the test months. Our model? It caught all 8. The catch is half its warnings were false alarms. Volatility explains most drops. Reddit hype adds a little something, but not much. The model leans heavily on volatility, so it over-warns on popular stocks that bounce around moderately, like PLTR. One more thing: the test months were easier than the training months.