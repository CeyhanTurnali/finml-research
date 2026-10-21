"""
Veri çekme katmanı.
 
Tasarım kararı: HER ÇALIŞTIRMADA HER ŞEYİ ÇEKME.
Yerel parquet cache tutulur; sadece eksik kuyruk indirilir.
Böylece haftalık ritüel 5 saniye sürer, 5 dakika değil.
 
Kurulum:
    pip install fredapi pandas pyarrow matplotlib python-dotenv
    FRED API key: https://fredaccount.stlouisfed.org/apikeys (ücretsiz)
    .env dosyasına: FRED_API_KEY=xxxxx
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from . import series as reg

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE = DATA_DIR / "fred_cache.parquet"
META = DATA_DIR / "fred_meta.parquet"

START = "1990-01-01"
STALE_HOURS = 120


def _client():
    from fredapi import Fred
 
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise RuntimeError(
            "FRED_API_KEY tanımlı değil. .env dosyasına ekle veya "
            "os.environ['FRED_API_KEY'] ile set et."
        )
    return Fred(api_key=key)

 
def _load_cache() -> pd.DataFrame:
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    return pd.DataFrame()
 
 
def _is_stale() -> bool:
    if not CACHE.exists():
        return True
        age = datetime.now(UTC) - datetime.fromtimestamp(CACHE.stat().st_mtime, tz=UTC)
    return age > timedelta(hours=STALE_HOURS)

def fetch_raw(force: bool = False, ids: list[str] | None = None) -> pd.DataFrame:
    """
    Ham seri matrisi döndürür (index=tarih, sütun=fred_id).
    Cache taze ise ağa hiç çıkmaz.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ids = ids or reg.ids()
    cached = _load_cache()
 
    if not force and not _is_stale() and not set(ids) - set(cached.columns):
        return cached[ids]

    fred = _client()
    frames, failed = {}, []
    for sid in ids:
        try:
            s = fred.get_series(sid, observation_start=START)
            frames[sid] = s.rename(sid)
        except Exception as exc:  # noqa: BLE001 — seri kaldırılmış / erişilemiyor olabilir
            failed.append((sid, str(exc)[:80]))
 
    if failed:
        print("UYARI - çekilemeyen seriler:")
        for sid, msg in failed:
            print(f"  {sid}: {msg}")
 
    df = pd.concat(frames.values(), axis=1).sort_index()
    df.to_parquet(CACHE)
 
    pd.DataFrame(
                {"fetched_at": [datetime.now(UTC)], "n_series": [df.shape[1]]}
    ).to_parquet(META)
 
    return df
def to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Karışık frekansları (günlük/haftalık/aylık/çeyreklik) aylığa hizala.
 
    Kural: ay içi ORTALAMA al (son değer değil) -> gürültü azalır.
    Çeyreklik seriler ileri doldurulur (forward fill), çünkü açıklanana
    kadar en son bilinen değer geçerlidir.
    """
    m = df.resample("ME").mean()
    return m.ffill(limit=3)