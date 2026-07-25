from playwright.sync_api import sync_playwright
import database as db

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) 
    page = browser.new_page()

    print("🌐 Acessando o site da FIFA...")
    page.goto("https://www.fifa.com/pt/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures?country=BR&wtw-filter=ALL")

    page.wait_for_selector(".ff-pb-24")

    page.evaluate("window.scrollBy(0, 800)")
    
    page.wait_for_timeout(2000)

    match_cards = page.locator(".ff-pb-24").all()

    print(f"🔎 Encontrados {len(match_cards)} cards de jogos na página.\n")

    # print(match_cards)

    conn = db.connect()
    cursor = conn.cursor()

    for i in range(len(match_cards)):
        title_locator = match_cards[i].locator(".matches-container_title__ATLsl")
        if title_locator.count() == 0:
            continue    

        match_date = title_locator.inner_text().strip()
        match_rows = match_cards[i].locator(".match-row_matchRowContainer__NoCRI")
        count = match_rows.count()
        for j in range(count):
            row = match_rows.nth(j)
            
            teams = row.locator(".d-none.d-md-block").all_inner_texts()
            goals = row.locator(".match-row_score__wfcQP").all_inner_texts()
            
            if len(teams) >= 2 and len(goals) >= 2:
                home_team = teams[0].strip()
                away_team = teams[1].strip()

                home_goals = int(goals[0])
                away_goals = int(goals[1])

                cursor.execute("""
                    INSERT INTO matches (home_team, away_team, match_date, home_goals, away_goals)
                    VALUES (?, ?, ?, ?, ?)
                """, (home_team, away_team, match_date, home_goals, away_goals))


                print(f"🏟️ Jogo {j + 1} ({match_date}): {home_team} vs {away_team} - {home_goals} x {away_goals}") 
            
            elif len(teams) >= 2:
                home_team = teams[0].strip()
                away_team = teams[1].strip()

                cursor.execute("""
                               SELECT id FROM matches 
                               WHERE home_team = ? AND away_team = ? AND match_date = ? 
                               """, (home_team, away_team, match_date))
                match_record = cursor.fetchone()

                print(f"🏟️ Jogo {j + 1} ({match_date}): {home_team} vs {away_team} - Placar ainda não disponível")
                cursor.execute("""
                    INSERT INTO matches (home_team, away_team, match_date, home_goals, away_goals)
                    VALUES (?, ?, ?, ?, ?)
                """, (home_team, away_team, match_date, None, None))


    # for i, card in enumerate(match_cards, start=1):
    #     txt = card.inner_text().strip()
    #     if txt:
    #         print(f"--- CARD {i} ---")
    #         print(txt)
    #         print("----------------\n")

    conn.commit()
    conn.close()
    browser.close()