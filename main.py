import streamlit as st
import pandas as pd
import itertools

# Load players from CSV
@st.cache_data
def load_players(filename="players.csv"):
    return pd.read_csv(filename)

# Calculate team feature sums
def calculate_team_stats(team):
    total_defense = sum(team["Defense"])
    total_pass = sum(team["Pass"])
    total_attack = sum(team["Attack"])
    return total_defense, total_pass, total_attack

# Compute the best team split using brute force
def find_best_teams(players_df):
    players = players_df.to_dict(orient="records")
    best_split = None
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

        # Compute total difference across all features
        difference = sum(abs(a - b) for a, b in zip(stats_A, stats_B))

        # Check if this split is better
        if difference < min_difference:
            min_difference = difference
            best_split = (df_A, df_B)

    return best_split, min_difference

# Streamlit UI
st.title("⚽ Team Generator per dei veri calcetti")

# Load and display player data
players_df = load_players()

st.subheader("Select 10 Players")
selected_players = st.multiselect("Choose exactly 10 players:", players_df["Name"].tolist())

if len(selected_players) == 10:
    # Filter selected players
    selected_df = players_df[players_df["Name"].isin(selected_players)]
    
    # Compute best team split
    best_teams, min_diff = find_best_teams(selected_df)

    # Display Teams
    st.subheader("🏆 Best Balanced Teams")

    col1, col2 = st.columns(2)
    with col1:
        st.write("### Team A - Bianchi")
        st.dataframe(best_teams[0].set_index("Name"))

    with col2:
        st.write("### Team B - Blu")
        st.dataframe(best_teams[1].set_index("Name"))

    st.success(f"✅ Minimum Feature Difference: {min_diff}")

elif len(selected_players) > 10:
    st.error("⚠️ Please select exactly 10 players!")
