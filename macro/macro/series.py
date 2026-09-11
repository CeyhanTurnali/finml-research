"""
Seri kayıt defteri (series registry).
 
Dashboard'un "tek doğruluk kaynağı". Yeni bir gösterge eklemek =
buraya bir satır eklemek. Kod hiçbir yerde seri ID'si hardcode etmez.
 
transform seçenekleri:
    "level"   -> ham seviye (zaten endeks/oran olanlar: CFNAI, spreadler, VIX)
    "yoy"     -> yıllık % değişim
    "ann3m"   -> son 3 ayın yıllıklandırılmış oranı (momentum ölçütü)
    "diff12"  -> 12 aylık fark (oranlar için: işsizlik, faiz)
 
invert=True  -> seri yükselince ilgili blok ZAYIFLIYOR demektir.
                (işsizlik başvurusu ↑ = büyüme ↓)
in_growth / in_inflation -> kompozit endekse dahil mi?
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Series:
    fred_id: str
    label: str
    block: str            # growth | inflation | policy | market | credit
    role: str             # leading | coincident | lagging | market
    transform: str
    invert: bool = False
    in_growth: bool = False
    in_inflation: bool = False
    note: str = ""

# --------------------------------------------------------------------------
# BÜYÜME BLOĞU
# --------------------------------------------------------------------------

GROWTH = [
    Series("ICSA", "Initial Jobless Claims", "growth", "leading", "yoy",
           invert=True, in_growth=True,
           note="Haftalık. En hızlı öncü. Yükseliş = kötü."),
    Series("PERMIT", "Building Permits", "growth", "leading", "yoy",
           in_growth=True, note="Faize en duyarlı sektör; klasik öncü."),
    Series("USSLIND", "Leading Index for the US", "growth", "leading", "level",
           in_growth=True, note="Philly Fed eyalet-bazlı öncü endeks."),
    Series("UMCSENT", "U. Michigan Consumer Sentiment", "growth", "leading", "yoy",
           in_growth=True),
    Series("CFNAI", "Chicago Fed National Activity Index", "growth", "coincident", "level",
           in_growth=True,
           note="85 seri kompoziti. 0 = trend büyüme. ISM'in en iyi ücretsiz ikamesi."),
    Series("INDPRO", "Industrial Production", "growth", "coincident", "yoy",
           in_growth=True),
    Series("RRSFS", "Real Retail Sales", "growth", "coincident", "yoy",
           in_growth=True, note="REEL perakende — nominal RSAFS değil."),
    Series("PAYEMS", "Nonfarm Payrolls", "growth", "coincident", "yoy",
           in_growth=True),
    # İzlenir ama kompozite girmez (gecikmeli):
    Series("GDPC1", "Real GDP", "growth", "lagging", "yoy"),
    Series("UNRATE", "Unemployment Rate", "growth", "lagging", "diff12", invert=True),
]

# --------------------------------------------------------------------------
# ENFLASYON BLOĞU
# --------------------------------------------------------------------------

INFLATION = [
    Series("CPILFESL", "Core CPI (3m ann.)", "inflation", "coincident", "ann3m",
           in_inflation=True,
           note="Momentum ölçütü. YoY baz etkisiyle kirlenir, 3m ann. kirlenmez."),
    Series("PCEPILFE", "Core PCE", "inflation", "coincident", "ann3m",
           in_inflation=True, note="Fed'in TERCİH ETTİĞİ ölçüt."),
    Series("CPIAUCSL", "Headline CPI", "inflation", "coincident", "yoy",
           in_inflation=True),
    Series("PPIFIS", "PPI Final Demand", "inflation", "leading", "yoy",
           in_inflation=True, note="Üreticiden tüketiciye geçiş öncüsü."),
    Series("T5YIE", "5Y Breakeven Inflation", "inflation", "leading", "level",
           in_inflation=True, note="Piyasanın fiyatladığı beklenti. Market-based."),
    Series("MICH", "U.Mich 1Y Inflation Expectation", "inflation", "leading", "level",
           in_inflation=True),
    Series("DCOILWTICO", "WTI Crude Oil", "inflation", "leading", "yoy",
           in_inflation=True, note="Arz şoku kanalı."),
    Series("AHETPI", "Avg Hourly Earnings", "inflation", "coincident", "yoy",
           note="Ücret-fiyat sarmalı takibi. Kompozite girmez, ayrı okunur."),
]
 
# --------------------------------------------------------------------------
# POLİTİKA / FİNANSAL KOŞULLAR (kompozite girmez — bağlam katmanı)
# --------------------------------------------------------------------------
POLICY = [
    Series("FEDFUNDS", "Fed Funds Rate", "policy", "lagging", "level"),
    Series("DGS2", "2Y Treasury Yield", "policy", "leading", "level",
           note="Piyasanın faiz BEKLENTİSİ burada okunur."),
    Series("DGS10", "10Y Treasury Yield", "policy", "market", "level"),
    Series("T10Y2Y", "Yield Curve 10Y-2Y", "policy", "leading", "level",
           note="Ters dönme = resesyon öncüsü."),
    Series("T10Y3M", "Yield Curve 10Y-3M", "policy", "leading", "level",
           note="Fed araştırmasına göre 10Y-2Y'den daha güvenilir."),
    Series("DFII10", "10Y Real Yield (TIPS)", "policy", "market", "level",
           note="REEL faiz. Altın ve growth hisseler için ana sürücü."),
    Series("NFCI", "Chicago Fed Financial Conditions", "policy", "leading", "level",
           invert=True, note="Pozitif = sıkı koşullar."),
    Series("DRTSCILM", "Bank Lending Standards (C&I)", "credit", "leading", "level",
           invert=True, note="Kredi döngüsünün kalbi. Çeyreklik, çok güçlü öncü."),
    Series("WALCL", "Fed Balance Sheet", "policy", "market", "yoy"),
    Series("M2SL", "M2 Money Supply", "policy", "leading", "yoy"),
]

# --------------------------------------------------------------------------
# PİYASA / RİSK İŞTAHI
# --------------------------------------------------------------------------
MARKET = [
    Series("BAMLH0A0HYM2", "High Yield Credit Spread (OAS)", "credit", "leading", "level",
           invert=True, note="Risk iştahı termometresi. Genişleme = stres."),
    Series("BAMLC0A0CM", "Investment Grade Spread (OAS)", "credit", "leading", "level",
           invert=True),
    Series("VIXCLS", "VIX", "market", "market", "level", invert=True),
    Series("DTWEXBGS", "Broad Dollar Index", "market", "market", "yoy",
           note="DXY değil; Fed'in geniş ticaret-ağırlıklı endeksi. EM için kritik."),
    Series("DEXTRUS", "USD/TRY", "market", "market", "yoy",
           note="TR bloğu için köprü seri."),
] 

ALL = GROWTH + INFLATION + POLICY + MARKET
 
BY_ID = {s.fred_id: s for s in ALL}
GROWTH_COMPOSITE = [s for s in ALL if s.in_growth]
INFLATION_COMPOSITE = [s for s in ALL if s.in_inflation]

 
def ids() -> list[str]:
    return [s.fred_id for s in ALL]