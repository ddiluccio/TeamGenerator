import streamlit as st
import pandas as pd
import itertools
import random
import os

CSV_FILE = "players.csv"

# -------------- Shared Utilities --------------
@st.cache_data
def load_players():
    return pd.read_csv(CSV_FILE)

def save_players(df):
    df.to_csv(CSV_FILE, index=False)
    st.cache_data.clear()

def calculate_team_stats(team):
    total_defense = sum(team["Defense"])
    total_pass = sum(team["Pass"])
    total_attack = sum(team["Attack"])
    total_physic = sum(team["Physic"])
    return total_defense, total_pass, total_attack, total_physic

def find_best_teams(players_df):
    players = sorted(players_df.to_dict(orient="records"), key=lambda p: p["Name"])
    best_splits = []
    min_difference = float("inf")

    for team_A in itertools.combinations(players, 5):
        team_B = [player for player in players if player not in team_A]
        names_A = sorted(p["Name"] for p in team_A)
        names_B = sorted(p["Name"] for p in team_B)
        if names_B < names_A:
            continue

        df_A = pd.DataFrame(team_A)
        df_B = pd.DataFrame(team_B)

        stats_A = calculate_team_stats(df_A)
        stats_B = calculate_team_stats(df_B)
        differences = [abs(a - b) for a, b in zip(stats_A, stats_B)]
        max_difference = max(differences)

        if max_difference < min_difference:
            min_difference = max_difference
            best_splits = [(df_A, df_B, stats_A, stats_B)]
        elif max_difference == min_difference:
            best_splits.append((df_A, df_B, stats_A, stats_B))

    best_split = random.choice(best_splits) if best_splits else None
    return best_split, min_difference, len(best_splits)

# -------------- UI: Sidebar Page Select --------------
st.sidebar.title("📋 Menu")
page = st.sidebar.selectbox("Vai alla pagina:", ["🏆 Team Generator", "🛠️ Editor Giocatori"])

# -------------- Page 1: Team Generator --------------
if page == "🏆 Team Generator":
    st.title("⚽ Team Generator per dei veri calcetti")
    players_df = load_players()

    st.subheader("Select 10 Players")
    selected_players = st.multiselect("Choose exactly 10 players:", players_df["Name"].tolist())

    button_disabled = len(selected_players) != 10
    if button_disabled:
        st.warning("⚠️ Seleziona esattamente 10 giocatori per abilitare il bottone!")

    if st.button("🔄 Genera Squadre", disabled=button_disabled):
        selected_df = players_df[players_df["Name"].isin(selected_players)]
        best_teams, min_diff, num_combinations = find_best_teams(selected_df)

        if best_teams:
            team_A, team_B, stats_A, stats_B = best_teams
            st.subheader("🏆 Best Balanced Teams")
            st.write(f"🔢 Possibili combinazioni con lo stesso punteggio: {num_combinations}")

            col1, col2 = st.columns(2)
            with col1:
                st.write("### Team A - Bianchi")
                st.dataframe(team_A.set_index("Name"))
            with col2:
                st.write("### Team B - Blu")
                st.dataframe(team_B.set_index("Name"))

            st.success(f"✅ Minimum Feature Difference (max diff among attributes): {min_diff}")

            st.subheader("📊 Team Stats Comparison")
            stats_df = pd.DataFrame({
                "Feature": ["Defense", "Pass", "Attack", "Physic"],
                "Team A (Bianchi)": stats_A,
                "Team B (Blu)": stats_B
            })
            st.dataframe(stats_df.set_index("Feature"))
        else:
            st.error("⚠️ Nessuna combinazione valida trovata!")

# -------------- Page 2: Player Editor --------------
elif page == "🛠️ Editor Giocatori":
    st.title("🛠️ Modifica i Giocatori")
    players_df = load_players()
    st.dataframe(players_df)

    st.subheader("➕ Aggiungi un nuovo giocatore")
    with st.form("add_player_form"):
        name = st.text_input("Nome")
        defense = st.number_input("Defense", 0, 10, 5)
        _pass = st.number_input("Pass", 0, 10, 5)
        attack = st.number_input("Attack", 0, 10, 5)
        physic = st.number_input("Physic", 0, 10, 5)
        submitted = st.form_submit_button("Aggiungi")

        if submitted:
            if name.strip() == "":
                st.warning("Il nome non può essere vuoto!")
            else:
                new_row = pd.DataFrame([{
                    "Name": name.strip(),
                    "Defense": defense,
                    "Pass": _pass,
                    "Attack": attack,
                    "Physic": physic
                }])
                updated_df = pd.concat([players_df, new_row], ignore_index=True)
                save_players(updated_df)
                st.success(f"Giocatore '{name}' aggiunto!")
                st.experimental_rerun()

    st.subheader("❌ Elimina giocatori")
    to_delete = st.multiselect("Seleziona giocatori da eliminare:", players_df["Name"].tolist())
    if st.button("Elimina selezionati"):
        updated_df = players_df[~players_df["Name"].isin(to_delete)]
        save_players(updated_df)
        st.success("Giocatori eliminati.")
        st.experimental_rerun()
