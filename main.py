import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Basket Stats Pro Tracker", layout="wide")

# Liste des joueurs (basée sur tes fichiers)
PLAYERS = [
    "M'Baye", "Lucas", "Yehya", "Ronice", "Jobin", "Kevin", 
    "Antoine", "Johan", "Franck", "Timéo", "Klérance", 
    "Keran", "Yannis", "Mehdi"
]

# Initialisation des statistiques détaillées
if 'stats' not in st.session_state:
    st.session_state.stats = {player: {
        "2pts_M": 0, "2pts_A": 0,  # M = Made (Réussi), A = Attempted (Tenté)
        "3pts_M": 0, "3pts_A": 0,
        "LF_M": 0, "LF_A": 0,
        "REB_OFF": 0, "REB_DEF": 0,
        "AST": 0, "TO": 0, "FTS": 0
    } for player in PLAYERS}

def change_stat(player, stat, delta):
    st.session_state.stats[player][stat] = max(0, st.session_state.stats[player][stat] + delta)
    
    # Logique automatique : Si on marque un panier (Made), on ajoute aussi une tentative (Attempted)
    if delta > 0 and "_M" in stat:
        attempt_stat = stat.replace("_M", "_A")
        st.session_state.stats[player][attempt_stat] += 1
    # Inversement pour la correction d'erreur
    if delta < 0 and "_M" in stat:
        attempt_stat = stat.replace("_M", "_A")
        st.session_state.stats[player][attempt_stat] = max(0, st.session_state.stats[player][attempt_stat] - 1)

st.title("🏀 Basket Stats Pro Tracker")
st.subheader("Suivi avancé : Pourcentages et Rebonds détaillés")

# Interface de saisie
for player in PLAYERS:
    with st.expander(f"👤 {player}", expanded=False):
        # On divise en 4 colonnes principales : Tirs, Rebonds, Jeu, Fautes
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.write("**Tirs (Réussis / Tentés)**")
            for shot in ["2pts", "3pts", "LF"]:
                c_m, c_a = st.columns(2)
                with c_m:
                    st.button(f"✅ {shot}", key=f"add_{player}_{shot}_M", on_click=change_stat, args=(player, f"{shot}_M", 1))
                with c_a:
                    st.button(f"❌ {shot}", key=f"add_{player}_{shot}_A", on_click=change_stat, args=(player, f"{shot}_A", 1))
        
        with col2:
            st.write("**Rebonds**")
            c_off, c_def = st.columns(2)
            with c_off:
                st.write(f"OFF: {st.session_state.stats[player]['REB_OFF']}")
                st.button("➕ Off", key=f"add_{player}_off", on_click=change_stat, args=(player, "REB_OFF", 1))
            with c_def:
                st.write(f"DEF: {st.session_state.stats[player]['REB_DEF']}")
                st.button("➕ Def", key=f"add_{player}_def", on_click=change_stat, args=(player, "REB_DEF", 1))

        with col3:
            st.write("**Jeu**")
            c_ast, c_to = st.columns(2)
            with c_ast:
                st.write(f"AST: {st.session_state.stats[player]['AST']}")
                st.button("➕ Ast", key=f"add_{player}_ast", on_click=change_stat, args=(player, "AST", 1))
            with c_to:
                st.write(f"TO: {st.session_state.stats[player]['TO']}")
                st.button("➕ TO", key=f"add_{player}_to", on_click=change_stat, args=(player, "TO", 1))
                
        with col4:
            st.write("**FTS**")
            st.write(f"F: {st.session_state.stats[player]['FTS']}")
            st.button("➕ F", key=f"add_{player}_f", on_click=change_stat, args=(player, "FTS", 1))

st.divider()

# --- CALCULS ET BOX SCORE ---
st.header("📊 Box Score Détaillé")

data_list = []
for player, s in st.session_state.stats.items():
    # Calcul des points
    pts = (s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"]
    
    # Calcul des pourcentages (évite la division par zéro)
    pct_2p = (s["2pts_M"] / s["2pts_A"] * 100) if s["2pts_A"] > 0 else 0
    pct_3p = (s["3pts_M"] / s["3pts_A"] * 100) if s["3pts_A"] > 0 else 0
    
    # Calcul de l'Évaluation FIBA (EFF)
    # Formule : (Pts + Reb_Tot + Ast + Stl + Blk) - ((FGA - FGM) + (FTA - FTM) + TO)
    missed_fg = (s["2pts_A"] + s["3pts_A"]) - (s["2pts_M"] + s["3pts_M"])
    missed_ft = s["LF_A"] - s["LF_M"]
    reb_tot = s["REB_OFF"] + s["REB_DEF"]
    eff = (pts + reb_tot + s["AST"]) - (missed_fg + missed_ft + s["TO"])
    
    data_list.append({
        "Joueur": player,
        "Pts": pts,
        "2PM/2PA": f"{s['2pts_M']}/{s['2pts_A']}",
        "2P %": f"{pct_2p:.1f}%",
        "3PM/3PA": f"{s['3pts_M']}/{s['3pts_A']}",
        "3P %": f"{pct_3p:.1f}%",
        "LF": f"{s['LF_M']}/{s['LF_A']}",
        "R.OFF": s["REB_OFF"],
        "R.DEF": s["REB_DEF"],
        "TOTAL REB": reb_tot,
        "AST": s["AST"],
        "TO": s["TO"],
        "FTS": s["FTS"],
        "EFF": eff
    })

df = pd.DataFrame(data_list)
st.dataframe(df, use_container_width=True)

# Sidebar pour la gestion globale
st.sidebar.title("Options")
if st.sidebar.button("Réinitialiser le match"):
    st.session_state.stats = {player: {
        "2pts_M": 0, "2pts_A": 0, "3pts_M": 0, "3pts_A": 0,
        "LF_M": 0, "LF_A": 0, "REB_OFF": 0, "REB_DEF": 0,
        "AST": 0, "TO": 0, "FTS": 0
    } for player in PLAYERS}
    st.rerun()

csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Exporter le Box Score (CSV)", csv, "box_score_complet.csv", "text/csv")
