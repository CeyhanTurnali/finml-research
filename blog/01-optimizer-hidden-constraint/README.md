# 01 — Your Optimizer Is a Hidden Portfolio Constraint

**Status:** 🟡 in progress; experiments have not run yet.

## The question

The global minimum-variance (GMV) problem is convex, so every optimizer that
converges reaches the same weights. Yet with an estimated covariance matrix,
the exact optimum is the overfit one: it concentrates weight in the
low-variance directions that the sample estimates worst.

This post measures what happens *before* convergence. The optimizer's path
(starting point, step budget, preconditioner) decides how much estimation
noise the portfolio absorbs. Early-stopped gradient descent behaves like
spectral shrinkage towards 1/N; Adam, being coordinate-wise, need not. That
choice acts as a portfolio constraint nobody wrote down.

## Setup

- **Problem:** GMV (primary, out-of-sample volatility as the main metric),
  plus a short mean-variance extension reporting Sharpe.
- **Universe:** ~100 large-cap S&P 500 stocks, list frozen and hashed.
- **Optimizers:** projected gradient descent, momentum, Adam (numpy).
- **Baselines:** exact GMV, 1/N, Ledoit-Wolf GMV, long-only GMV.
- **Evaluation:** monthly walk-forward; stopping points and risk aversion are
  chosen on 2010–2017 only and tested on 2018–2025.

## Layout (filled in as the work lands)

```
hidden_constraint/  objective, optimizers (+ data, baselines, metrics, backtest to come)
experiments/        one script per experiment; each writes results/ and figures/
tests/              E0: every optimizer reaches the closed-form optimum
```

## Install

```bash
pip install -e ".[blog01,dev]"   # from the repo root
```