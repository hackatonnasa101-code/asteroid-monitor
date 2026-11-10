"""User-visible text for app.py in English and Azerbaijani.

Only text lives here — no calculations. Placeholders like {n} are filled in by
app.py with values that come from logic.py / db.py.
"""

EN, AZ = "en", "az"
LANGUAGES = {EN: "🇬🇧 English", AZ: "🇦🇿 Azərbaycan"}

TEXT = {
    EN: {
        # Page / header
        "title": "☄️ Asteroid Monitor",
        "subtitle": "Near-Earth objects · daily threat assessment",
        "period_chip": "Period: {start} – {end}",
        "tab_now": "🎯 Now",
        "tab_history": "📈 History",
        "tab_table": "📋 Table",

        # Statuses
        "status_green": "Green",
        "status_yellow": "Yellow",
        "status_red": "Red",
        "title_green": "No threat",
        "title_yellow": "Needs attention",
        "title_red": "High risk",

        # Explanations (filled in by app.py from logic.classify reasons)
        "explain_red": "{name} is flagged as hazardous by NASA, is {diameter} m across "
                       "and passes within {distance} km of Earth.",
        "explain_yellow": "{name} needs attention: {reasons}.",
        "explain_green": "{name} is not considered hazardous: it is neither very close "
                         "nor large.",
        "reason_hazardous": "flagged as hazardous by NASA",
        "reason_close": "close approach to Earth ({distance} km)",
        "reason_large": "large size ({diameter} m)",

        # Sidebar
        "language": "🌐 Language",
        "control_panel": "### ☄️ Control panel",
        "data_source": "Data source",
        "source_real": "🛰️ Real data",
        "source_sim": "🧪 Simulation",
        "today": "Today",
        "upload_heading": "**Upload real data**",
        "csv_file": "CSV file",
        "save_button": "Save to database",
        "saved": "{n} asteroids saved to the database.",
        "upload_failed": "Upload failed: {error}",
        "required_columns": "Required columns: name, date, diameter_m, speed_kms, "
                            "distance_km, hazardous (id is optional).",
        "sim_heading": "**Simulation**",
        "sim_caption": "{days} days of synthetic data. Day {red_day} contains one red event.",
        "seed": "Seed",
        "sim_button": "Generate new simulation",
        "sim_saved": "{n} simulated asteroids saved to the database.",

        # Empty state
        "no_data_for": "No data for {day}",
        "nothing_yet": "🔭 Nothing to show yet",
        "steps_real": "<li>Prepare a CSV with the columns <code>name, date, diameter_m, "
                      "speed_kms, distance_km, hazardous</code>.</li>"
                      "<li>Upload it in the sidebar and click <b>Save to database</b>.</li>"
                      "<li>Make sure your file has rows for the selected <b>Today</b> date.</li>",
        "steps_sim": "<li>Pick any <b>Seed</b> in the sidebar.</li>"
                     "<li>Click <b>Generate new simulation</b> — 14 days of data ending "
                     "on the selected <b>Today</b> will be created.</li>",

        # Glossary
        "glossary_title": "📖 What do these terms mean?",
        "glossary": """
- **NEO (Near-Earth Object)** — an asteroid or comet whose orbit brings it close
  to Earth's orbit.
- **PHA (Potentially Hazardous Asteroid)** — NASA's label for objects larger than
  about 140 m that can pass within 0.05 AU of Earth's orbit. This is the
  "hazardous" flag in the data.
- **AU (Astronomical Unit)** — the average Earth–Sun distance, about 150 million km.
  0.05 AU ≈ {close_km} km.
- **LD (Lunar Distance)** — the average Earth–Moon distance, about {lunar_km} km.
- **Close approach** — the moment an asteroid passes nearest to Earth. "Distance"
  in this dashboard is that minimum distance.

*A red status means "watch closely", not "on a collision course". Close
approaches at millions of km are routine and safe.*
""",

        # Perspective
        "perspective": "Putting it in perspective",
        "moon": "{ld}× the distance to the Moon",
        "moon_note": "The Moon is {lunar_km} km away",
        "size_about": "About the size of {label}",
        "size_times": "{ratio}× the size of {label}",
        "size_note": "Compared by length / height",
        "bullet": "{ratio}× faster than a rifle bullet",
        "bullet_note": "Would cross Earth's diameter in {minutes} minutes",
        "no_comparisons": "Not enough data for comparisons.",
        "size_refs": {},   # logic.py labels are already English

        # Counts
        "at_a_glance": "Today at a glance · {day}",
        "total_today": "Total today",
        "asteroids": "asteroids",

        # Now tab
        "most_dangerous": "Most dangerous asteroid today · {day}",
        "explanation": "Explanation:",
        "distance_from_earth": "Distance from Earth",
        "close_limit": "Close-approach limit: {km} km",
        "diameter": "Diameter",
        "large_limit": "Large-object limit: {m} m",
        "speed": "Speed",
        "relative_to_earth": "Relative to Earth",
        "nasa_flag": "NASA flag",
        "hazardous_yes": "Hazardous",
        "hazardous_no": "No",
        "pha": "Potentially Hazardous Asteroid (PHA)",
        "rule": "<b>How status is decided:</b> 🔴 Red = NASA hazardous flag + closer than "
                "{km} km + diameter ≥ {m} m (all three). 🟡 Yellow = any one of these. "
                "🟢 Green = none.",

        # History tab
        "close_line": "Close-approach limit (0.05 AU)",
        "closest_of_day": "Closest asteroid of the day",
        "red_status": "Red status",
        "chart_title": "Distance from Earth — last {days} days",
        "axis_date": "Date",
        "axis_distance": "Distance (km)",
        "no_period_data": "No data for this period.",
        "tracked": "Asteroids tracked",
        "closest_approach": "Closest approach",
        "average_speed": "Average speed",
        "unusually_fast": "{n} unusually fast",
        "red_events": "Red events",
        "all_three": "All three risk factors",
        "chart_caption": "Blue line — the closest asteroid of each day. Red points — "
                         "red-status asteroids. Everything below the dotted line passes "
                         "closer than 0.05 AU.",
        "no_red": "No red-status asteroids in this period.",
        "red_events_heading": "#### 🔴 Red events",

        # Table tab
        "col_status": "Status",
        "col_name": "Name",
        "col_date": "Date",
        "col_diameter": "Diameter (m)",
        "col_speed": "Speed (km/s)",
        "col_distance": "Distance (km)",
        "col_hazardous": "Hazardous",
        "col_hazardous_help": "Flagged as hazardous by NASA",
        "col_explanation": "Explanation",
        "filter_status": "Status",
        "filter_name": "Search by name",
        "filter_name_ph": "e.g. VU25",
        "filter_hazardous": "NASA hazardous only",
        "filter_distance": "Maximum distance (million km)",
        "filter_distance_help": "Slide to the end for no limit.",
        "table_caption": "**{n}** asteroids · {start} – {end} · sorted by risk, then distance",
        "no_match": "No asteroids match these filters.",
    },

    AZ: {
        # Səhifə / başlıq
        "title": "☄️ Asteroid Monitoru",
        "subtitle": "Yerə yaxın obyektlər · gündəlik təhlükə qiymətləndirməsi",
        "period_chip": "Dövr: {start} – {end}",
        "tab_now": "🎯 İndi",
        "tab_history": "📈 Tarixçə",
        "tab_table": "📋 Cədvəl",

        # Statuslar
        "status_green": "Yaşıl",
        "status_yellow": "Sarı",
        "status_red": "Qırmızı",
        "title_green": "Təhlükə yoxdur",
        "title_yellow": "Diqqət tələb edir",
        "title_red": "Yüksək risk",

        # İzahlar (app.py logic.classify səbəblərindən doldurur)
        "explain_red": "{name} NASA tərəfindən təhlükəli kimi işarələnib, diametri "
                       "{diameter} m-dir və Yerə {distance} km-ə qədər yaxınlaşır.",
        "explain_yellow": "{name} diqqət tələb edir: {reasons}.",
        "explain_green": "{name} təhlükəli sayılmır: nə çox yaxındır, nə də böyükdür.",
        "reason_hazardous": "NASA təhlükəli kimi işarələyib",
        "reason_close": "Yerə yaxın keçid ({distance} km)",
        "reason_large": "böyük ölçü ({diameter} m)",

        # Yan panel
        "language": "🌐 Dil",
        "control_panel": "### ☄️ İdarə paneli",
        "data_source": "Məlumat mənbəyi",
        "source_real": "🛰️ Real məlumat",
        "source_sim": "🧪 Simulyasiya",
        "today": "Bu gün",
        "upload_heading": "**Real məlumat yüklə**",
        "csv_file": "CSV faylı",
        "save_button": "Bazaya yaz",
        "saved": "{n} asteroid bazaya yazıldı.",
        "upload_failed": "Yükləmə alınmadı: {error}",
        "required_columns": "Lazımi sütunlar: name, date, diameter_m, speed_kms, "
                            "distance_km, hazardous (id istəyə bağlıdır).",
        "sim_heading": "**Simulyasiya**",
        "sim_caption": "{days} günlük süni məlumat. {red_day}. gündə bir qırmızı hadisə olur.",
        "seed": "Seed",
        "sim_button": "Yeni simulyasiya yarat",
        "sim_saved": "{n} simulyasiya asteroidi bazaya yazıldı.",

        # Boş vəziyyət
        "no_data_for": "{day} üçün məlumat yoxdur",
        "nothing_yet": "🔭 Hələ göstəriləcək heç nə yoxdur",
        "steps_real": "<li>Sütunları <code>name, date, diameter_m, speed_kms, distance_km, "
                      "hazardous</code> olan CSV hazırlayın.</li>"
                      "<li>Yan paneldə yükləyin və <b>Bazaya yaz</b> düyməsini basın.</li>"
                      "<li>Seçilmiş <b>Bu gün</b> tarixi üçün faylda sətir olduğundan əmin olun.</li>",
        "steps_sim": "<li>Yan paneldə istənilən <b>Seed</b> seçin.</li>"
                     "<li><b>Yeni simulyasiya yarat</b> düyməsini basın — seçilmiş "
                     "<b>Bu gün</b> ilə bitən 14 günlük məlumat yaranacaq.</li>",

        # Lüğət
        "glossary_title": "📖 Bu terminlər nə deməkdir?",
        "glossary": """
- **NEO (Yerə yaxın obyekt)** — orbiti onu Yerin orbitinə yaxınlaşdıran asteroid
  və ya kometa.
- **PHA (Potensial təhlükəli asteroid)** — NASA-nın təxminən 140 m-dən böyük və Yerin
  orbitinə 0.05 AU-dan yaxın keçə bilən obyektlərə verdiyi ad. Məlumatdakı
  "təhlükəli" işarəsi budur.
- **AU (Astronomik vahid)** — Yerlə Günəş arasındakı orta məsafə, təxminən 150 milyon km.
  0.05 AU ≈ {close_km} km.
- **LD (Ay məsafəsi)** — Yerlə Ay arasındakı orta məsafə, təxminən {lunar_km} km.
- **Yaxınlaşma** — asteroidin Yerə ən yaxın keçdiyi an. Bu paneldəki "məsafə"
  həmin minimum məsafədir.

*Qırmızı status "diqqətlə izləyin" deməkdir, "toqquşma yolundadır" demək deyil.
Milyonlarla km məsafədən keçidlər adi və təhlükəsizdir.*
""",

        # Müqayisələr
        "perspective": "Müqayisə üçün",
        "moon": "Ay məsafəsinin {ld} misli",
        "moon_note": "Ay {lunar_km} km uzaqdadır",
        "size_about": "Təxminən {label} boydadır",
        "size_times": "{label} ölçüsünün {ratio} misli",
        "size_note": "Uzunluq / hündürlüyə görə müqayisə",
        "bullet": "Tüfəng gülləsindən {ratio} dəfə sürətli",
        "bullet_note": "Yerin diametrini {minutes} dəqiqəyə keçərdi",
        "no_comparisons": "Müqayisə üçün kifayət qədər məlumat yoxdur.",
        "size_refs": {     # logic.SIZE_REFERENCES adlarının tərcüməsi
            "a school bus": "məktəb avtobusu",
            "a blue whale": "göy balina",
            "a football pitch": "futbol meydançası",
            "the Eiffel Tower": "Eyfel qülləsi",
            "the Burj Khalifa": "Bürc Xəlifə",
        },

        # Saylar
        "at_a_glance": "Bu gün qısaca · {day}",
        "total_today": "Bu gün cəmi",
        "asteroids": "asteroid",

        # İndi tabı
        "most_dangerous": "Bu günün ən təhlükəli asteroidi · {day}",
        "explanation": "İzah:",
        "distance_from_earth": "Yerə məsafə",
        "close_limit": "Yaxınlıq həddi: {km} km",
        "diameter": "Diametr",
        "large_limit": "Böyüklük həddi: {m} m",
        "speed": "Sürət",
        "relative_to_earth": "Yerə nisbətən",
        "nasa_flag": "NASA işarəsi",
        "hazardous_yes": "Təhlükəli",
        "hazardous_no": "Yox",
        "pha": "Potensial təhlükəli asteroid (PHA)",
        "rule": "<b>Status necə təyin olunur:</b> 🔴 Qırmızı = NASA təhlükəli işarəsi + "
                "{km} km-dən yaxın + diametr ≥ {m} m (üçü birlikdə). 🟡 Sarı = bunlardan "
                "hər hansı biri. 🟢 Yaşıl = heç biri.",

        # Tarixçə tabı
        "close_line": "Yaxınlaşma həddi (0.05 AU)",
        "closest_of_day": "Günün ən yaxın asteroidi",
        "red_status": "Qırmızı status",
        "chart_title": "Yerə məsafə — son {days} gün",
        "axis_date": "Tarix",
        "axis_distance": "Məsafə (km)",
        "no_period_data": "Bu dövr üçün məlumat yoxdur.",
        "tracked": "İzlənən asteroidlər",
        "closest_approach": "Ən yaxın keçid",
        "average_speed": "Orta sürət",
        "unusually_fast": "{n} qeyri-adi sürətli",
        "red_events": "Qırmızı hadisələr",
        "all_three": "Üç risk amilinin hamısı",
        "chart_caption": "Mavi xətt — hər günün Yerə ən yaxın asteroidi. Qırmızı nöqtələr — "
                         "qırmızı statuslu asteroidlər. Nöqtəli xəttdən aşağıdakılar "
                         "0.05 AU-dan yaxın keçir.",
        "no_red": "Bu dövrdə qırmızı statuslu asteroid yoxdur.",
        "red_events_heading": "#### 🔴 Qırmızı hadisələr",

        # Cədvəl tabı
        "col_status": "Status",
        "col_name": "Ad",
        "col_date": "Tarix",
        "col_diameter": "Diametr (m)",
        "col_speed": "Sürət (km/s)",
        "col_distance": "Məsafə (km)",
        "col_hazardous": "Təhlükəli",
        "col_hazardous_help": "NASA təhlükəli kimi işarələyib",
        "col_explanation": "İzah",
        "filter_status": "Status",
        "filter_name": "Ada görə axtar",
        "filter_name_ph": "məs. VU25",
        "filter_hazardous": "Yalnız NASA təhlükəliləri",
        "filter_distance": "Maksimal məsafə (milyon km)",
        "filter_distance_help": "Limitsiz üçün sona qədər çəkin.",
        "table_caption": "**{n}** asteroid · {start} – {end} · əvvəl riskə, sonra məsafəyə "
                         "görə sıralanıb",
        "no_match": "Bu filtrlərə uyğun asteroid yoxdur.",
    },
}
