"""logic.classify üçün testlər.

İşə salmaq:  py -m pytest test_logic.py   və ya   py -m unittest test_logic
"""

import unittest

from logic import (CLOSE, GREEN, HAZARDOUS, LARGE, RED, YELLOW, classify, day_overview,
                   perspective)


class ClassifyTest(unittest.TestCase):
    def test_green(self):
        # kiçik, uzaq, təhlükəli işarəsi yoxdur
        color, reasons = classify({"name": "A", "diameter_m": 30,
                                   "distance_km": 40_000_000, "hazardous": False})
        self.assertEqual((color, reasons), (GREEN, ()))

    def test_yellow(self):
        # yalnız yaxındır (< 7.48 mln km), amma kiçikdir və təhlükəli deyil
        color, reasons = classify({"name": "B", "diameter_m": 20,
                                   "distance_km": 2_000_000, "hazardous": False})
        self.assertEqual((color, reasons), (YELLOW, (CLOSE,)))

    def test_red(self):
        # təhlükəli + böyük (>= 140 m) + yaxın — hamısı birlikdə
        color, reasons = classify({"name": "C", "diameter_m": 353,
                                   "distance_km": 1_186_900, "hazardous": True})
        self.assertEqual((color, reasons), (RED, (HAZARDOUS, CLOSE, LARGE)))


class HelpersTest(unittest.TestCase):
    def setUp(self):
        import pandas as pd
        self.df = pd.DataFrame([
            {"name": "A", "date": "2026-11-01", "diameter_m": 30,
             "speed_kms": 10, "distance_km": 40_000_000, "hazardous": 0},
            {"name": "C", "date": "2026-11-01", "diameter_m": 353,
             "speed_kms": 20, "distance_km": 1_186_900, "hazardous": 1},
            {"name": "B", "date": "2026-11-02", "diameter_m": 20,
             "speed_kms": 5, "distance_km": 2_000_000, "hazardous": 0},
        ])

    def test_day_overview(self):
        o = day_overview(self.df, "2026-11-01")
        self.assertEqual((o["total"], o[GREEN], o[YELLOW], o[RED]), (2, 1, 0, 1))
        self.assertEqual(day_overview(self.df, "2026-12-01")["total"], 0)

    def test_perspective(self):
        p = perspective({"distance_km": 384_400 * 3, "diameter_m": 320, "speed_kms": 20})
        self.assertAlmostEqual(p["lunar_distances"], 3)
        self.assertEqual(p["size_ref"][0], "the Eiffel Tower")
        self.assertAlmostEqual(p["bullet_ratio"], 20)
        self.assertIsNone(perspective({})["lunar_distances"])


if __name__ == "__main__":
    unittest.main()
