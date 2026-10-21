# macro

Macro regime dashboard: FRED data ingestion with a local parquet cache,
growth/inflation z-score composites, 2×2 regime classification, horizon
projections, and a positioning journal. The goal is regime-based portfolio
positioning, not point forecasting.

## Modules

| Module | Role | Status |
|---|---|---|
| `series.py` | Series registry: the single source of truth for every indicator | ✅ |
| `fetch.py` | FRED client with incremental parquet cache, monthly alignment | ✅ |
| `transform.py` | yoy / ann3m / diff12 transforms and rolling z-scores | 🟡 in progress |
| `demo_data.py` | Synthetic fixture for running without a FRED key | ✅ |
| `regime.py` | 2×2 regime engine with configurable measurement plane | ⚪ designed, not yet committed |
| `horizon.py` | Horizon layers, calibrated projection, transition matrices | ⚪ designed, not yet committed |
| `plot.py` | Regime clock, heatmaps, skill-decay charts | ⚪ designed, not yet committed |
| `journal.py` | Append-only weekly regime journal | ⚪ designed, not yet committed |

## Setup

```bash
pip install -e ".[macro]"          # from the repo root
export FRED_API_KEY=...           # free key: https://fredaccount.stlouisfed.org/apikeys
```

Run scripts from this folder (`tools/macro/`) so that `import macro` resolves.
