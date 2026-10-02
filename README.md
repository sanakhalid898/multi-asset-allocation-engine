# Multi-Asset Portfolio Decision System

A production-grade decision-support system for multi-asset allocation: Bayesian capital market assumptions, mandate-constrained optimization, and pre-trade impact analysis.

> Status: Phase 1 (live skeleton) in progress.

## Structure

```
src/
  ingest/      # price + macro data loaders
  db/          # models, connection, migrations
  analytics/   # returns, covariance, risk
  optimize/    # portfolio optimizer
  app/         # dashboard
tests/
config/        # mandate + universe config
notebooks/     # exploration only, not production code
docs/          # architecture diagram, memo
.github/workflows/
```

## Setup

_TBD_
