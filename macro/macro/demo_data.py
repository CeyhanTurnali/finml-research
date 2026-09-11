"""
DEMO veri üreteci — FRED erişimi olmadan dashboard çıktısını göstermek için.
Gerçekçi bir makro yörünge kurgular: 2019 normal -> 2020 COVID çöküşü ->
2021 reflasyon -> 2022 stagflasyon -> 2023-25 dezenflasyon/toparlanma.
"""
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from macro import series as reg

rng = np.random.default_rng(42)
idx = pd.date_range("2004-01-31", "2025-08-31", freq="ME")
n = len(idx)
t = np.arange(n)


def bump(center_ym, width, height):
    c = (pd.Period(center_ym, "M") - pd.Period("2004-01", "M")).n
    return height * np.exp(-0.5 * ((t - c) / width) ** 2)


# --- Latent faktörler: G (büyüme), I (enflasyon) ---
G = np.zeros(n)
G += -1.0 * bump("2008-11", 8, 1.0) * 3.0          # GFC
G += -1.0 * bump("2020-04", 2.2, 1.0) * 4.5        # COVID çöküşü
G += bump("2021-05", 6, 1.0) * 3.0                 # yeniden açılma
G += -1.0 * bump("2022-10", 7, 1.0) * 1.5          # sıkılaşma yavaşlaması
G += bump("2024-08", 9, 1.0) * 1.1                 # ılımlı toparlanma
G += -1.0 * bump("2025-06", 5, 1.0) * 1.3          # son dönem yavaşlama
G += 0.35 * np.sin(t / 21) + rng.normal(0, 0.22, n)

I = np.zeros(n)
I += -1.0 * bump("2009-06", 7, 1.0) * 2.2          # deflasyon korkusu
I += -1.0 * bump("2020-05", 3, 1.0) * 1.8
I += bump("2022-06", 8, 1.0) * 4.2                 # enflasyon şoku
I += -1.0 * bump("2024-06", 10, 1.0) * 1.0         # dezenflasyon
I += 0.25 * np.sin(t / 26 + 1.0) + rng.normal(0, 0.2, n)

G = pd.Series(G, index=idx).rolling(3, min_periods=1).mean().values
I = pd.Series(I, index=idx).rolling(3, min_periods=1).mean().values

data = {}


def level_from_growth(base_pct, sens, factor, start=100.0, noise=0.15):
    """Aylık büyüme oranı faktöre bağlı -> yoy dönüşümü faktörü izler."""
    mg = (base_pct + sens * factor) / 12 + rng.normal(0, noise / 12, n)
    return pd.Series(start * np.exp(np.cumsum(mg / 100)), index=idx)


# --- BÜYÜME bloğu ---
data["ICSA"] = level_from_growth(-1.0, -9.0, G, start=320_000, noise=3.0)   # invert=True
data["PERMIT"] = level_from_growth(1.0, 7.0, G, start=1300, noise=2.5)
data["UMCSENT"] = level_from_growth(0.2, 6.0, G, start=90, noise=2.0)
data["INDPRO"] = level_from_growth(1.2, 3.2, G, start=100, noise=0.9)
data["RRSFS"] = level_from_growth(2.0, 3.6, G, start=180, noise=1.0)
data["PAYEMS"] = level_from_growth(1.3, 2.4, G, start=131_000, noise=0.4)
data["GDPC1"] = level_from_growth(2.0, 2.6, G, start=15_000, noise=0.5)
data["CFNAI"] = pd.Series(0.55 * G + rng.normal(0, 0.18, n), index=idx)      # level
data["USSLIND"] = pd.Series(1.4 + 0.9 * G + rng.normal(0, 0.2, n), index=idx)
data["UNRATE"] = pd.Series(
    np.clip(5.4 - 1.05 * pd.Series(G, index=idx).rolling(6, min_periods=1).mean().values
            + rng.normal(0, 0.15, n), 3.2, 15), index=idx)                    # invert=True

# --- ENFLASYON bloğu ---
data["CPIAUCSL"] = level_from_growth(2.3, 1.35, I, start=185, noise=0.35)
data["CPILFESL"] = level_from_growth(2.1, 1.05, I, start=195, noise=0.28)
data["PCEPILFE"] = level_from_growth(1.9, 0.95, I, start=100, noise=0.25)
data["PPIFIS"] = level_from_growth(2.0, 2.6, I, start=170, noise=0.9)
data["DCOILWTICO"] = level_from_growth(1.0, 16.0, I, start=45, noise=8.0)
data["AHETPI"] = level_from_growth(2.8, 0.8, 0.6 * I + 0.4 * G, start=18, noise=0.3)
data["T5YIE"] = pd.Series(np.clip(2.15 + 0.42 * I + rng.normal(0, 0.09, n), 0.2, 4), index=idx)
data["MICH"] = pd.Series(np.clip(2.9 + 0.60 * I + rng.normal(0, 0.13, n), 0.5, 6), index=idx)

# --- POLİTİKA / PİYASA (Taylor benzeri tepki, gecikmeli) ---
pol = pd.Series(np.clip(1.2 + 0.95 * I + 0.55 * G, 0.05, 8), index=idx)
pol = pol.rolling(7, min_periods=1).mean()
data["FEDFUNDS"] = pol
data["DGS2"] = pol.shift(-3).ffill() + rng.normal(0, 0.12, n)
data["DGS10"] = pd.Series(2.3 + 0.42 * I + 0.30 * G, index=idx).rolling(4, min_periods=1).mean() \
                + rng.normal(0, 0.12, n)
data["T10Y2Y"] = data["DGS10"] - data["DGS2"]
data["T10Y3M"] = data["DGS10"] - (pol + 0.15)
data["DFII10"] = data["DGS10"] - data["T5YIE"]
data["NFCI"] = pd.Series(-0.35 - 0.30 * G + 0.16 * I + rng.normal(0, 0.1, n), index=idx)
data["DRTSCILM"] = pd.Series(np.clip(6 - 15 * G + rng.normal(0, 4, n), -25, 80), index=idx)
data["WALCL"] = level_from_growth(6.0, -3.0, G, start=800_000, noise=1.5)
data["M2SL"] = level_from_growth(5.5, 1.2, 0.5 * I - 0.3 * G, start=6_000, noise=0.8)
data["BAMLH0A0HYM2"] = pd.Series(np.clip(4.4 - 1.35 * G + rng.normal(0, 0.28, n), 2.4, 20), index=idx)
data["BAMLC0A0CM"] = pd.Series(np.clip(1.4 - 0.42 * G + rng.normal(0, 0.1, n), 0.7, 7), index=idx)
data["VIXCLS"] = pd.Series(np.clip(18 - 4.6 * G + rng.normal(0, 1.9, n), 10, 65), index=idx)
data["DTWEXBGS"] = level_from_growth(0.8, -1.6, G, start=100, noise=1.2)
data["DEXTRUS"] = level_from_growth(11.0, -2.0, G, start=1.4, noise=2.5)

monthly = pd.DataFrame(data)[[s.fred_id for s in reg.ALL]]
monthly.to_parquet("data/demo_monthly.parquet")
print(f"Demo veri: {monthly.shape[0]} ay x {monthly.shape[1]} seri "
      f"({monthly.index[0].date()} → {monthly.index[-1].date()})")
