# finml-research

![CI](https://github.com/CeyhanTurnali/finml-research/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Applied research at the intersection of finance and machine learning:
portfolio construction, financial NLP, and LLM systems for regulated finance.

Every post in [`blog/`](blog/) ships with the code needed to reproduce its
results. [`tools/`](tools/) holds the tools I use in my own investment
research.

## Posts

| # | Title | Status | Code |
|---|---|---|---|
| 01 | Your Optimizer Is a Hidden Portfolio Constraint | 🟡 in progress | [`blog/01-optimizer-hidden-constraint`](blog/01-optimizer-hidden-constraint/) |

## Tools

| Tool | What it does | Status |
|---|---|---|
| [`macro`](tools/macro/) | Macro regime dashboard: FRED data, growth/inflation composites, regime classification | 🟡 in progress |

## Conventions

- **Results come from scripts, not notebooks.** Experiments append to a
  `results.json`; figures are regenerated from it.
- **Frozen inputs.** Universes and splits are fixed and hashed, so later runs
  are comparable with earlier ones.
- **Product code lives in product repos.** When a post is about a system that
  has its own repository, the post folder holds only its experiments and
  links to the system.

## Development

```bash
pip install -e ".[blog01,macro,dev]"   # or just the extra you need
pytest
ruff check .
```

## License

MIT — see [LICENSE](LICENSE).
