"""Asteroid dashboard (Streamlit). Display code only.

Data is read from db.py and imported via data_loader.py; all calculations
(status, most dangerous asteroid, history, filters, summary) come from logic.py. All user-visible text comes from
i18n.py (English / Azerbaijani). This file only renders and formats.

Tabs:
  Now      — today's most dangerous asteroid: colored status card + explanation
  History  — 14-day Plotly line chart (distance from Earth), red statuses as red points
  Table    — filterable table

Run:  py -m streamlit run app.py
"""

from datetime import date
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data_loader
import db
import i18n
import logic
import simulator
from logic import GREEN, RED, YELLOW

HISTORY_DAYS = 14
MAX_DISTANCE_MLN = 80.0          # slider end = "no limit"

# --- Colors (dark surface; matches .streamlit/config.toml) -------------------
SURFACE, PAGE = "#1a1a19", "#0d0d0d"
INK, INK_2, MUTED = "#f0efec", "#c3c2b7", "#898781"
GRID, AXIS, BORDER = "#2c2c2a", "#383835", "rgba(255,255,255,0.10)"
SERIES = "#3987e5"
STATUS_COLOR = {GREEN: "#0ca30c", YELLOW: "#fab219", RED: "#d03b3b"}
ICONS = {GREEN: "🟢", YELLOW: "🟡", RED: "🔴"}
STATUS_KEY = {GREEN: "green", YELLOW: "yellow", RED: "red"}

TABLE_COLUMNS = ["status", "name", "date", "diameter_m", "speed_kms",
                 "distance_km", "hazardous", "explanation"]

CSS = f"""
<style>
.block-container {{ padding-top: 2.2rem; max-width: 1200px; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 0.5rem; border-bottom: 1px solid {GRID}; }}
.stTabs [data-baseweb="tab"] {{ font-size: 1rem; padding: 0.6rem 1rem; }}
.hero {{ display:flex; justify-content:space-between; align-items:flex-end;
         flex-wrap:wrap; gap:0.8rem; margin-bottom:0.6rem; }}
.hero h1 {{ font-size:2.1rem; margin:0; padding:0; color:{INK}; }}
.hero .sub {{ color:{MUTED}; font-size:0.95rem; margin-top:0.2rem; }}
.chips {{ display:flex; gap:0.5rem; flex-wrap:wrap; }}
.chip {{ border:1px solid {BORDER}; background:{SURFACE}; color:{INK_2};
         border-radius:999px; padding:0.25rem 0.75rem; font-size:0.85rem; }}
.card {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:14px;
         padding:1.4rem 1.6rem; }}
.status-card {{ border-left-width:8px; }}
.eyebrow {{ color:{MUTED}; font-size:0.8rem; text-transform:uppercase;
            letter-spacing:0.08em; }}
.big-name {{ font-size:2.2rem; font-weight:700; color:{INK}; margin:0.3rem 0 0.6rem; }}
.pill {{ display:inline-block; border-radius:999px; padding:0.2rem 0.75rem;
         font-size:0.85rem; font-weight:600; }}
.explain {{ color:{INK_2}; font-size:1.02rem; line-height:1.55; margin-top:1rem; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(190px, 1fr));
          gap:0.8rem; margin-top:0.9rem; }}
.tile {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:12px;
         padding:0.9rem 1.1rem; }}
.tile .label {{ color:{MUTED}; font-size:0.82rem; }}
.tile .value {{ color:{INK}; font-size:1.6rem; font-weight:650; margin:0.15rem 0; }}
.tile .note {{ color:{MUTED}; font-size:0.78rem; }}
.rule {{ color:{MUTED}; font-size:0.82rem; margin-top:0.9rem; }}
.steps {{ color:{INK_2}; margin:0.6rem 0 0; }}
.facts {{ display:flex; flex-direction:column; gap:0.75rem; margin-top:0.8rem; }}
.fact {{ display:flex; gap:0.8rem; align-items:flex-start; }}
.fact .ico {{ font-size:1.4rem; line-height:1.2; }}
.fact .t {{ color:{INK}; font-size:0.98rem; }}
.fact .s {{ color:{MUTED}; font-size:0.8rem; }}
.half {{ height:100%; }}
.counts {{ display:grid; grid-template-columns:repeat(2, 1fr); gap:0.6rem; margin-top:0.8rem; }}
.count {{ border-radius:10px; padding:0.7rem 0.9rem; background:{PAGE};
          border:1px solid {BORDER}; }}
.count .n {{ font-size:1.6rem; font-weight:700; color:{INK}; }}
.count .l {{ color:{INK_2}; font-size:0.85rem; }}
.count .s {{ color:{MUTED}; font-size:0.75rem; }}
</style>
"""

LANG = i18n.EN   # set in main() from the language switch


# --- Text helpers ------------------------------------------------------------
def t(key, **values):
    """Text for the current language, with {placeholders} filled in."""
    text = i18n.TEXT[LANG][key]
    return text.format(**values) if values else text


def status_name(status):
    return t(f"status_{STATUS_KEY[status]}")


def status_title(status):
    return t(f"title_{STATUS_KEY[status]}")


def explain(asteroid):
    """Explanation sentence in the current language, built from logic.classify reasons."""
    name = asteroid.get("name") or "Asteroid"
    values = {"distance": fmt(asteroid.get("distance_km"), ",.0f"),
              "diameter": fmt(asteroid.get("diameter_m"), ",.0f")}
    status, reasons = asteroid["status"], asteroid["reasons"]
    if status == YELLOW:
        listed = ", ".join(t(f"reason_{code}", **values) for code in reasons)
        return t("explain_yellow", name=name, reasons=listed)
    return t(f"explain_{STATUS_KEY[status]}", name=name, **values)


def source_label(source):
    return t("source_real") if source == db.REAL else t("source_sim")


def column_config():
    return {
        "status": st.column_config.TextColumn(t("col_status"), width="small"),
        "name": t("col_name"),
        "date": st.column_config.DateColumn(t("col_date"), format="DD.MM.YYYY"),
        "diameter_m": st.column_config.NumberColumn(t("col_diameter"), format="%,d"),
        "speed_kms": st.column_config.NumberColumn(t("col_speed"), format="%.1f"),
        "distance_km": st.column_config.NumberColumn(t("col_distance"), format="%,d"),
        "hazardous": st.column_config.CheckboxColumn(t("col_hazardous"), width="small",
                                                     help=t("col_hazardous_help")),
        "explanation": st.column_config.TextColumn(t("col_explanation"), width="large"),
    }


# --- Language-safe choice widgets --------------------------------------------
# The widgets show translated labels, but the real choice (e.g. 'real', 'sim',
# 'qırmızı') is kept in session_state under "<key>_value". Each language gets its
# own widget key, so a label from the other language can never come back as a value.
def choice_radio(container, label, options, fmt, key, **kwargs):
    state = f"{key}_value"
    current = st.session_state.get(state, options[0])
    labels = [fmt(o) for o in options]
    picked = container.radio(label, labels, index=options.index(current),
                             key=f"{key}_{LANG}", **kwargs)
    st.session_state[state] = options[labels.index(picked)]
    return st.session_state[state]


def choice_multiselect(container, label, options, fmt, key, **kwargs):
    state = f"{key}_value"
    current = st.session_state.get(state, list(options))
    labels = [fmt(o) for o in options]
    picked = container.multiselect(label, labels, default=[fmt(o) for o in current],
                                   key=f"{key}_{LANG}", **kwargs)
    st.session_state[state] = [o for o, lab in zip(options, labels) if lab in picked]
    return st.session_state[state]


# --- Small helpers (formatting only) -----------------------------------------
def fmt(value, pattern, unit=""):
    """Format a number; '—' for empty/NaN values."""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:{pattern}}{' ' + unit if unit else ''}"


def status_label(status):
    return f"{ICONS.get(status, '⚪')} {status_name(status)}"


def pill(status):
    text_color = "#0b0b0b" if status == YELLOW else "#ffffff"
    return (f'<span class="pill" style="background:{STATUS_COLOR[status]}; '
            f'color:{text_color};">{ICONS[status]} {status_name(status)} · '
            f'{status_title(status)}</span>')


def tiles(items):
    """items: [(label, value, note), ...] -> a row of stat tiles."""
    cells = "".join(
        f'<div class="tile"><div class="label">{escape(label)}</div>'
        f'<div class="value">{escape(value)}</div>'
        f'<div class="note">{escape(note)}</div></div>'
        for label, value, note in items
    )
    st.markdown(f'<div class="tiles">{cells}</div>', unsafe_allow_html=True)


def show_table(df, columns, **kwargs):
    """Show a table with icon status labels and real date values."""
    view = df.assign(status=df["status"].map(status_label))
    if "explanation" in columns:
        view = view.assign(explanation=[explain(r) for r in df.to_dict("records")])
    if "date" in columns:
        view = view.assign(date=pd.to_datetime(view["date"]))
    if "hazardous" in columns:
        view = view.assign(hazardous=view["hazardous"].astype(bool))
    st.dataframe(view[columns], hide_index=True, width="stretch",
                 column_config=column_config(), **kwargs)


# --- Sidebar -----------------------------------------------------------------
def sidebar():
    """Source, date and data upload/simulation. Returns (source, today)."""
    with st.sidebar:
        st.markdown(t("control_panel"))
        source = choice_radio(st, t("data_source"), list(db.SOURCES), source_label,
                              key="source")
        today = st.date_input(t("today"), value=date.today(), format="DD.MM.YYYY",
                              key="today")
        st.divider()

        if source == db.REAL:
            st.markdown(t("upload_heading"))
            uploaded = st.file_uploader(t("csv_file"), type="csv", key="upload",
                                        label_visibility="collapsed")
            if uploaded is not None and st.button(t("save_button"), type="primary",
                                                  width="stretch", key="save"):
                try:
                    n = data_loader.import_csv(uploaded)
                    st.success(t("saved", n=n))
                except Exception as e:  # show bad CSV errors to the user
                    st.error(t("upload_failed", error=e))
            st.caption(t("required_columns"))
        else:
            st.markdown(t("sim_heading"))
            st.caption(t("sim_caption", days=simulator.DAYS, red_day=simulator.RED_DAY))
            seed = st.number_input(t("seed"), min_value=0, value=42, step=1, key="seed")
            if st.button(t("sim_button"), type="primary", width="stretch", key="simulate"):
                sim = simulator.simulate(simulator.start_for_today(today), int(seed))
                n = data_loader.import_simulation(sim)
                st.success(t("sim_saved", n=n))
    return source, today


def hero(source, today, start, end):
    st.markdown(
        f'<div class="hero"><div><h1>{t("title")}</h1>'
        f'<div class="sub">{t("subtitle")}</div></div>'
        f'<div class="chips"><span class="chip">{source_label(source)}</span>'
        f'<span class="chip">📅 {today:%d.%m.%Y}</span>'
        f'<span class="chip">{t("period_chip", start=f"{start:%d.%m}", end=f"{end:%d.%m}")}'
        f'</span></div></div>',
        unsafe_allow_html=True,
    )


def glossary():
    with st.expander(t("glossary_title")):
        st.markdown(t("glossary", close_km=f"{logic.CLOSE_DISTANCE_KM:,}",
                      lunar_km=f"{logic.LUNAR_DISTANCE_KM:,}"))


def empty_state(today, source):
    steps = t("steps_real") if source == db.REAL else t("steps_sim")
    st.markdown(
        f'<div class="card"><div class="eyebrow">{t("no_data_for", day=f"{today:%d.%m.%Y}")}'
        f'</div><div class="big-name" style="font-size:1.5rem;">{t("nothing_yet")}</div>'
        f'<ol class="steps">{steps}</ol></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    glossary()


def perspective_card(top):
    """Plain-language comparisons for one asteroid (values from logic.perspective)."""
    p = logic.perspective(top)
    facts = []
    if p["lunar_distances"] is not None:
        facts.append(("🌙", t("moon", ld=f"{p['lunar_distances']:,.1f}"),
                      t("moon_note", lunar_km=f"{logic.LUNAR_DISTANCE_KM:,}")))
    if p["size_ref"] is not None:
        label, ratio = p["size_ref"]
        label = t("size_refs").get(label, label)
        size_text = (t("size_about", label=label) if 0.8 <= ratio <= 1.25
                     else t("size_times", ratio=f"{ratio:,.1f}", label=label))
        facts.append(("📏", size_text, t("size_note")))
    if p["bullet_ratio"] is not None:
        facts.append(("💨", t("bullet", ratio=f"{p['bullet_ratio']:,.0f}"),
                      t("bullet_note", minutes=f"{p['seconds_to_cross_earth'] / 60:,.0f}")))
    rows = "".join(
        f'<div class="fact"><div class="ico">{ico}</div><div>'
        f'<div class="t">{escape(text)}</div><div class="s">{escape(note)}</div></div></div>'
        for ico, text, note in facts
    ) or f'<div class="fact"><div class="s">{t("no_comparisons")}</div></div>'
    return (f'<div class="card half"><div class="eyebrow">{t("perspective")}</div>'
            f'<div class="facts">{rows}</div></div>')


def counts_card(df, today):
    """Today's asteroid counts per status (values from logic.day_overview)."""
    o = logic.day_overview(df, today)
    cells = [(t("total_today"), o["total"], t("asteroids"))] + [
        (status_label(s), o[s], status_title(s)) for s in (RED, YELLOW, GREEN)]
    counts = "".join(
        f'<div class="count"><div class="n">{n}</div><div class="l">{label}</div>'
        f'<div class="s">{escape(note)}</div></div>'
        for label, n, note in cells
    )
    return (f'<div class="card half"><div class="eyebrow">'
            f'{t("at_a_glance", day=f"{today:%d.%m.%Y}")}</div>'
            f'<div class="counts">{counts}</div></div>')


# --- Tab: Now ----------------------------------------------------------------
def render_now(df, today, source):
    top = logic.most_dangerous(df, today)      # selected using classify
    if top is None:
        empty_state(today, source)
        return

    status = top["status"]
    color = STATUS_COLOR[status]
    st.markdown(
        f'<div class="card status-card" style="border-left-color:{color}; '
        f'box-shadow: inset 0 0 0 1px {color}33;">'
        f'<div class="eyebrow">{t("most_dangerous", day=f"{today:%d.%m.%Y}")}</div>'
        f'<div class="big-name">{escape(str(top["name"]))}</div>'
        f'{pill(status)}'
        f'<div class="explain"><b>{t("explanation")}</b> {escape(explain(top))}</div></div>',
        unsafe_allow_html=True,
    )

    tiles([
        (t("distance_from_earth"), fmt(top.get("distance_km"), ",.0f", "km"),
         t("close_limit", km=f"{logic.CLOSE_DISTANCE_KM:,}")),
        (t("diameter"), fmt(top.get("diameter_m"), ",.0f", "m"),
         t("large_limit", m=logic.LARGE_DIAMETER_M)),
        (t("speed"), fmt(top.get("speed_kms"), ".1f", "km/s"), t("relative_to_earth")),
        (t("nasa_flag"), t("hazardous_yes") if top.get("hazardous") else t("hazardous_no"),
         t("pha")),
    ])
    st.markdown(
        f'<div class="rule">{t("rule", km=f"{logic.CLOSE_DISTANCE_KM:,}", m=logic.LARGE_DIAMETER_M)}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.write("")
    left, right = st.columns(2)
    left.markdown(perspective_card(top), unsafe_allow_html=True)
    right.markdown(counts_card(df, today), unsafe_allow_html=True)
    st.write("")
    glossary()


# --- Tab: History ------------------------------------------------------------
def history_figure(daily, red):
    fig = go.Figure()
    # Close-approach zone (threshold comes from logic.py)
    fig.add_hrect(y0=0, y1=logic.CLOSE_DISTANCE_KM, fillcolor=STATUS_COLOR[RED],
                  opacity=0.08, line_width=0)
    fig.add_hline(y=logic.CLOSE_DISTANCE_KM,
                  line=dict(color=STATUS_COLOR[RED], width=1, dash="dot"),
                  annotation_text=t("close_line"),
                  annotation_position="top left",
                  annotation_font=dict(color=INK_2, size=11))
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(daily["date"]), y=daily["distance_km"],
        mode="lines+markers", name=t("closest_of_day"),
        line=dict(color=SERIES, width=2),
        marker=dict(size=8, color=SERIES, line=dict(color=SURFACE, width=2)),
        customdata=daily[["name"]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{x|%d.%m.%Y}<br>"
                      "%{y:,.0f} km<extra></extra>",
    ))
    if not red.empty:
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(red["date"]), y=red["distance_km"],
            mode="markers", name=t("red_status"),
            marker=dict(color=STATUS_COLOR[RED], size=15,
                        line=dict(color=SURFACE, width=2)),
            customdata=red[["name"]],
            hovertemplate="<b>🔴 %{customdata[0]}</b><br>%{x|%d.%m.%Y}<br>"
                          "%{y:,.0f} km<extra></extra>",
        ))
    fig.update_layout(
        title=dict(text=t("chart_title", days=HISTORY_DAYS),
                   font=dict(color=INK, size=16), x=0, xanchor="left"),
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(color=INK_2, family="system-ui, Segoe UI, sans-serif"),
        hovermode="closest",
        hoverlabel=dict(bgcolor=PAGE, bordercolor=BORDER, font_color=INK),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=1, xanchor="right"),
        margin=dict(l=16, r=16, t=70, b=16), height=440,
    )
    fig.update_xaxes(type="date", tickformat="%d.%m", title=t("axis_date"),
                     showgrid=False, linecolor=AXIS, tickfont=dict(color=MUTED))
    fig.update_yaxes(tickformat=",.0f", rangemode="tozero", title=t("axis_distance"),
                     gridcolor=GRID, zeroline=False, linecolor=AXIS,
                     tickfont=dict(color=MUTED))
    return fig


def render_history(df, start, end):
    hist = logic.distance_history(df)
    daily, red = hist["daily"], hist["red"]
    if daily.empty:
        st.info(t("no_period_data"), icon="🔭")
        glossary()
        return

    summary = logic.weekly_summary(df)
    closest = summary["closest"] or {}
    tiles([
        (t("tracked"), f"{summary['count']:,}", f"{start:%d.%m.%Y} – {end:%d.%m.%Y}"),
        (t("closest_approach"), fmt(closest.get("distance_km"), ",.0f", "km"),
         str(closest.get("name", "—"))),
        (t("average_speed"), fmt(summary["avg_speed_kms"], ".1f", "km/s"),
         t("unusually_fast", n=len(summary["fast"]))),
        (t("red_events"), str(len(red)), t("all_three")),
    ])
    st.write("")
    st.plotly_chart(history_figure(daily, red), width="stretch",
                    config={"displaylogo": False})
    st.caption(t("chart_caption"))

    if red.empty:
        st.success(t("no_red"), icon="✅")
    else:
        st.markdown(t("red_events_heading"))
        show_table(red, ["status", "date", "name", "distance_km", "explanation"])
    st.write("")
    glossary()


# --- Tab: Table --------------------------------------------------------------
def render_table(df, start, end):
    with st.container(border=True):
        f1, f2, f3 = st.columns([2, 2, 1.2], vertical_alignment="bottom")
        statuses = choice_multiselect(f1, t("filter_status"), [RED, YELLOW, GREEN],
                                      status_label, key="f_status")
        name_query = f2.text_input(t("filter_name"), placeholder=t("filter_name_ph"),
                                   key="f_name")
        hazardous_only = f3.toggle(t("filter_hazardous"), key="f_hazardous")
        max_mln = st.slider(t("filter_distance"), 0.5, MAX_DISTANCE_MLN,
                            MAX_DISTANCE_MLN, step=0.5, format="%.1f",
                            help=t("filter_distance_help"), key="f_distance")

    table = logic.filter_asteroids(
        df,
        statuses=statuses,
        name_query=name_query,
        hazardous_only=hazardous_only,
        max_distance_km=None if max_mln >= MAX_DISTANCE_MLN else max_mln * 1_000_000,
    )
    st.caption(t("table_caption", n=len(table), start=f"{start:%d.%m.%Y}",
                 end=f"{end:%d.%m.%Y}"))
    if table.empty:
        st.info(t("no_match"), icon="🔍")
        return
    show_table(table, TABLE_COLUMNS, height=520)


# --- Page --------------------------------------------------------------------
def main():
    global LANG
    st.set_page_config(page_title="Asteroid Monitor", page_icon="☄️", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    db.init_db()

    # Language switch first, so every label below uses the chosen language
    LANG = st.sidebar.radio("🌐 Language / Dil", list(i18n.LANGUAGES),
                            format_func=i18n.LANGUAGES.get, horizontal=True, key="lang")
    st.sidebar.divider()

    source, today = sidebar()
    start, end = logic.history_window(today, HISTORY_DAYS)
    hero(source, today, start, end)

    df = db.get_asteroids_between(start, end, source=source)

    tab_now, tab_history, tab_table = st.tabs([t("tab_now"), t("tab_history"),
                                               t("tab_table")])
    with tab_now:
        render_now(df, today, source)
    with tab_history:
        render_history(df, start, end)
    with tab_table:
        render_table(df, start, end)


main()
