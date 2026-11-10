"""Asteroid məlumatları üçün təhlil məntiqi.

Bu fayl yalnız hesablamalar aparır: ekrana heç nə çıxarmır, Streamlit/GUI və ya
baza kodundan asılı deyil. Giriş: dict / pandas Series (bir asteroid) və ya
DataFrame (bir neçə asteroid). Sütunlar db.py-dakı ilə eynidir:
id, name, date, diameter_m, speed_kms, distance_km, hazardous
"""

import math

import pandas as pd

# --- Qayda hədləri (lazım olsa, yalnız buranı dəyişin) ---------------------
# NASA-nın "potensial təhlükəli asteroid" (PHA) meyarlarına əsaslanır:
# Yerə 0.05 AU-dan yaxın keçən və diametri ~140 m-dən böyük olan cisimlər.
CLOSE_DISTANCE_KM = 7_480_000   # 0.05 AU ≈ 7.48 milyon km
LARGE_DIAMETER_M = 140          # metr
FAST_FACTOR = 2                 # "sürətli" = ortadan neçə dəfə sürətli

GREEN, YELLOW, RED = "yaşıl", "sarı", "qırmızı"


def _num(value):
    """Rəqəmi float kimi qaytarır; boş/NaN/yanlış dəyər üçün None."""
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def _flag(value):
    """hazardous dəyərini (1/0, True/False, "true"/"false") bool-a çevirir."""
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes")
    num = _num(value)
    return bool(num) if num is not None else False


# Səbəb kodları — mətnə çevrilməsi i18n.py-da (explain_* / reason_* açarları)
HAZARDOUS, CLOSE, LARGE = "hazardous", "close", "large"


def classify(asteroid):
    """Bir asteroidi qiymətləndirir.

    Qaydalar:
      - qırmızı: NASA "təhlükəli" kimi işarələyib, VƏ həm yaxın
        (< 7.48 mln km), həm də böyükdür (>= 140 m);
      - sarı:    təhlükəli işarəsi var, və ya yaxındır, və ya böyükdür;
      - yaşıl:   bunların heç biri yoxdur.

    Qaytarır: (rəng, səbəblər), məs. ("sarı", ("close",)).
    Səbəblər HAZARDOUS / CLOSE / LARGE kodlarıdır; izah mətni app.py-da
    i18n.py-dakı şablonlarla seçilmiş dildə qurulur.
    """
    get = asteroid.get
    distance = _num(get("distance_km"))
    diameter = _num(get("diameter_m"))

    flags = {
        HAZARDOUS: _flag(get("hazardous")),
        CLOSE: distance is not None and distance < CLOSE_DISTANCE_KM,
        LARGE: diameter is not None and diameter >= LARGE_DIAMETER_M,
    }
    reasons = tuple(code for code, on in flags.items() if on)

    if len(reasons) == len(flags):
        return RED, reasons
    if reasons:
        return YELLOW, reasons
    return GREEN, reasons


STATUS_RANK = {RED: 0, YELLOW: 1, GREEN: 2}   # kiçik = daha təhlükəli


def classify_df(df):
    """DataFrame-ə 'status' və 'reasons' sütunlarını əlavə edir (classify ilə).

    Nəticə əvvəlcə ən təhlükəlilər, sonra ən yaxınlar olmaqla sıralanır.
    """
    if df is None or df.empty:
        out = (df if df is not None else pd.DataFrame()).copy()
        return out.assign(status=pd.Series(dtype=object), reasons=pd.Series(dtype=object))

    results = [classify(row) for row in df.to_dict("records")]
    out = df.assign(
        status=[r[0] for r in results],
        reasons=[r[1] for r in results],
        distance_km=pd.to_numeric(df["distance_km"], errors="coerce"),
    )
    return (
        out.assign(_rank=out["status"].map(STATUS_RANK))
        .sort_values(["_rank", "distance_km"], na_position="last")
        .drop(columns="_rank")
        .reset_index(drop=True)
    )


def most_dangerous(df, day):
    """Verilən gündə ('YYYY-MM-DD' və ya date) ən təhlükəli asteroid.

    Əvvəl statusa (qırmızı > sarı > yaşıl), sonra Yerə məsafəyə görə seçilir.
    Qaytarır: 'status' və 'reasons' daxil olan dict, və ya o gün məlumat yoxdursa None.
    """
    if df is None or df.empty:
        return None
    today = df[df["date"].astype(str) == str(day)]
    if today.empty:
        return None
    return classify_df(today).iloc[0].to_dict()


def history_window(day, days=14):
    """'day' daxil olmaqla son 'days' günün (başlanğıc, son) tarixləri."""
    end = pd.Timestamp(day).date()
    return end - pd.Timedelta(days=days - 1), end


def distance_history(df):
    """Tarixçə qrafiki üçün məlumat.

    Qaytarır (dict):
      daily – hər gün üçün Yerə ən yaxın asteroid (date, name, distance_km, status)
      red   – bütün qırmızı statuslu asteroidlər (+ diameter_m, hazardous, reasons)
    """
    classified = classify_df(df)
    cols = ["date", "name", "distance_km", "diameter_m", "hazardous", "status", "reasons"]
    if classified.empty:
        empty = pd.DataFrame(columns=cols)
        return {"daily": empty, "red": empty}

    known = classified.dropna(subset=["distance_km"])
    daily = (
        known.loc[known.groupby("date")["distance_km"].idxmin(), cols]
        .sort_values("date")
        .reset_index(drop=True)
    )
    red = known.loc[known["status"] == RED, cols].sort_values("date").reset_index(drop=True)
    return {"daily": daily, "red": red}


def filter_asteroids(df, statuses=None, name_query="", hazardous_only=False,
                     max_distance_km=None):
    """classify_df nəticəsini filtrləyir.

    statuses        – saxlanacaq statusların siyahısı (None = hamısı)
    name_query      – adda axtarılan mətn (böyük/kiçik hərfə həssas deyil)
    hazardous_only  – yalnız NASA-nın təhlükəli işarələdikləri
    max_distance_km – bu məsafədən uzaq olanları çıxar (None = limitsiz)
    """
    out = classify_df(df)
    if out.empty:
        return out
    if statuses is not None:
        out = out[out["status"].isin(statuses)]
    if name_query and name_query.strip():
        out = out[out["name"].str.contains(name_query.strip(), case=False, regex=False)]
    if hazardous_only:
        out = out[out["hazardous"].map(_flag)]
    if max_distance_km is not None:
        out = out[out["distance_km"] <= max_distance_km]
    return out.reset_index(drop=True)


def day_asteroids(df, day):
    """All asteroids of the given day, classified and sorted (most dangerous first)."""
    if df is None or df.empty:
        return classify_df(df)
    return classify_df(df[df["date"].astype(str) == str(day)])


def day_overview(df, day):
    """Counts for one day: {'total': n, 'yaşıl': n, 'sarı': n, 'qırmızı': n}."""
    today = day_asteroids(df, day)
    counts = today["status"].value_counts() if not today.empty else {}
    return {"total": len(today), **{s: int(counts.get(s, 0)) for s in (GREEN, YELLOW, RED)}}


# --- Everyday comparisons (for "Putting it in perspective") -----------------
LUNAR_DISTANCE_KM = 384_400      # average Earth–Moon distance
SIZE_REFERENCES = [              # (metres, label), small -> large
    (10, "a school bus"),
    (30, "a blue whale"),
    (100, "a football pitch"),
    (330, "the Eiffel Tower"),
    (830, "the Burj Khalifa"),
]
RIFLE_BULLET_KMS = 1.0           # ~1 km/s


def perspective(asteroid):
    """Plain-language comparisons for one asteroid.

    Returns dict (values may be None when data is missing):
      lunar_distances – distance in Earth–Moon distances
      size_ref        – (label, ratio) of the closest everyday object by size
      bullet_ratio    – speed relative to a rifle bullet
      seconds_to_cross_earth – time to travel Earth's diameter (12,742 km)
    """
    get = asteroid.get
    distance, diameter, speed = (_num(get(k)) for k in ("distance_km", "diameter_m", "speed_kms"))

    size_ref = None
    if diameter:
        label_m, label = min(SIZE_REFERENCES, key=lambda r: abs(math.log(diameter / r[0])))
        size_ref = (label, diameter / label_m)

    return {
        "lunar_distances": distance / LUNAR_DISTANCE_KM if distance is not None else None,
        "size_ref": size_ref,
        "bullet_ratio": speed / RIFLE_BULLET_KMS if speed else None,
        "seconds_to_cross_earth": 12_742 / speed if speed else None,
    }


def weekly_summary(df):
    """Həftəlik xülasə.

    Qaytarır (dict):
      count          – asteroid sayı
      avg_speed_kms  – orta sürət (km/s) və ya None
      closest        – ən yaxın asteroidin sətri (dict) və ya None
      fast           – ortadan FAST_FACTOR dəfə sürətli olanlar (DataFrame)
    """
    empty = df.iloc[0:0] if df is not None else pd.DataFrame()
    if df is None or df.empty:
        return {"count": 0, "avg_speed_kms": None, "closest": None, "fast": empty}

    speed = pd.to_numeric(df["speed_kms"], errors="coerce")
    distance = pd.to_numeric(df["distance_km"], errors="coerce")

    avg = speed.mean()
    avg_speed = None if pd.isna(avg) else float(avg)

    closest = None
    if distance.notna().any():
        closest = df.loc[distance.idxmin()].to_dict()

    if avg_speed is None:
        fast = empty
    else:
        mask = speed >= FAST_FACTOR * avg_speed
        fast = df[mask].assign(speed_kms=speed[mask]).sort_values(
            "speed_kms", ascending=False
        )

    return {
        "count": len(df),
        "avg_speed_kms": avg_speed,
        "closest": closest,
        "fast": fast,
    }
