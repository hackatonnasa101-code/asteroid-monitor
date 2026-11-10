"""Asteroid datasını oxuyur, yoxlayır, təmizləyir və bazaya ötürür.

Bu fayl yalnız data ilə işləyir: ekrana heç nə çıxarmır (Streamlit yoxdur),
qayda hesablamır (logic.py), SQL yazmır (db.py). Mənbələr:
  - CSV faylı (yol və ya yüklənmiş fayl obyekti)  -> source = 'real'
  - simulator.simulate() nəticəsi                -> source = 'sim'

İstifadə:
  py data_loader.py                 # data/asteroids.csv -> asteroid.db
  py data_loader.py yol/fayl.csv    # başqa CSV
"""

import sys
from pathlib import Path

import pandas as pd

import db

CSV_PATH = Path(__file__).resolve().parent / "data" / "asteroids.csv"
NUMERIC_COLUMNS = ["diameter_m", "speed_kms", "distance_km"]


def normalize(df):
    """Xam DataFrame-i bazaya uyğun formata salır (yeni DataFrame qaytarır).

    - lazımi sütunları yoxlayır ('id' yoxdursa, boş qoyulur — SQLite nömrə verir);
    - tarixi 'YYYY-MM-DD' formatına salır;
    - rəqəm sütunlarını float-a çevirir (yanlış dəyər -> ValueError);
    - hazardous: True/False, "true"/"false", "yes", 1/0 -> 1/0.
    """
    df = df.copy()
    if "id" not in df.columns:
        df["id"] = None

    missing = [c for c in db.COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV-də bu sütunlar çatışmır: {missing}")

    df = df[db.COLUMNS]
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col])
    df["hazardous"] = (
        df["hazardous"].astype(str).str.strip().str.lower()
        .isin(["1", "1.0", "true", "yes"]).astype(int)
    )
    return df


def read_csv(file):
    """CSV-ni (yol və ya fayl obyekti) oxuyub təmizlənmiş DataFrame qaytarır."""
    return normalize(pd.read_csv(file))


def import_csv(file):
    """CSV-ni oxuyur və 'real' mənbəsi ilə bazaya yazır. Yazılan sətir sayı."""
    return db.save_asteroids(read_csv(file), source=db.REAL)


def import_simulation(df, reset=True):
    """Simulyasiya DataFrame-ini 'sim' mənbəsi ilə bazaya yazır.

    reset=True: əvvəlcə köhnə simulyasiya sətirləri silinir (real data qalır).
    """
    if reset:
        db.clear_source(db.SIM)
    return db.save_asteroids(normalize(df), source=db.SIM)


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_PATH
    db.init_db()
    if not path.exists():
        print(f"CSV tapılmadı: {path}")
    else:
        n = import_csv(path)
        print(f"{n} asteroid bazaya yazıldı -> {db.DB_PATH}")
        print(db.get_asteroids(7))
