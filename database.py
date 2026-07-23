import sqlite3

DB_NAME = "bolao.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user TEXT UNIQUE NOT NULL,            
            password TEXT NOT NULL           
        )         
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            match_date TEXT NOT NULL,
            home_goals INTEGER,
            away_goals INTEGER 
        )                                         
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            predicted_home_goals INTEGER NOT NULL,
            predicted_away_goals INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (match_id) REFERENCES matches (id),
            UNIQUE(user_id, match_id)
        )               
    """)

    conn.commit()
    conn.close()

    print("Database and tables created successfully!")


def register_user(name, user, password):
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, user, password) VALUES (?, ?, ?)",
            (name, user, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False    
    finally:
        conn.close()

def verify_login(user, password):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name 
        FROM users 
        WHERE user = ? AND password = ?
    """, (user, password))

    user_data = cursor.fetchone()
    conn.close()
    return user_data

def add_match(home_team, away_team, match_date):    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO matches (home_team, away_team, match_date) VALUES (?, ?, ?)",
        (home_team, away_team, match_date)
    )
    conn.commit()
    conn.close()

def save_prediction(user_id, match_id, predicted_home_goals, predicted_away_goals):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (user_id, match_id, predicted_home_goals, predicted_away_goals)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, match_id)
        DO UPDATE SET 
            predicted_home_goals = excluded.predicted_home_goals,
            predicted_away_goals = excluded.predicted_away_goals
    """, (user_id, match_id, predicted_home_goals, predicted_away_goals))
    
    conn.commit()
    conn.close()

def update_match_result(match_id, home_goals, away_goals):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE matches
        SET home_goals = ?, away_goals = ?
        WHERE id = ?
                   """,
        (home_goals, away_goals, match_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()