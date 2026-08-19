import streamlit as st
import database as db
import engine as eng
import scraper

st.set_page_config(page_title="Bolão Nota 10", page_icon="⚽", layout="centered")

db.create_tables()

if "user" not in st.session_state:
    st.session_state["user"] = None  


def show_login_page():
    st.title("⚽ Bolão Nota 10")
    st.subheader("Welcome! Please log in or register to continue.")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Log In"):
            user_data = db.verify_login(username, password)
            if user_data:
                st.session_state["user"] = user_data
                st.success(f"Welcome back, {user_data[1]}!")
                st.rerun() 
            else:
                st.error("Invalid username or password.")

    with tab_register:
        new_name = st.text_input("Full Name", key="reg_name")
        new_username = st.text_input("Choose Username", key="reg_user")
        new_password = st.text_input("Choose Password", type="password", key="reg_pass")

        if st.button("Create Account"):
            if new_name and new_username and new_password:
                success = db.register_user(new_name, new_username, new_password)
                if success:
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Username already taken. Please choose another one.")
            else:
                st.warning("Please fill in all fields.")


def show_main_dashboard():
    user_id, user_name = st.session_state["user"]

    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.title("⚽ Bolão Dashboard")
        st.write(f"Logged in as: **{user_name}**")
    with col_logout:
        if st.button("Log Out"):
            st.session_state["user"] = None
            st.rerun()

    st.divider()

    tab_predictions, tab_ranking = st.tabs(["🎯 Submit Predictions", "🏆 Leaderboard"])

    with tab_predictions:
        col_header, col_sync = st.columns([3, 1])
        with col_header:
            st.subheader("Upcoming Matches")
        with col_sync:
            if st.button("🔄 Sincronizar Jogos FIFA"):
                with st.spinner("Buscando jogos da FIFA..."):
                    scraper.run_fifa_scraper()
                st.success("Jogos atualizados!")
                st.rerun()

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, home_team, away_team, match_date, home_goals, away_goals FROM matches")
        matches = cursor.fetchall()
        conn.close()

        if not matches:
            st.info("Nenhuma partida encontrada. Clique no botão acima para carregar os jogos da FIFA.")
        else:
            for match_id, home_team, away_team, match_date, actual_home, actual_away in matches:
                st.markdown(f"### {home_team} vs {away_team}")
                st.caption(f"📅 Data: {match_date}")

                conn = db.connect()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT predicted_home_goals, predicted_away_goals 
                    FROM predictions 
                    WHERE user_id = ? AND match_id = ?
                """, (user_id, match_id))
                existing_prediction = cursor.fetchone()
                conn.close()

                default_home = existing_prediction[0] if existing_prediction else 0
                default_away = existing_prediction[1] if existing_prediction else 0

                col_home, col_vs, col_away, col_btn = st.columns([2, 1, 2, 2])
                with col_home:
                    pred_home = st.number_input(f"{home_team}", min_value=0, value=default_home, key=f"home_{match_id}")
                with col_vs:
                    st.write("### x")
                with col_away:
                    pred_away = st.number_input(f"{away_team}", min_value=0, value=default_away, key=f"away_{match_id}")
                with col_btn:
                    st.write(" ")
                    if st.button("Salvar Palpite", key=f"btn_{match_id}"):
                        db.save_prediction(user_id, match_id, int(pred_home), int(pred_away))
                        st.success("Salvo!")

                st.divider()

    with tab_ranking:
        st.subheader("Current Leaderboard")

        if st.button("🔄 Refresh Leaderboard"):
            st.rerun()

        df_ranking = eng.generate_ranking()

        if df_ranking.empty:
            st.info("No scores calculated yet.")
        else:
            st.dataframe(df_ranking, use_container_width=True)


if st.session_state["user"] is None:
    show_login_page()
else:
    show_main_dashboard()