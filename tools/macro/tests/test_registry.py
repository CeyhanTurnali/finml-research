"""Integrity checks for the series registry and frequency alignment.

The registry is the dashboard's single source of truth; a duplicated ID or a
composite member filed under the wrong block silently corrupts every regime
reading downstream.
"""

import numpy as np
import pandas as pd

from macro import series as reg
from macro.fetch import to_monthly

ALLOWED_TRANSFORMS = {"level", "yoy", "ann3m", "diff12"}


def test_fred_ids_are_unique():
    ids = reg.ids()
    assert len(ids) == len(set(ids))


def test_transforms_are_known():
    unknown = {s.fred_id: s.transform for s in reg.ALL if s.transform not in ALLOWED_TRANSFORMS}
    assert not unknown


def test_composite_members_belong_to_their_block():
    assert all(s.block == "growth" for s in reg.GROWTH_COMPOSITE)
    assert all(s.block == "inflation" for s in reg.INFLATION_COMPOSITE)


def test_no_series_is_in_both_composites():
    assert not {s.fred_id for s in reg.GROWTH_COMPOSITE} & {
        s.fred_id for s in reg.INFLATION_COMPOSITE
    }


def test_to_monthly_averages_within_month_and_forward_fills_quarterly():
    daily = pd.Series(
        [1.0, 3.0], index=pd.to_datetime(["2024-01-05", "2024-01-25"]), name="D"
    )
    quarterly = pd.Series([10.0], index=pd.to_datetime(["2024-01-31"]), name="Q")
    monthly = to_monthly(pd.concat([daily, quarterly], axis=1))

    assert monthly.loc["2024-01-31", "D"] == 2.0  # mean, not last value

    # A lone observation is carried forward at most 3 months.
    extended = pd.concat(
        [quarterly, pd.Series([np.nan], index=pd.to_datetime(["2024-06-30"]), name="Q")]
    )
    filled = to_monthly(extended.to_frame())["Q"]
    assert filled.loc["2024-04-30"] == 10.0
    assert np.isnan(filled.loc["2024-05-31"])
