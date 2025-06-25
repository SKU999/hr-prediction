import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Prediction Dashboard", layout="wide")

st.title("Home Run Prediction Dashboard")

uploaded_file = st.file_uploader("Upload Batter vs Pitcher TXT/CSV", type=["csv", "txt"]) 

if uploaded_file:
    # Read as tab-delimited
    df = pd.read_csv(uploaded_file, sep='\t')

    # Ensure numeric columns
    df['vs'] = pd.to_numeric(df['vs'], errors='coerce')
    df['HR'] = pd.to_numeric(df['HR'], errors='coerce')

    # Normalize columns
    df['vs_norm'] = (df['vs'] - df['vs'].min()) / (df['vs'].max() - df['vs'].min())
    df['HR_norm'] = (df['HR'] - df['HR'].min()) / (df['HR'].max() - df['HR'].min())

    # Weighted prediction score (70% vs, 30% HR)
    df['HR_Predict_Score'] = (0.7 * df['vs_norm'] + 0.3 * df['HR_norm']) * 100
    df['HR_Predict_Score'] = df['HR_Predict_Score'].round().astype(int)

    # Team filter
    teams = sorted(df['Tm'].dropna().unique())
    selected_teams = st.multiselect("Filter by Team", options=teams, default=teams)
    filtered_df = df[df['Tm'].isin(selected_teams)]

    # Show results
    st.dataframe(filtered_df[['Batter', 'Tm', 'vs', 'HR', 'HR_Predict_Score']].sort_values(by='HR_Predict_Score', ascending=False), use_container_width=True)

    # Optionally download results
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data as CSV", csv, "filtered_hr_predictions.csv", "text/csv")
else:
    st.info("Please upload a tab-delimited TXT or CSV file to begin.")
