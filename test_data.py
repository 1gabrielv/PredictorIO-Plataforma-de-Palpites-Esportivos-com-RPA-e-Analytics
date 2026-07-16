import database as db

def insert_test_data():
    db.create_tables()

    db.register_user("John Doe", "johndoe", "password123")
    db.register_user("Jane Smith", "janesmith", "password456")
    db.register_user("Bob Johnson", "bobjohnson", "password789")


    db.add_match("Brazil", "Argentina", "2026-07-20 16:00")
    db.add_match("France", "Germany", "2026-07-21 16:00")
    db.add_match("Japan", "Senegal", "2026-07-22 12:00")

    db.save_prediction(user_id=1, match_id=1, predicted_home_goals=3, predicted_away_goals=1) 
    db.save_prediction(user_id=2, match_id=1, predicted_home_goals=2, predicted_away_goals=0) 
    db.save_prediction(user_id=3, match_id=1, predicted_home_goals=1, predicted_away_goals=2) 

    db.save_prediction(user_id=1, match_id=2, predicted_home_goals=2, predicted_away_goals=2)
    db.save_prediction(user_id=2, match_id=2, predicted_home_goals=1, predicted_away_goals=1)

    print("Test data inserted successfully!")


if __name__ == "__main__":
    insert_test_data()