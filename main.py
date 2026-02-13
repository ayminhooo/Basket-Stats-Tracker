import streamlit as st
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="Basket Pro Tracker", layout="wide")

# CSS pour l'ergonomie - Corrigé pour éviter les erreurs de syntaxe CSS
st.markdown("""
    <style>
    .stButton>button {
        height: 3.5em;
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #d1d1d1;
    }
    div[data-testid="column"] {
        padding: 10px;
        border: 1px dashed #cccccc;
        border-radius: 12px;
        background-color: #fcfcfc;
    }
    .main {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Données des joueurs (Ordre précis 4-16)
PLAYERS_DATA = [
    {"num": 4, "name": "Timéo"}, {"num": 5, "name": "Yehya"}, 
    {"num": 6, "name": "Yannis"}, {"num": 7, "name": "Ronice"}, 
    {"num": 8, "name": "Keran"}, {"num": 9, "name": "M'Baye"}, 
    {"num": 10, "name": "Jobin"}, {"num": 11, "name": "Klérance"}, 
    {"num": 12, "name": "Franck"}, {"num": 13, "name": "Johan"}, 
    {"num": 14, "name": "Lucas"}, {"num": 15, "name": "Mehdi"}, 
    {"num": 16, "name": "Antoine"}
]

PLAYER_NAMES = [p["name"] for p in PLAYERS_DATA]

# 3. Initialisation du session_state
if 'stats' not in st.session_state:
    st.session_state.stats = {p["name"]: {
        "2pts_M": 0, "2pts_A": 0, "3pts_M": 0, "3pts_A": 0, "LF_M": 0, "LF_A": 0,
        "REB_OFF": 0, "REB_DEF": 0, "AST": 0, "TO": 0, "FTS": 0
    } for p in PLAYERS_DATA}

if 'on_court' not in st.session_state:
    st.session_state.on_court = []

# 4. Fonctions de gestion
def add_stat(player, key, is_made=False):
    if is_made:
        st.session_state.stats[player][key + "_M"] += 1
        st.session_state.stats[player][key + "_A"] += 1
    else:
        st.session_state.stats[player][key] += 1

def toggle_court(player):
    if player in st.session_state.on_court:
        st.session_state.on_court.remove(player)
    else:
        if len(st.session_state.on_court) < 5:
            st.session_state.on_court.append(player)
        else:
            st.warning("Action impossible : Déjà 5 joueurs sur le terrain.")

# --- SCORE ÉQUIPE ---
total_score = sum((s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"] for s in st.session_state.stats.values())

# --- INTERFACE ---
c_title, c_score = st.columns([3, 1])
with c_title:
    st.title("🏀 Basket Stats Live Tracker")
with c_score:
    st.metric("SCORE ÉQUIPE", f"{total_score} pts")

# SECTION 1 : TERRAIN
st.subheader(f"🏟️ Rotation Terrain ({len(st.session_state.on_court)}/5)")
court_cols = st.columns(5)
for i in range(5):
    with court_cols[i]:
        if i < len(st.session_state.on_court):
            p_name = st.session_state.on_court[i]
            p_num = next(p["num"] for p in PLAYERS_DATA if p["name"] == p_name)
            s = st.session_state.stats[p_name]
            p_pts = (s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"]
            
            st.markdown(f"**#{p_num} {p_name}**")
            st.write(f"Points: **{p_pts}**")
            
            # Tirs
            for shot in ["2pts", "3pts", "LF"]:
                c1, c2 = st.columns(2)
                c1.button(f"✅{shot}", key=f"m_{p_name}_{shot}", on_click=add_stat, args=(p_name, shot, True))
                c2.button(f"❌{shot}", key=f"a_{p_name}_{shot}", on_click=add_stat, args=(p_name, shot + "_A"))
            
            # Rebonds
            st.write("---")
            r1, r2 = st.columns(2)
            r1.button(f"OFF:{s['REB_OFF']}", key=f"o_{p_name}", on_click=add_stat, args=(p_name, "REB_OFF"))
            r2.button(f"DEF:{s['REB_DEF']}", key=f"d_{p_name}", on_click=add_stat, args=(p_name, "REB_DEF"))
            
            # Jeu & Fautes
            st.write("---")
            j1, j2, j3 = st.columns(3)
            j1.button("AS", key=f"ast_{p_name}", on_click=add_stat, args=(p_name, "AST"))
            j2.button("BP", key=f"to_{p_name}", on_click=add_stat, args=(p_name, "TO"))
            j3.button("F", key=f"ft_{p_name}", on_click=add_stat, args=(p_name, "FTS"))
            
            st.button("🔄 SORTIR", key=f"out_{p_name}", on_click=toggle_court, args=(p_name,), type="primary")
        else:
            st.info("Libre")

st.divider()

# SECTION 2 : BANC
st.subheader("🪑 Banc (Cliquer pour faire entrer)")
bench_players = [p for p in PLAYER_NAMES if p not in st.session_state.on_court]
bench_cols = st.columns(7)
for i, p_name in enumerate(bench_players):
    with bench_cols[i % 7]:
        st.button(p_name, key=f"in_{p_name}", on_click=toggle_court, args=(p_name,))

# SECTION 3 : BOX SCORE
st.divider()
st.subheader("📊 Box Score Final")

final_data = []
for p_info in PLAYERS_DATA:
    name = p_info["name"]
    s = st.session_state.stats[name]
    pts = (s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"]
    reb_tot = s["REB_OFF"] + s["REB_DEF"]
    fg_m, fg_a = (s["2pts_M"] + s["3pts_M"]), (s["2pts_A"] + s["3pts_A"])
    
    final_data.append({
        "N°": p_info["num"], "Joueur": name, "Pts": pts,
        "FG (M/A)": f"{fg_m}/{fg_a}", "FG%": f"{(fg_m/fg_a*100):.1f}%" if fg_a > 0 else "0%",
        "2P (M/A)": f"{s['2pts_M']}/{s['2pts_A']}", "3P (M/A)": f"{s['3pts_M']}/{s['3pts_A']}",
        "REB OFF": s["REB_OFF"], "REB DEF": s["REB_DEF"], "REB TOT": reb_tot,
        "AST": s["AST"], "TO": s["TO"], "FTS": s["FTS"],
        "EFF": (pts + reb_tot + s["AST"]) - ((fg_a - fg_m) + (s["LF_A"] - s["LF_M"]) + s["TO"])
    })

st.dataframe(pd.DataFrame(final_data), use_container_width=True)

# SIDEBAR OPTIONS
if st.sidebar.button("🗑️ Réinitialiser le match"):
    st.session_state.stats = {p["name"]: {
        "2pts_M": 0, "2pts_A": 0, "3pts_M": 0, "3pts_A": 0, "LF_M": 0, "LF_A": 0,
        "REB_OFF": 0, "REB_DEF": 0, "AST": 0, "TO": 0, "FTS": 0
    } for p in PLAYERS_DATA}
    st.session_state.on_court = []
    st.rerun()

csv = pd.DataFrame(final_data).to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Télécharger Box Score (CSV)", data=csv, file_name="match_stats.csv", mime="text/csv")
