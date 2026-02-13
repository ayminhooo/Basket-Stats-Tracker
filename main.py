import streamlit as st
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="Basket Pro Tracker", layout="wide")

# Liste officielle des joueurs [cite: 1]
PLAYERS = [
    "M'Baye", "Lucas", "Yehya", "Ronice", "Jobin", 
    "Antoine", "Johan", "Franck", "Timéo", "Klérance", 
    "Keran", "Yannis", "Mehdi"
]

# 2. Initialisation sécurisée du session_state
if 'stats' not in st.session_state:
    st.session_state.stats = {p: {
        "2pts_M": 0, "2pts_A": 0, 
        "3pts_M": 0, "3pts_A": 0, 
        "LF_M": 0, "LF_A": 0,
        "REB_OFF": 0, "REB_DEF": 0, 
        "AST": 0, "TO": 0, "FTS": 0
    } for p in PLAYERS}

if 'on_court' not in st.session_state:
    st.session_state.on_court = []

# 3. Fonctions de mise à jour (Correction des erreurs de logique)
def add_stat(player, key, is_made=False):
    if is_made:
        # Un panier réussi (Made) incrémente aussi les tentatives (Attempted)
        st.session_state.stats[player][key + "_M"] += 1
        st.session_state.stats[player][key + "_A"] += 1
    else:
        # Incrémentation simple (tentative ratée, rebond, faute, etc.)
        st.session_state.stats[player][key] += 1

def toggle_court(player):
    if player in st.session_state.on_court:
        st.session_state.on_court.remove(player)
    else:
        if len(st.session_state.on_court) < 5:
            st.session_state.on_court.append(player)
        else:
            st.warning("Action impossible : Le terrain est limité à 5 joueurs.")

# --- CALCUL DU SCORE GLOBAL ---
# Calcul basé sur les paniers à 2pts (x2), 3pts (x3) et Lancers-francs (x1) [cite: 2]
total_score = sum((s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"] for s in st.session_state.stats.values())

# --- INTERFACE ---
st.title("🏀 Basket Stats Live Tracker")
st.metric(label="SCORE ÉQUIPE", value=total_score)

# SECTION 1 : LE TERRAIN (Rotation interactive)
st.header(f"🏟️ Sur le terrain ({len(st.session_state.on_court)}/5)")
if not st.session_state.on_court:
    st.info("Sélectionnez des joueurs sur le banc pour les faire entrer.")

court_cols = st.columns(len(st.session_state.on_court) if st.session_state.on_court else 1)

for i, player in enumerate(st.session_state.on_court):
    with court_cols[i]:
        s = st.session_state.stats[player]
        p_pts = (s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"]
        
        st.subheader(player)
        st.write(f"Points: **{p_pts}**")
        
        # Tirs (Réussis ✅ / Ratés ❌)
        for shot in ["2pts", "3pts", "LF"]:
            c1, c2 = st.columns(2)
            c1.button(f"✅ {shot}", key=f"m_{player}_{shot}", on_click=add_stat, args=(player, shot, True), use_container_width=True)
            c2.button(f"❌ {shot}", key=f"a_{player}_{shot}", on_click=add_stat, args=(player, shot + "_A"), use_container_width=True)
        
        # Rebonds
        cr1, cr2 = st.columns(2)
        cr1.button(f"OFF ({s['REB_OFF']})", key=f"off_{player}", on_click=add_stat, args=(player, "REB_OFF"), use_container_width=True)
        cr2.button(f"DEF ({s['REB_DEF']})", key=f"def_{player}", on_click=add_stat, args=(player, "REB_DEF"), use_container_width=True)
        
        # Jeu & Fautes
        cj1, cj2, cj3 = st.columns(3)
        cj1.button("AST", key=f"ast_{player}", on_click=add_stat, args=(player, "AST"), use_container_width=True)
        cj2.button("TO", key=f"to_{player}", on_click=add_stat, args=(player, "TO"), use_container_width=True)
        cj3.button("FTS", key=f"fts_{player}", on_click=add_stat, args=(player, "FTS"), use_container_width=True)
        
        st.button("🔄 SORTIR", key=f"out_{player}", on_click=toggle_court, args=(player,), type="primary", use_container_width=True)

st.divider()

# SECTION 2 : LE BANC
st.header("🪑 Le Banc")
bench_players = [p for p in PLAYERS if p not in st.session_state.on_court]
bench_cols = st.columns(4)
for i, player in enumerate(bench_players):
    with bench_cols[i % 4]:
        st.button(f"➡️ ENTRER : {player}", key=f"in_{player}", on_click=toggle_court, args=(player,), use_container_width=True)

# SECTION 3 : BOX SCORE (Synthèse avec ratios et pourcentages)
st.divider()
st.header("📊 Box Score Complet")

final_data = []
for p in PLAYERS:
    s = st.session_state.stats[p]
    
    # Calculs de base
    pts = (s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"]
    reb_tot = s["REB_OFF"] + s["REB_DEF"]
    
    # Ratios et Pourcentages Généraux (Field Goals)
    fg_m = s["2pts_M"] + s["3pts_M"]
    fg_a = s["2pts_A"] + s["3pts_A"]
    fg_pct = (fg_m / fg_a * 100) if fg_a > 0 else 0
    
    # Pourcentages spécifiques
    p2_pct = (s["2pts_M"] / s["2pts_A"] * 100) if s["2pts_A"] > 0 else 0
    p3_pct = (s["3pts_M"] / s["3pts_A"] * 100) if s["3pts_A"] > 0 else 0
    
    # Évaluation (EFF) 
    # Formule : (Pts + Reb + Ast) - (Tirs manqués + LF manqués + Pertes de balle)
    missed_fg = fg_a - fg_m
    missed_ft = s["LF_A"] - s["LF_M"]
    eff = (pts + reb_tot + s["AST"]) - (missed_fg + missed_ft + s["TO"])
    
    final_data.append({
        "Joueur": p,
        "Pts": pts,
        "FG (M/A)": f"{fg_m}/{fg_a}",
        "FG %": f"{fg_pct:.1f}%",
        "2P (M/A)": f"{s['2pts_M']}/{s['2pts_A']}",
        "2P %": f"{p2_pct:.1f}%",
        "3P (M/A)": f"{s['3pts_M']}/{s['3pts_A']}",
        "3P %": f"{p3_pct:.1f}%",
        "REB OFF": s["REB_OFF"],
        "REB DEF": s["REB_DEF"],
        "REB TOT": reb_tot,
        "AST": s["AST"],
        "TO": s["TO"],
        "FTS": s["FTS"],
        "EFF": eff
    })

df_final = pd.DataFrame(final_data)
st.dataframe(df_final, use_container_width=True)

# SECTION 4 : OPTIONS & EXPORT
st.sidebar.header("Options")
if st.sidebar.button("🗑️ Reset Match"):
    st.session_state.stats = {p: {
        "2pts_M": 0, "2pts_A": 0, "3pts_M": 0, "3pts_A": 0, "LF_M": 0, "LF_A": 0,
        "REB_OFF": 0, "REB_DEF": 0, "AST": 0, "TO": 0, "FTS": 0
    } for p in PLAYERS}
    st.session_state.on_court = []
    st.rerun()

csv = df_final.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Télécharger les Stats (CSV)",
    data=csv,
    file_name="stats_match_complet.csv",
    mime="text/csv"
)
