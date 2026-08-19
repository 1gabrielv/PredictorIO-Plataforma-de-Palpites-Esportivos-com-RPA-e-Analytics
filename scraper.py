from playwright.sync_api import sync_playwright
import database as db

def run_fifa_scraper():
    db.create_tables()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("🌐 Conectando à FIFA...")
        page.goto(
            "https://www.fifa.com/pt/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures?country=BR&wtw-filter=ALL",
            wait_until="domcontentloaded",
            timeout=30000
        )
        
        page.wait_for_selector(".ff-pb-24", timeout=20000)

        for _ in range(4):
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(800)

        match_cards = page.locator(".ff-pb-24").all()
        print(f"🔎 Encontrados {len(match_cards)} blocos na página.")

        conn = db.connect()
        cursor = conn.cursor()
        total_saved = 0

        for card in match_cards:
            title_locator = card.locator(".matches-container_title__ATLsl")
            if title_locator.count() == 0:
                continue

            match_date = title_locator.inner_text().strip()
            match_rows = card.locator(".match-row_matchRowContainer__NoCRI")
            count = match_rows.count()

            for j in range(count):
                row = match_rows.nth(j)
                teams = row.locator(".d-none.d-md-block").all_inner_texts()
                goals_raw = row.locator("[class*='match-row_score']").all_inner_texts()
                goals = [g.strip() for g in goals_raw if g.strip().isdigit()]

                if len(teams) >= 2:
                    home_team = teams[0].strip()
                    away_team = teams[1].strip()

                    cursor.execute("""
                        SELECT id FROM matches 
                        WHERE home_team = ? AND away_team = ?
                    """, (home_team, away_team))
                    match_record = cursor.fetchone()

                    home_goals = int(goals[0]) if len(goals) >= 2 else None
                    away_goals = int(goals[1]) if len(goals) >= 2 else None

                    if not match_record:
                        cursor.execute("""
                            INSERT INTO matches (home_team, away_team, match_date, home_goals, away_goals)
                            VALUES (?, ?, ?, ?, ?)
                        """, (home_team, away_team, match_date, home_goals, away_goals))
                        total_saved += 1
                    else:
                        match_id = match_record[0]
                        cursor.execute("""
                            UPDATE matches 
                            SET home_goals = ?, away_goals = ?, match_date = ?
                            WHERE id = ?
                        """, (home_goals, away_goals, match_date, match_id))

        conn.commit()
        conn.close()
        browser.close()
        print(f"✅ Ingestão finalizada: {total_saved} jogos processados.")

if __name__ == "__main__":
    run_fifa_scraper()