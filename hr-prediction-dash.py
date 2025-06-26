import streamlit as st
import pandas as pd
from itertools import combinations

st.set_page_config(page_title="HR Prediction Dashboard", layout="wide")
st.title("Home Run Prediction + Lineup Optimizer")

# Upload files
uploaded_file = st.file_uploader("Upload Batter vs Pitcher TXT/CSV", type=["csv", "txt"])
salary_file = st.file_uploader("Upload Salary & Position File (CSV with Batter, Salary, Position)", type=["csv"])

if uploaded_file:
    # Read main file (tab-delimited)
    df = pd.read_csv(uploaded_file, sep='\t')

    # Ensure core numeric columns
    df['vs'] = pd.to_numeric(df['vs'], errors='coerce')
    df['HR'] = pd.to_numeric(df['HR'], errors='coerce')

    # Merge salary + position
    if salary_file:
        salary_df = pd.read_csv(salary_file)
        required_cols = {'Batter', 'Salary', 'Position'}
        if required_cols.issubset(salary_df.columns):
            df = df.merge(salary_df[['Batter', 'Salary', 'Position']], on='Batter', how='left')
            df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce').fillna(0)
        else:
            st.error("The salary file must contain columns: Batter, Salary, Position")
            st.stop()
    else:
        df['Salary'] = 0
        df['Position'] = ''

    # Normalize scores
    df['vs_norm'] = (df['vs'] - df['vs'].min()) / (df['vs'].max() - df['vs'].min())
    df['HR_norm'] = (df['HR'] - df['HR'].min()) / (df['HR'].max() - df['HR'].min())
    df['HR_Predict_Score'] = (0.7 * df['vs_norm'] + 0.3 * df['HR_norm']) * 100
    df['HR_Predict_Score'] = df['HR_Predict_Score'].round().astype(int)

    # Team filter
    teams = sorted(df['Tm'].dropna().unique())
    selected_teams = st.multiselect("Filter by Team", options=teams, default=teams)
    filtered_df = df[df['Tm'].isin(selected_teams)]

    # Show table
    st.subheader("Player HR Prediction Scores")
    st.dataframe(
        filtered_df[['Batter', 'Tm', 'vs', 'HR', 'HR_Predict_Score', 'Salary', 'Position']]
        .sort_values(by='HR_Predict_Score', ascending=False),
        use_container_width=True
    )

    # Optimal lineup builder
    st.subheader("Optimal Lineup Generator")
    salary_cap = st.number_input("Salary Cap", value=35000)
    lineup_size = st.number_input("Lineup Size", value=9)

    best_score = 0
    best_lineup = pd.DataFrame()

    for combo in combinations(filtered_df.index, lineup_size):
        lineup = filtered_df.loc[list(combo)]
        total_salary = lineup['Salary'].sum()
        if total_salary <= salary_cap:
            score = lineup['HR_Predict_Score'].sum()
            if score > best_score:
                best_score = score
                best_lineup = lineup

    if not best_lineup.empty:
        st.success(f"Best Lineup Total Score: {best_score} (Salary: {best_lineup['Salary'].sum()})")
        st.dataframe(best_lineup[['Batter', 'Tm', 'Position', 'HR_Predict_Score', 'Salary']], use_container_width=True)
    else:
        st.warning("No valid lineup found under salary cap.")

    # Download option
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data as CSV", csv, "filtered_hr_predictions.csv", "text/csv")

else:
    st.info("Please upload a tab-delimited TXT or CSV file to begin.")
