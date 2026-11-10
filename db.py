"""Asteroid (NEO) məlumatları üçün SQLite bazası: asteroid.db

Bu fayl yalnız bazanı idarə edir (cədvəl, yazma, oxuma, silmə). CSV oxumaq və
datanı təmizləmək data_loader.py-dadır; qaydalar logic.py-dadır.
"""

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "asteroid.db"

COLUMNS = ["id", "name", "date", "diameter_m", "speed_kms", "distance_km", "hazardous"]

# Məlumat mənbəyi: real (NASA / yüklənmiş CSV) və ya simulyasiya (simulator.py)
REAL = "real"
SIM = "sim"
SOURCES = (REAL, SIM)

SCHEMA = """
CREATE TABLE IF NOT EXISTS asteroids (
    id           INTEGER PRIMARY KEY,
    name         TEXT    NOT NULL,
    date         TEXT    NOT NULL CHECK (date(date) IS NOT NULL),
    diameter_m   REAL    CHECK (diameter_m  IS NULL OR diameter_m  >= 0),
    speed_kms    REAL    CHECK (speed_kms   IS NULL OR speed_kms   >= 0),
    distance_km  REAL    CHECK (distance_km IS NULL OR distance_km >= 0),
    hazardous    INTEGER NOT NULL DEFAULT 0 CHECK (hazardous IN (0, 1)),
    source       TEXT    NOT NULL DEFAULT 'real' CHECK (source IN ('real', 'sim'))
);
CREATE INDEX IF NOT EXISTS idx_asteroids_date      ON asteroids(date);
CREATE INDEX IF NOT EXISTS idx_asteroids_hazardous ON asteroids(hazardous);
"""


def _connect():
    return sqlite3.connect(DB_PATH)


def _check_source(source):
    if source not in SOURCES:
        raise ValueError(f"Naməlum mənbə: {source!r}. Mümkün olanlar: {SOURCES}")


def init_db():
    """Bazanı və 'asteroids' cədvəlini yaradır (artıq varsa, heç nəyə toxunmur).

    Köhnə bazada 'source' sütunu yoxdursa, onu əlavə edir (köhnə sətirlər = 'real').
    """
    with _connect() as conn:
        conn.executescript(SCHEMA)
        cols = [row[1] for row in conn.execute("PRAGMA table_info(asteroids)")]
        if "source" not in cols:
            conn.execute(
                "ALTER TABLE asteroids ADD COLUMN source TEXT NOT NULL DEFAULT 'real' "
                "CHECK (source IN ('real', 'sim'))"
            )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_asteroids_source_date ON asteroids(source, date)"
        )


def clear_source(source):
    """Verilən mənbənin bütün sətirlərini silir. Silinən sətir sayını qaytarır."""
    _check_source(source)
    with _connect() as conn:
        return conn.execute("DELETE FROM asteroids WHERE source = ?", (source,)).rowcount


def save_asteroids(df, source=REAL):
    """Təmizlənmiş DataFrame-i (data_loader.normalize) 'source' mənbəyi ilə yazır.

    Eyni id varsa, köhnə sətri yeniləyir. Yazılan sətir sayını qaytarır.
    """
    _check_source(source)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Bu sütunlar çatışmır: {missing}")

    # NaN -> None (bazada NULL olsun)
    out = df[COLUMNS].astype(object)
    out = out.where(pd.notna(out), None).assign(source=source)

    cols = COLUMNS + ["source"]
    rows = out[cols].itertuples(index=False, name=None)
    with _connect() as conn:
        conn.executemany(
            f"INSERT OR REPLACE INTO asteroids ({', '.join(cols)}) "
            f"VALUES ({', '.join('?' * len(cols))})",
            rows,
        )
    return len(out)


def _source_filter(source):
    """(SQL parçası, parametrlər): source=None olduqda bütün mənbələr."""
    if source is None:
        return "", ()
    _check_source(source)
    return " AND source = ?", (source,)


def get_asteroids(days=7, source=None):
    """Son 'days' gündən bu günə (və sonrasına) qədər olan asteroidləri DataFrame kimi qaytarır."""
    where, extra = _source_filter(source)
    with _connect() as conn:
        return pd.read_sql_query(
            f"SELECT * FROM asteroids WHERE date >= date('now', ?){where} ORDER BY date",
            conn,
            params=(f"-{int(days)} days", *extra),
        )


def get_asteroids_between(start, end, source=None):
    """[start, end] tarix aralığındakı (hər ikisi daxil) asteroidləri qaytarır.

    start / end: datetime.date və ya 'YYYY-MM-DD' sətri.
    source: 'real', 'sim' və ya None (hamısı).
    """
    where, extra = _source_filter(source)
    with _connect() as conn:
        return pd.read_sql_query(
            f"SELECT * FROM asteroids WHERE date BETWEEN ? AND ?{where} ORDER BY date",
            conn,
            params=(str(start), str(end), *extra),
        )


if __name__ == "__main__":
    init_db()
    print(f"Baza hazırdır -> {DB_PATH}  (CSV yükləmək üçün: py data_loader.py)")
