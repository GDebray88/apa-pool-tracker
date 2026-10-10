import streamlit as st
import sqlite3
import hashlib

conn = sqlite3.connect("apa.pool.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game TEXT,
    opponent TEXT,
    your_skill INTEGER,
    opponent_skill INTEGER,
    your_score INTEGER,
    opponent_score INTEGER,
    result TEXT,
    lag_result TEXT,
    rackless INTEGER
)
""")
conn.commit()

try:
    cursor.execute("ALTER TABLE matches ADD COLUMN match_points TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE matches ADD COLUMN match_date TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass
try:
    cursor.execute("ALTER TABLE matches ADD COLUMN session TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT
)
""")
conn.commit()

try:
    cursor.execute("ALTER TABLE matches ADD COLUMN user_id INTEGER")
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE matches ADD COLUMN match_type TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE matches ADD COLUMN match_type TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS opponents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTERGER NOT NULL,
    name TEXT NOT NULL,
    UNIQUE(user_id, name)
)
""")
conn.commit()

eight_ball_races = {
    (2, 2): (2, 2),
    (2, 3): (2, 3),
    (2, 4): (2, 4),
    (2, 5): (2, 5),
    (2, 6): (2, 6),
    (2, 7): (2, 7),
    (3, 2): (3, 2),
    (3, 3): (2, 2),
    (3, 4): (2, 3),
    (3, 5): (2, 4),
    (3, 6): (2, 5),
    (3, 7): (2, 6),
    (4, 2): (4, 2),
    (4, 3): (3, 2),
    (4, 4): (3, 3),
    (4, 5): (3, 4),
    (4, 6): (3, 5),
    (4, 7): (2, 5),
    (5, 2): (5, 2),
    (5, 3): (4, 2),
    (5, 4): (4, 3),
    (5, 5): (4, 4),
    (5, 6): (4, 5),
    (5, 7): (3, 5),
    (6, 2): (6, 2),
    (6, 3): (5, 2),
    (6, 4): (5, 3),
    (6, 5): (5, 4),
    (6, 6): (5, 5),
    (6, 7): (4, 5),
    (7, 2): (7, 2),
    (7, 3): (6, 2),
    (7, 4): (5, 2),
    (7, 5): (5, 3),
    (7, 6): (5, 4),
    (7, 7): (5, 5),
}
nine_ball_points = {
    1: 14,
    2: 19,
    3: 25,
    4: 31,
    5: 38,
    6: 46,
    7: 55,
    8: 65,
    9: 75
}
if st.session_state.get("current_user_id") is not None:
    cursor.execute(
        "SELECT display_name FROM users WHERE id = ?",
        (st.session_state.current_user_id,)
    )
    user_row = cursor.fetchone()
    player_name = user_row[0] if user_row else ""
else:
    player_name = ""

st.title(f"🎱 {player_name}'s APA Pool Tracker" if player_name else "🎱 APA Pool Tracker")
st.write("Track my APA 8-ball and 9-ball matches")
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None

if "current_username" not in st.session_state:
    st.session_state.current_username = None
if st.session_state.current_user_id is None:
    st.subheader("Sign In")

    page_login_username = st.text_input(
        "Username",
        key="page_login_username"
    )

    page_login_password = st.text_input(
        "Password",
        type="password",
        key="page_login_password"
    )

    if st.button("Sign In", key="page_sign_in"):
        username_clean = page_login_username.strip()
        password_clean = page_login_password.strip()

        if not username_clean or not password_clean:
            st.warning("Username and Password are required.")
        else:
            password_hash = hashlib.sha256(
                password_clean.encode()
            ).hexdigest()

            cursor.execute(
                """
                SELECT id, username, display_name
                FROM users
                WHERE username = ?
                  AND password_hash = ?
                """,
                (username_clean, password_hash)
            )

            login_user = cursor.fetchone()

            if login_user:
                st.session_state.current_user_id = login_user[0]
                st.session_state.current_username = login_user[1]
                st.rerun()
            else:
                st.error("Incorrect username or password")
    if st.button("Create Account", key="show_create_account_button"):
        st.session_state.show_create_account = True
        st.rerun()

    if st.session_state.get("show_create_account", False):
        st.divider()
        st.subheader("Create Account")
        new_username = st.text_input(
            "Username",
            key="new_username"
        )
    
        new_display_name = st.text_input(
            "Display Name",
            key="new_display_name"
        )
    
        new_email = st.text_input(
            "Email (optional)",
            key="new_email"
        )
    
        new_password = st.text_input(
            "Password",
            type="password",
            key="new_password"
        )
    
        if st.button("Create Account"):
            username_clean = new_username.strip()
            display_name_clean = new_display_name.strip()
            email_clean = new_email.strip()
            password_clean = new_password.strip()
            if not username_clean or not display_name_clean or not password_clean:
                st.warning("Username and Display Name, and Password are required.")
            else:
                password_hash = hashlib.sha256(password_clean.encode()).hexdigest()
                
                try:
                    cursor.execute(
                        """
                        INSERT INTO users (username, display_name, email, password_hash)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            username_clean,
                            display_name_clean,
                            email_clean if email_clean else None,
                            password_hash
                        )
                    )
                    conn.commit()
    
                    new_user_id = cursor.lastrowid
    
                    st.success(
                        f"Account created! Your User ID is #{new_user_id}"
                    )
    
                except sqlite3.IntegrityError:
                    st.error("That username or email is already being used.")

    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "Enter Match",
    "History & Stats",
    "Opponent Lookup",
    "Account"
])
with tab1:
    game_type = st.selectbox(
        "What game are you playing?",
        ["8-ball", "9-ball"]
    )
    st.subheader("Match Information")
    match_type = st.selectbox(
        "Match Type",
        ["League", "Tournament", "Sudden Death"]
    )

    sudden_death_winner = None

    if game_type == "9-ball" and match_type == "Sudden Death":
        sudden_death_winner = st.selectbox(
            "Sudden Death Winner",
            ["Me", "Opponent"]
        )
    
        if st.session_state.get("current_user_id") is not None:
            cursor.execute(
                "SELECT DISTINCT opponent FROM matches WHERE user_id = ? ORDER BY opponent",
                (st.session_state.current_user_id,)
            )
            saved_opponents = [row[0] for tow in cursor.fetchall()]
        else:
            saved_opponents = []

    cursor.execute(
        "SELECT opponent, user_id FROM matches ORDER BY id DESC"
    )

    saved_opponents = []

    if st.session_state.get("current_user_id") is not None:
        cursor.execute(
            "SELECT DISTINCT opponent FROM matches WHERE user_id = ? ORDER BY opponent",
            (st.session_state.current_user_id,)
        )
        saved_opponents = [row[0] for row in cursor.fetchall()]

    opponent_choice = st.selectbox(
        "Opponent",
        ["Add New Opponent"] + saved_opponents
    )

    if opponent_choice == "Add New Opponent":
        opponent_name = st.text_input("Opponent's name")
    else:
        opponent_name = opponent_choice

    match_date = st.date_input("Match date")
    session = st.selectbox(
        "Session",
        ["Spring 2026", "Summer 2026", "Fall 2026", "Spring 2027", "Summer 2027", "Fall 2027", "Spring 2028", "Summer 2028", "Fall 2028"]
        )
    if game_type == "8-ball":
        min_skill = 2
        max_skill = 7
    else:
        min_skill = 1
        max_skill = 9
    your_skill_level = st.number_input(
        "Your skill level",
        min_value=min_skill,
        max_value=max_skill,
        value=4
    )
    opponent_skill_level = st.number_input(
        "Opponents skill level",
        min_value=min_skill,
        max_value=max_skill,
        value=4
    )
    if game_type == "8-ball":
        your_race, opponent_race = eight_ball_races[
            (your_skill_level, opponent_skill_level)
        ]

        st.write(
            f"Race: {player_name} needs {your_race} games | "
            f"Opponent needs {opponent_race} games"
        )

    else:
        your_race = nine_ball_points[your_skill_level]
        opponent_race = nine_ball_points[opponent_skill_level]

        st.write(
            f"Race: {player_name} needs {your_race} points | "
            f"Opponent needs {opponent_race} points"
        )
        st.subheader("Match Score")

    if game_type == "8-ball":
        your_score_label = "Games you won"
        opponent_score_label = "Games opponent won"
    else:
        your_score_label = "Points you scored"
        opponent_score_label = "Points opponent scored"

    if game_type == "8-ball":
        your_max_score = your_race
        opponent_max_score = opponent_race
    else:
        your_max_score = your_race
        opponent_max_score = opponent_race

    your_game = st.number_input(
        your_score_label,
        min_value=0,
        max_value=your_max_score,
        value=0
    )

    opponent_games = st.number_input(
        opponent_score_label,
        min_value=0,
        max_value=opponent_max_score,
        value=0
    )

    lag_result = st.selectbox(
        "Lag result",
        ["Won", "Lost"]
    )

    if game_type == "8-ball":
        rackless = st.checkbox("Rackless match")
    else:
        rackless = False

    if st.button("Show Result"):
        if st.session_state.current_user_id is None:
            st.warning("Please sign in before saving a match.")
            st.stop()

        if game_type == "8-ball":
            if your_game >= your_race:
                match_result = "W"
                st.success(f"🎱 {player_name} wins {your_game} - {opponent_games}!")
                if opponent_games == 0:
                    eight_ball_match_points = 3
                else:
                    eight_ball_match_points = 2
            elif opponent_games >= opponent_race:
                match_result = "L"
                st.error(f"{player_name} loses {your_game} - {opponent_games}.")
                if your_game == 0:
                    eight_ball_match_points = 0
                else:
                    eight_ball_match_points = 1
            else:
                if match_type == "Sudden Death":
                    if your_game > opponent_games:
                        match_result = "W"
                        st.success(f"🎱{player_name} wins {your_game} - {opponent_games}")
                        if opponent_games == 0:
                            eight_ball_match_points = 3
                        else:
                            eight_ball_match_points = 2
                    elif opponent_games > your_game:
                        match_result = "L"
                        st.error(f"{player_name} loses {your_game} - {opponent_games}")
                        if your_game == 0:
                            eight_ball_match_points = 0
                        else:
                            eight_ball_match_points = 1
                    else:
                        st.warning("A Sudden Death match cannot end in a tie.")
                        st.stop()
                else:
                    st.warning("This match is not finished yet.")
                    st.stop()
        else:
            if your_game >= your_race:
                match_result = "W"
                st.success(f"🎱 {player_name} wins {your_game} - {opponent_games}!")
            elif opponent_games >= opponent_race:
                match_result = "L"
                st.error(f"{player_name} loses {your_game} - {opponent_games}.")
            else:
                if match_type == "Sudden Death":
                    if sudden_death_winner == "Me":
                        match_result = "W"
                        st.success(f"🎱 {player_name} wins {your_game} - {opponent_games}")
                    else:
                        match_result = "L"
                        st.error(f"{player_name} loses {your_game} - {opponent_games}.")
                else:
                    st.warning("This match is not finished yet.")
                    st.stop()
        if game_type == "9-ball":
            if match_result == "W":
                loser_skill = opponent_skill_level
                loser_points = opponent_games
            else:
                loser_skill = your_skill_level
                loser_points = your_game

            nine_ball_result = None
            if loser_skill == 1:
                if loser_points <= 2:
                    nine_ball_result = "20-0"
                elif loser_points == 3:
                    nine_ball_result = "19-1"
                elif loser_points == 4:
                    nine_ball_result = "18-2"
                elif loser_points <= 6:
                    nine_ball_result = "17-3"
                elif loser_points == 7:
                    nine_ball_result = "16-4"
                elif loser_points == 8:
                    nine_ball_result = "15-5"
                elif loser_points <= 10:
                    nine_ball_result = "14-6"
                elif loser_points == 11:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 2:
                if loser_points <= 3:
                    nine_ball_result = "20-0"
                elif loser_points <= 5:
                    nine_ball_result = "19-1"
                elif loser_points <= 7:
                    nine_ball_result = "18-2"
                elif loser_points == 8:
                    nine_ball_result = "17-3"
                elif loser_points <= 10:
                    nine_ball_result = "16-4"
                elif loser_points <= 12:
                    nine_ball_result = "15-5"
                elif loser_points <= 14:
                    nine_ball_result = "14-6"
                elif loser_points <= 16:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 3:
                if loser_points <= 4:
                    nine_ball_result = "20-0"
                elif loser_points <= 6:
                    nine_ball_result = "19-1"
                elif loser_points <= 9:
                    nine_ball_result = "18-2"
                elif loser_points <= 11:
                    nine_ball_result = "17-3"
                elif loser_points <= 14:
                    nine_ball_result = "16-4"
                elif loser_points <= 16:
                    nine_ball_result = "15-5"
                elif loser_points <= 19:
                    nine_ball_result = "14-6"
                elif loser_points <= 21:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 4:
                if loser_points <= 5:
                    nine_ball_result = "20-0"
                elif loser_points <= 8:
                    nine_ball_result = "19-1"
                elif loser_points <= 11:
                    nine_ball_result = "18-2"
                elif loser_points <= 14:
                    nine_ball_result = "17-3"
                elif loser_points <= 18:
                    nine_ball_result = "16-4"
                elif loser_points <= 21:
                    nine_ball_result = "15-5"
                elif loser_points <= 24:
                    nine_ball_result = "14-6"
                elif loser_points <= 27:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 5:
                if loser_points <= 6:
                    nine_ball_result = "20-0"
                elif loser_points <= 10:
                    nine_ball_result = "19-1"
                elif loser_points <= 14:
                    nine_ball_result = "18-2"
                elif loser_points <= 18:
                    nine_ball_result = "17-3"
                elif loser_points <= 22:
                    nine_ball_result = "16-4"
                elif loser_points <= 26:
                    nine_ball_result = "15-5"
                elif loser_points <= 29:
                    nine_ball_result = "14-6"
                elif loser_points <= 33:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 6:
                if loser_points <= 8:
                    nine_ball_result = "20-0"
                elif loser_points <= 12:
                    nine_ball_result = "19-1"
                elif loser_points <= 17:
                    nine_ball_result = "18-2"
                elif loser_points <= 22:
                    nine_ball_result = "17-3"
                elif loser_points <= 27:
                    nine_ball_result = "16-4"
                elif loser_points <= 31:
                    nine_ball_result = "15-5"
                elif loser_points <= 36:
                    nine_ball_result = "14-6"
                elif loser_points <= 40:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 7:
                if loser_points <= 10:
                    nine_ball_result = "20-0"
                elif loser_points <= 15:
                    nine_ball_result = "19-1"
                elif loser_points <= 21:
                    nine_ball_result = "18-2"
                elif loser_points <= 26:
                    nine_ball_result = "17-3"
                elif loser_points <= 32:
                    nine_ball_result = "16-4"
                elif loser_points <= 37:
                    nine_ball_result = "15-5"
                elif loser_points <= 43:
                    nine_ball_result = "14-6"
                elif loser_points <= 49:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 8:
                if loser_points <= 13:
                    nine_ball_result = "20-0"
                elif loser_points <= 19:
                    nine_ball_result = "19-1"
                elif loser_points <= 26:
                    nine_ball_result = "18-2"
                elif loser_points <= 32:
                    nine_ball_result = "17-3"
                elif loser_points <= 39:
                    nine_ball_result = "16-4"
                elif loser_points <= 45:
                    nine_ball_result = "15-5"
                elif loser_points <= 52:
                    nine_ball_result = "14-6"
                elif loser_points <= 58:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"

            elif loser_skill == 9:
                if loser_points <= 17:
                    nine_ball_result = "20-0"
                elif loser_points <= 24:
                    nine_ball_result = "19-1"
                elif loser_points <= 31:
                    nine_ball_result = "18-2"
                elif loser_points <= 38:
                    nine_ball_result = "17-3"
                elif loser_points <= 46:
                    nine_ball_result = "16-4"
                elif loser_points <= 53:
                    nine_ball_result = "15-5"
                elif loser_points <= 60:
                    nine_ball_result = "14-6"
                elif loser_points <= 67:
                    nine_ball_result = "13-7"
                else:
                    nine_ball_result = "12-8"
        st.subheader("Match Summary")
        st.write(f"Game: {game_type}")
        st.write(f"Date: {match_date.strftime('%m/%d/%Y')}")
        st.write(f"Session: {session}")
        st.write(f"Opponent: {opponent_name}")
        st.write(f"Your skill level: {your_skill_level}")
        st.write(f"Opponent skill level: {opponent_skill_level}")
        if game_type == "8-ball":
            st.write(f"Final game score: {your_game} - {opponent_games}")
            st.write(f"Match Points: {eight_ball_match_points}")
        else:
            st.write(f"Final points: {your_game} - {opponent_games}")
            st.write(f"Match Points: {nine_ball_result}")
        st.write(f"Lag: {lag_result}")

        if game_type == "8-ball":
            if rackless:
                st.write("Rackless: Yes")
            else:
                st.write("Rackless: No")
        match = {
            "game": game_type,
            "opponent": opponent_name,
            "your_skill": your_skill_level,
            "opponent_skill": opponent_skill_level,
            "your_score": your_game,
            "opponent_score": opponent_games,
            "result": match_result,
            "lag_result": lag_result,
            "rackless": rackless
        }

        if opponent_name.strip():
            cursor.execute(
                """
                INSERT OR IGNORE INTO opponents (user_id, name)
                VALUES (?, ?)
                """,
                (
                    st.session_state.current_user_id,
                    opponent_name.strip()
                )
            )
            conn.commit()

        cursor.execute("""
    INSERT INTO matches (
        game,
        opponent,
        your_skill,
        opponent_skill,
        your_score,
        opponent_score,
        result,
        lag_result,
        rackless,
        match_points,
        match_date,
        session,
        user_id,
        match_type
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        game_type,
        opponent_name,
        your_skill_level,
        opponent_skill_level,
        your_game,
        opponent_games,
        match["result"],
        lag_result,
        1 if rackless else 0,
        str(eight_ball_match_points) if game_type == "8-ball" else nine_ball_result,
        str(match_date),
        session,
        st.session_state.current_user_id,
        match_type
    ))

        conn.commit()

with tab2:
    cursor.execute("""
    SELECT game, opponent, your_skill, opponent_skill,
        your_score, opponent_score, result,
        lag_result, rackless, match_points, match_date, session, match_type
    FROM matches
    WHERE user_id = ?
    ORDER BY id DESC
    """, (st.session_state.current_user_id,))

    saved_matches = cursor.fetchall()
    if saved_matches:
        st.subheader("Match History")

        for saved_match in saved_matches:
            if saved_match[0] == "8-ball":
                score_type = "Games"
            else:
                score_type = "Points"

            if saved_match[10]:
                year, month, day = saved_match[10].split("-")
                display_date = f"{month}/{day}/{year}"
            else:
                display_date = "No Date"
                
            st.write(
                f"{display_date} | "
                f"{saved_match[11]} | "
                f"{saved_match[12]} | "
                f"{saved_match[1]} | "
                f"SL {saved_match[2]} vs {saved_match[3]} | "
                f"{score_type}: {saved_match[4]} - {saved_match[5]} | "
                f"{saved_match[6]} | "
                f"Match Points: {saved_match[9]} | "
                f"Lag: {saved_match[7]}"
                + (
                    f" | Rackless: {'Yes' if saved_match[8] else 'No'}"
                    if saved_match[0] == "8-ball"
                    else ""
            )
    )

    eight_ball_matches = [match for match in saved_matches if match[0] == "8-ball"]
    nine_ball_matches = [match for match in saved_matches if match[0] == "9-ball"]

    tournament_matches = [
    match for match in saved_matches
    if match[12] == "Tournament"
    ]

    tournament_eight_ball = [
        match for match in tournament_matches
        if match[0] == "8-ball"
    ]

    tournament_nine_ball = [
        match for match in tournament_matches
        if match[0] == "9-ball"
    ]

    tournament_wins = sum(
        1 for match in tournament_matches if match[6] == "W"
    )

    tournament_losses = sum(
        1 for match in tournament_matches if match[6] == "L"
    )

    tournament_eight_wins = sum(
        1 for match in tournament_eight_ball if match[6] == "W"
    )
    tournament_eight_losses = sum(
        1 for match in tournament_eight_ball if match[6] == "L"
    )

    tournament_nine_wins = sum(
        1 for match in tournament_nine_ball if match[6] == "W"
    )
    tournament_nine_losses = sum(
        1 for match in tournament_nine_ball if match[6] == "L"
    )

    # 8-ball stats
    eight_wins = sum(1 for match in eight_ball_matches if match[6] == "W")
    eight_losses = sum(1 for match in eight_ball_matches if match[6] == "L")
    eight_total = eight_wins + eight_losses

    if eight_total > 0:
        eight_win_percentage = (eight_wins / eight_total) * 100
    else:
        eight_win_percentage = 0

    eight_match_points = [
        int(match[9])
        for match in eight_ball_matches
        if match[9] is not None
    ]

    eight_total_match_points = sum(eight_match_points)

    if eight_match_points:
        eight_average_match_points = eight_total_match_points / len(eight_match_points)
    else:
        eight_average_match_points = 0

    eight_rackless = sum(1 for match in eight_ball_matches if match[8] == 1)
    eight_lag_wins = sum(1 for match in eight_ball_matches if match[7] == "Won")
    eight_lag_losses = sum(1 for match in eight_ball_matches if match[7] == "Lost")

    st.subheader("8-ball Stats")
    st.write(f"Record: {eight_wins} - {eight_losses}")
    st.write(f"Win percentage: {eight_win_percentage:.1f}%")
    st.write(f"Total Match Points: {eight_total_match_points}")
    st.write(f"Average Match Points: {eight_average_match_points:.2f}")
    st.write(f"Rackless matches: {eight_rackless}")
    st.write(f"Lag record: {eight_lag_wins} - {eight_lag_losses}")

    # 9-ball stats
    nine_wins = sum(1 for match in nine_ball_matches if match[6] == "W")
    nine_losses = sum(1 for match in nine_ball_matches if match[6] == "L")
    nine_total = nine_wins + nine_losses

    if nine_total > 0:
        nine_win_percentage = (nine_wins / nine_total) * 100
    else:
        nine_win_percentage = 0

    nine_points_for = 0
    nine_points_against = 0

    for match in nine_ball_matches:
        if match[9] is not None and "-" in str(match[9]):
            first_points, second_points = map(int, str(match[9]).split("-"))

            if match[6] == "W":
                nine_points_for += first_points
                nine_points_against += second_points
            else:
                nine_points_for += second_points
                nine_points_against += first_points

    nine_lag_wins = sum(1 for match in nine_ball_matches if match[7] == "Won")
    nine_lag_losses = sum(1 for match in nine_ball_matches if match[7] == "Lost")

    st.subheader("9-ball Stats")
    st.write(f"Record: {nine_wins} - {nine_losses}")
    st.write(f"Win percentage: {nine_win_percentage:.1f}%")
    st.write(f"Total Match Points: {nine_points_for} - {nine_points_against}")
    st.write(f"Lag record: {nine_lag_wins} - {nine_lag_losses}")

    st.divider()
    st.subheader("Tournament Stats")

    st.write(
        f"Overall Record: {tournament_wins} - {tournament_losses}"
    )

    st.write(
        f"8-ball Record: {tournament_eight_wins} - {tournament_eight_losses}"
    )

    st.write(
        f"9-ball Record: {tournament_nine_wins} - {tournament_nine_losses}"
    )
    st.subheader("Test Data")    
    confirm_clear = st.checkbox("Yes, delete all saved match data")
    if st.button("Clear Test Data"):
        if confirm_clear:
            cursor.execute("DELETE FROM matches")
            conn.commit()
            st.success("Test data cleared.")
        else:
            st.warning("Check the confirmation box first.")

with tab3:
    st.subheader("Opponent Lookup")

    if st.session_state.get("current_user_id") is None:
        st.info("Please sign in to view opponent records.")
    else:
        cursor.execute(
            """
            SELECT DISTINCT opponent
            FROM matches
            WHERE user_id = ?
              AND opponent IS NOT NULL
              AND TRIM(opponent) != ''
            ORDER BY opponent COLLATE NOCASE
            """,
            (st.session_state.current_user_id,)
        )
        lookup_opponents = [row[0] for row in cursor.fetchall()]

        if lookup_opponents:
            lookup_opponent = st.selectbox(
                "Choose an opponent",
                lookup_opponents,
                key="opponent_lookup"
            )
            cursor.execute(
                """
                SELECT game, result
                FROM matches
                WHERE user_id = ?
                  AND opponent = ?
                ORDER BY id DESC
                """,
                (st.session_state.current_user_id, lookup_opponent)
            )

            opponent_matches = cursor.fetchall()
            total_matches = len(opponent_matches)
            opponent_wins = sum(1 for match in opponent_matches if match[1] == "W")
            opponent_losses = sum(1 for match in opponent_matches if match[1] == "L")
            eight_ball_matches = [match for match in opponent_matches if match[0] == "8-ball"]
            nine_ball_matches = [match for match in opponent_matches if match [0] == "9-ball"]

            eight_ball_wins = sum(1 for match in eight_ball_matches if match[1] == "W")
            eight_ball_losses = sum(1 for match in eight_ball_matches if match[1] == "L")

            nine_ball_wins = sum(1 for match in nine_ball_matches if match[1] == "W")
            nine_ball_losses = sum(1 for match in nine_ball_matches if match[1] =="L")

            st.write(f"Total Matches: {total_matches}")
            st.write(f"Record: {opponent_wins} - {opponent_losses}")
            st.write(f"8-ball Record: {eight_ball_wins} - {eight_ball_losses}")
            st.write(f"9-ball Record: {nine_ball_wins} - {nine_ball_losses}")
        else:
            st.info("No saved opponents yet.")
            
with tab4:
    st.subheader("Account")

    if st.session_state.current_user_id is not None:
        st.write(
            f"Current User ID: #{st.session_state.current_user_id}"
        )
        if st.button("Sign Out"):
            st.session_state.current_user_id = None
            st.session_state.current_username = None
            st.rerun()
    st.divider()