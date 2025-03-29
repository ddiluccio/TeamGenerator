import streamlit as st
import pandas as pd
import itertools
import random

# Load players from CSV
@st.cache_data
def load_players(filename="players.csv"):
    return pd.read_csv(filename)

# Calculate team feature sums
def calculate_team_stats(team):
    total_defense = sum(team["Defense"])
    total_pass = sum(team["Pass"])
    total_attack = sum(team["Attack"])
    total_physic = sum(team["Physic"])  # New feature
    return total_defense, total_pass, total_attack, total_physic

# Compute the best team split balancing all features
def find_best_teams(players_df):
    players = players_df.to_dict(orient="records")
    
    # Shuffle players randomly
    random.shuffle(players)

    best_splits = []
    min_difference = float("inf")

    # Generate all possible 5-player team combinations
    for team_A in itertools.combinations(players, 5):
        team_B = [player for player in players if player not in team_A]

        # Convert lists to DataFrame
        df_A = pd.DataFrame(team_A)
        df_B = pd.DataFrame(team_B)

        # Compute team feature sums
        stats_A = calculate_team_stats(df_A)
        stats_B = calculate_team_stats(df_B)

        # Compute individual feature differences
        differences = [abs(a - b) for a, b in zip(stats_A, stats_B)]
        max_difference = max(differences)  # Ensure each feature is balanced

        # Check if this split is better or equally good
        if max_difference < min_difference:
            min_difference = max_difference
            best_splits = [(df_A, df_B, stats_A, stats_B)]
        elif max_difference == min_difference:
            best_splits.append((df_A, df_B, stats_A, stats_B))

    # Choose a random best split if multiple exist
    best_split = random.choice(best_splits) if best_splits else None

    return best_split, min_difference, len(best_splits)

# Streamlit UI
st.title("⚽ Team Generator per dei veri calcetti")

# Load and display player data
players_df = load_players()

st.subheader("Select 10 Players")
selected_players = st.multiselect("Choose exactly 10 players:", players_df["Name"].tolist())

# Abilita il bottone solo se sono selezionati 10 giocatori
button_disabled = len(selected_players) != 10
if button_disabled:
    st.warning("⚠️ Seleziona esattamente 10 giocatori per abilitare il bottone!")

# Bottone per calcolare le squadre
if st.button("🔄 Genera Squadre", disabled=button_disabled):
    # Filter selected players
    selected_df = players_df[players_df["Name"].isin(selected_players)]
    
    # Compute best team split
    best_teams, min_diff, num_combinations = find_best_teams(selected_df)

    if best_teams:
        team_A, team_B, stats_A, stats_B = best_teams

        # Display Teams
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

        # Display summed stats comparison
        st.subheader("📊 Team Stats Comparison")
        stats_df = pd.DataFrame({
            "Feature": ["Defense", "Pass", "Attack", "Physic"],
            "Team A (Bianchi)": stats_A,
            "Team B (Blu)": stats_B
        })
        st.dataframe(stats_df.set_index("Feature"))
    else:
        st.error("⚠️ Nessuna combinazione valida trovata!")
