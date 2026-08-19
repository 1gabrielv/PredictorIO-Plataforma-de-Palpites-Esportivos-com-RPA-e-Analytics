import pandas as pd
import database as db

def calculate_match_points(row):
    if pd.isna(row['home_goals']) or pd.isna(row['away_goals']):
        return 0
    
    real_home = int(row['home_goals'])
    real_away = int(row['away_goals'])
    pred_home = int(row['predicted_home_goals'])
    pred_away = int(row['predicted_away_goals'])

    if real_home == pred_home and real_away == pred_away:
        return 12
    
    real_winner = 'home' if real_home > real_away else 'away' if real_home < real_away else 'draw'
    pred_winner = 'home' if pred_home > pred_away else 'away' if pred_home < pred_away else 'draw'

    if real_winner == pred_winner:
        if (real_home == pred_home) or (real_away == pred_away):
            return 7
        return 5

    if (real_home == pred_home) or (real_away == pred_away):
        return 2

    return 0

def generate_ranking():
    conn = db.connect()
    df_predictions = pd.read_sql_query("SELECT * FROM predictions", conn)
    df_matches = pd.read_sql_query("SELECT id, home_goals, away_goals FROM matches", conn)
    df_users = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()

    if df_predictions.empty:
        return pd.DataFrame(columns=['Name', 'Total Points'])
    
    df_merged = pd.merge(df_predictions, df_matches, left_on='match_id', right_on='id', suffixes=('_pred', '_real'))
    df_merged['points_earned'] = df_merged.apply(calculate_match_points, axis=1)
    df_final = pd.merge(df_merged, df_users, left_on='user_id', right_on='id')

    ranking = df_final.groupby('name')['points_earned'].sum().reset_index()
    ranking.columns = ['Name', 'Total Points']
    ranking = ranking.sort_values(by='Total Points', ascending=False).reset_index(drop=True)
    return ranking

def get_user_match_history(user_id):
    conn = db.connect()
    query = """
        SELECT 
            m.home_team, 
            m.away_team, 
            m.match_date, 
            m.home_goals, 
            m.away_goals,
            p.predicted_home_goals, 
            p.predicted_away_goals
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        WHERE p.user_id = ?
        ORDER BY m.id ASC
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df.empty:
        return df

    df['points'] = df.apply(calculate_match_points, axis=1)
    return df