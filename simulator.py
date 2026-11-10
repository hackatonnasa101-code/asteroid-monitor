"""14 günlük real görünən asteroid (NEO) datası yaradan simulyator.

10-cu gün bilərəkdən bir "qırmızı" hadisə yerləşdirilir: NASA tərəfindən
təhlükəli sayılan, böyük (>= 140 m) və Yerə çox yaxın (< 7.48 mln km) keçən
asteroid. Qalan günlərdə qırmızı hadisə olmaması təmin edilir (logic.classify
ilə yoxlanılır).

Bu fayl yalnız data yaradır; bazaya yazma data_loader.py vasitəsilədir.

İstifadə:
  py simulator.py                      # data/simulated.csv yaradır
  py simulator.py --print              # hər asteroidin adını və statusunu çap edir
  py simulator.py --db                 # həm də asteroid.db-yə yazır
  py simulator.py --db --reset         # köhnə simulyasiyanı silir, sonra yazır
  py simulator.py --start 2026-11-01 --seed 7

Sütunlar db.py ilə eynidir: id, name, date, diameter_m, speed_kms,
distance_km, hazardous
"""

import argparse
import math
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from logic import (CLOSE_DISTANCE_KM, GREEN, LARGE_DIAMETER_M, LUNAR_DISTANCE_KM, RED,
                   YELLOW, classify)

DAYS = 14
RED_DAY = 10                     # 1-dən sayılır
OUT_PATH = Path(__file__).resolve().parent / "data" / "simulated.csv"
START_ID = 5001

# Provizor adlarda istifadə olunan hərflər ("I" yoxdur)
HALF_MONTH = "ABCDEFGHJKLMNOPQRSTUVWXY"   # 24 yarım ay
ORDER = "ABCDEFGHJKLMNOPQRSTUVWXYZ"       # 25 hərf


class Designations:
    """MPC üslubunda provizor adlar: (2026 VA1), (2026 VB1), ...

    Birinci hərf yarım ayı göstərir (Noyabr 1-15 = V, 16-30 = W),
    ikinci hərf və rəqəm həmin yarım ayda kəşf sırasıdır.
    """

    def __init__(self, rng):
        self.rng = rng
        self.counters = {}

    def next(self, d):
        half = HALF_MONTH[(d.month - 1) * 2 + (0 if d.day <= 15 else 1)]
        key = (d.year, half)
        # Real kataloqlarda bir neçə yüz obyektdən sonra gəlinir — təsadüfi başla
        n = self.counters.get(key, self.rng.randint(25, 400))
        self.counters[key] = n + self.rng.randint(1, 9)
        letter, cycle = ORDER[n % 25], n // 25
        return f"({d.year} {half}{letter}{cycle if cycle else ''})"


def _name_key(name):
    """'(2026 VJ26)' -> sıralama açarı (yarım ay, dövr, hərf)."""
    code = name.strip("()").split()[1]
    return code[0], int(code[2:] or 0), ORDER.index(code[1])


def _diameter(rng):
    """Log-normal: median ≈ 45 m, kiçiklər çox, 140 m+ olanlar ~13% (4–1200 m)."""
    return min(1200.0, max(4.0, rng.lognormvariate(math.log(45), 1.0)))


def _speed(rng):
    """Nisbi sürət, km/s: log-normal, median ≈ 12 km/s, 4–45 aralığında."""
    return min(45.0, max(4.0, rng.lognormvariate(math.log(12), 0.42)))


def _distance(rng):
    """Yaxınlaşma məsafəsi, km: ~2 LD – 0.5 AU, yaxın keçidlər daha nadir (~20%)."""
    lo, hi = 0.8e6, 74_800_000
    return lo + (hi - lo) * rng.random() ** 1.5


def _random_asteroid(rng, names, d):
    diameter = _diameter(rng)
    distance = _distance(rng)
    # NASA PHA: böyük obyektlərin bir hissəsi təhlükəli işarələnir
    hazardous = diameter >= LARGE_DIAMETER_M and rng.random() < 0.55

    # Təsadüfən qırmızı alınmasın: təhlükəli + böyük isə, yaxın olmasın
    if hazardous and distance < CLOSE_DISTANCE_KM:
        distance = rng.uniform(CLOSE_DISTANCE_KM * 1.15, 60_000_000)

    return {
        "name": names.next(d),
        "date": d.isoformat(),
        "diameter_m": round(diameter, 0 if diameter >= 20 else 1),
        "speed_kms": round(_speed(rng), 2),
        "distance_km": round(distance, -2),
        "hazardous": hazardous,
    }


def _red_event(rng, names, d):
    """10-cu günün planlı hadisəsi: böyük, təhlükəli və çox yaxın."""
    return {
        "name": names.next(d),
        "date": d.isoformat(),
        "diameter_m": float(rng.randint(310, 480)),
        "speed_kms": round(rng.uniform(19.5, 24.0), 2),
        "distance_km": round(rng.uniform(2.6, 3.4) * LUNAR_DISTANCE_KM, -2),
        "hazardous": True,
    }


def start_for_today(today=None):
    """Qırmızı hadisə (RED_DAY) 'today' gününə düşsün deyə 1-ci günün tarixi."""
    return (today or date.today()) - timedelta(days=RED_DAY - 1)


def simulate(start=None, seed=42):
    """14 günlük DataFrame qaytarır. start — 1-ci gün (default: 10-cu gün = bu gün)."""
    rng = random.Random(seed)
    names = Designations(rng)
    if start is None:
        start = start_for_today()

    rows = []
    for i in range(DAYS):
        d = start + timedelta(days=i)
        count = max(4, round(rng.gauss(11, 3)))          # gündə ~8–14 obyekt
        day_rows = [_random_asteroid(rng, names, d) for _ in range(count)]
        if i + 1 == RED_DAY:
            day_rows.insert(rng.randint(0, len(day_rows)), _red_event(rng, names, d))
            # adlar kəşf sırası ilə getsin (qırmızı araya düşəndə sıra pozulmasın)
            for row, name in zip(day_rows, sorted((r["name"] for r in day_rows), key=_name_key)):
                row["name"] = name
        rows.extend(day_rows)

    df = pd.DataFrame(rows)
    df.insert(0, "id", range(START_ID, START_ID + len(df)))

    # Yoxlama: qırmızı yalnız 10-cu gündə və tam bir dənə olmalıdır
    colors = df.apply(lambda r: classify(r)[0], axis=1)
    red_day = (start + timedelta(days=RED_DAY - 1)).isoformat()
    reds = df[colors == RED]
    assert len(reds) == 1 and reds["date"].iloc[0] == red_day, reds
    return df


def print_statuses(df, colors):
    """Hər asteroid üçün bir sətir: tarix, ad, status; sonda hər statusun sayı."""
    icons = {GREEN: "🟢", YELLOW: "🟡", RED: "🔴"}
    print()
    for row, color in zip(df.itertuples(), colors):
        print(f"{row.date}  {row.name:<14} {icons[color]} {color}")
    print()
    for color in (GREEN, YELLOW, RED):
        print(f"{icons[color]} {color:<8} {int((colors == color).sum())}")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--start", type=date.fromisoformat,
                   help="1-ci günün tarixi (YYYY-MM-DD). Default: 10-cu gün = bu gün")
    p.add_argument("--seed", type=int, default=42, help="təkrarlana bilən nəticə üçün")
    p.add_argument("--out", type=Path, default=OUT_PATH, help="CSV faylının yolu")
    p.add_argument("--print", action="store_true", dest="show",
                   help="hər asteroidin adını və statusunu terminalda çap et")
    p.add_argument("--db", action="store_true", help="asteroid.db-yə də yaz")
    p.add_argument("--reset", action="store_true",
                   help="--db ilə: yazmadan əvvəl köhnə simulyasiya sətirlərini sil (real data qalır)")
    args = p.parse_args()

    df = simulate(args.start, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"{len(df)} asteroid, {DAYS} gün -> {args.out}")

    colors = df.apply(lambda r: classify(r)[0], axis=1)
    if args.show:
        print_statuses(df, colors)

    red = df[colors == RED].iloc[0]
    print(f"🔴 10-cu gün ({red['date']}): {red['name']}, {red['diameter_m']:.0f} m, "
          f"{red['distance_km']:,.0f} km ({red['distance_km'] / LUNAR_DISTANCE_KM:.1f} LD), "
          f"{red['speed_kms']} km/s")

    if args.db:
        # Bazaya yazmaq data_loader-in işidir (simulator yalnız data yaradır)
        import data_loader
        import db
        db.init_db()
        n = data_loader.import_simulation(df, reset=args.reset)   # real dataya toxunmur
        print(f"{n} sətir bazaya yazıldı -> {db.DB_PATH}")


if __name__ == "__main__":
    main()
