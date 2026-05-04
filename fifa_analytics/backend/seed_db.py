"""
FIFA World Cup Analytics Platform
Seed Script — populates SQLite with historical data
Deliverable 1: Cleaned FIFA Dataset
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fifa.db")

# ── TOURNAMENTS ──────────────────────────────────────────────────────────────
TOURNAMENTS = [
    (1930, "Uruguay",       "Uruguay",       13, 18,  70, "First ever World Cup"),
    (1934, "Italy",         "Italy",         16, 17,  70, "First World Cup in Europe"),
    (1938, "France",        "Italy",         15, 18,  84, "Italy retained title"),
    (1950, "Brazil",        "Uruguay",       13, 22,  88, "Highest ever attendance"),
    (1954, "Switzerland",   "West Germany",  16, 26, 140, "Most goals per match ever"),
    (1958, "Sweden",        "Brazil",        16, 35, 126, "Pelé's debut World Cup"),
    (1962, "Chile",         "Brazil",        16, 32,  89, "Brazil retained title"),
    (1966, "England",       "England",       16, 32,  89, "England's only title"),
    (1970, "Mexico",        "Brazil",        16, 32,  95, "First colour TV broadcast"),
    (1974, "West Germany",  "West Germany",  16, 38,  97, "Total Football era"),
    (1978, "Argentina",     "Argentina",     16, 38, 102, "Argentina's first title"),
    (1982, "Spain",         "Italy",         24, 52, 146, "Expanded to 24 teams"),
    (1986, "Mexico",        "Argentina",     24, 52, 132, "Hand of God tournament"),
    (1990, "Italy",         "West Germany",  24, 52, 115, "Lowest scoring tournament"),
    (1994, "USA",           "Brazil",        24, 52, 141, "Record 3.5M attendance"),
    (1998, "France",        "France",        32, 64, 171, "Expanded to 32 teams"),
    (2002, "South Korea/Japan","Brazil",     32, 64, 161, "First World Cup in Asia"),
    (2006, "Germany",       "Italy",         32, 64, 147, "Zidane headbutt final"),
    (2010, "South Africa",  "Spain",         32, 64, 145, "First in Africa"),
    (2014, "Brazil",        "Germany",       32, 64, 171, "Mineirazo 7-1"),
    (2018, "Russia",        "France",        32, 64, 169, "Mbappé teenage sensation"),
    (2022, "Qatar",         "Argentina",     32, 64, 172, "Greatest final ever"),
]

# ── MATCHES ──────────────────────────────────────────────────────────────────
MATCHES = [
    # 2022
    (2022,"Final","Argentina","France",3,3,"4-2 pens","Lusail Stadium, Qatar",88966,"Argentina"),
    (2022,"Semi-Final","Argentina","Croatia",3,0,None,"Lusail Stadium, Qatar",88966,"Argentina"),
    (2022,"Semi-Final","France","Morocco",2,0,None,"Al Bayt Stadium, Qatar",68294,"France"),
    (2022,"Quarter-Final","Morocco","Portugal",1,0,None,"Al Thumama Stadium, Qatar",44137,"Morocco"),
    (2022,"Quarter-Final","France","England",2,1,None,"Al Bayt Stadium, Qatar",68295,"France"),
    (2022,"Quarter-Final","Argentina","Netherlands",2,2,"4-3 pens","Lusail Stadium, Qatar",88235,"Argentina"),
    (2022,"Quarter-Final","Croatia","Brazil",1,1,"4-2 pens","Education City, Qatar",44175,"Croatia"),
    (2022,"Round of 16","France","Poland",3,1,None,"Al Thumama, Qatar",41721,"France"),
    (2022,"Round of 16","Argentina","Australia",2,1,None,"Ahmad bin Ali, Qatar",45416,"Argentina"),
    (2022,"Round of 16","Morocco","Spain",0,0,"3-0 pens","Education City, Qatar",45116,"Morocco"),
    (2022,"Round of 16","Croatia","Japan",1,1,"3-1 pens","Al Janoub, Qatar",44375,"Croatia"),
    (2022,"Group Stage","Argentina","Saudi Arabia",1,2,None,"Lusail, Qatar",88012,"Saudi Arabia"),
    (2022,"Group Stage","Germany","Japan",1,2,None,"Khalifa International",42608,"Japan"),
    (2022,"Group Stage","Spain","Japan",1,2,None,"Khalifa International",42668,"Japan"),
    (2022,"Group Stage","Brazil","Serbia",2,0,None,"Lusail, Qatar",88103,"Brazil"),
    (2022,"Group Stage","Portugal","Ghana",3,2,None,"Stadium 974, Qatar",41698,"Portugal"),
    (2022,"Group Stage","England","Senegal",3,0,None,"Al Bayt Stadium",67713,"England"),
    # 2018
    (2018,"Final","France","Croatia",4,2,None,"Luzhniki, Moscow",78011,"France"),
    (2018,"Semi-Final","France","Belgium",1,0,None,"Saint Petersburg",64286,"France"),
    (2018,"Semi-Final","Croatia","England",2,1,"AET","Luzhniki, Moscow",78011,"Croatia"),
    (2018,"Quarter-Final","France","Uruguay",2,0,None,"Nizhny Novgorod",43319,"France"),
    (2018,"Quarter-Final","Belgium","Brazil",2,1,None,"Kazan Arena",42844,"Belgium"),
    (2018,"Quarter-Final","Russia","Croatia",2,2,"3-4 pens","Fisht, Sochi",43699,"Croatia"),
    (2018,"Quarter-Final","Sweden","England",0,2,None,"Samara Arena",41970,"England"),
    (2018,"Round of 16","Spain","Russia",1,1,"3-4 pens","Luzhniki, Moscow",78011,"Russia"),
    (2018,"Round of 16","Argentina","France",3,4,None,"Kazan Arena",42873,"France"),
    (2018,"Round of 16","Uruguay","Portugal",2,1,None,"Fisht, Sochi",43387,"Uruguay"),
    (2018,"Round of 16","Brazil","Mexico",2,0,None,"Samara Arena",41427,"Brazil"),
    (2018,"Group Stage","Germany","South Korea",0,2,None,"Kazan Arena",42873,"South Korea"),
    (2018,"Group Stage","Germany","Mexico",0,1,None,"Luzhniki, Moscow",80680,"Mexico"),
    (2018,"Group Stage","Russia","Saudi Arabia",5,0,None,"Luzhniki, Moscow",78011,"Russia"),
    # 2014
    (2014,"Final","Germany","Argentina",1,0,"AET","Maracanã, Rio",74738,"Germany"),
    (2014,"Semi-Final","Brazil","Germany",1,7,None,"Mineirão, BH",58141,"Germany"),
    (2014,"Semi-Final","Argentina","Netherlands",0,0,"4-2 pens","Arena de SP",63267,"Argentina"),
    (2014,"Quarter-Final","Germany","France",1,0,None,"Maracanã, Rio",74240,"Germany"),
    (2014,"Quarter-Final","Brazil","Colombia",2,1,None,"Castelão, Fortaleza",60342,"Brazil"),
    (2014,"Quarter-Final","Argentina","Belgium",1,0,None,"Brasília National",68351,"Argentina"),
    (2014,"Quarter-Final","Netherlands","Costa Rica",0,0,"4-3 pens","Arena Fonte Nova",51179,"Netherlands"),
    (2014,"Round of 16","Germany","Algeria",2,1,"AET","Beira-Rio, Porto Alegre",43063,"Germany"),
    (2014,"Round of 16","Colombia","Uruguay",2,0,None,"Maracanã, Rio",74101,"Colombia"),
    (2014,"Round of 16","Brazil","Chile",1,1,"3-2 pens","Estádio Mineirão",57714,"Brazil"),
    (2014,"Group Stage","Germany","Ghana",2,2,None,"Fortaleza, Brazil",60342,"Draw"),
    (2014,"Group Stage","Brazil","Croatia",3,1,None,"Arena de São Paulo",62103,"Brazil"),
    (2014,"Group Stage","Colombia","Japan",4,1,None,"Arena Pantanal",40340,"Colombia"),
    # 2010
    (2010,"Final","Spain","Netherlands",1,0,"AET","Soccer City, Joburg",84490,"Spain"),
    (2010,"Semi-Final","Spain","Germany",1,0,None,"Moses Mabhida, Durban",60960,"Spain"),
    (2010,"Semi-Final","Netherlands","Uruguay",3,2,None,"Green Point, Cape Town",64100,"Netherlands"),
    (2010,"Quarter-Final","Ghana","Uruguay",1,1,"2-4 pens","Soccer City, Joburg",84017,"Uruguay"),
    (2010,"Quarter-Final","Germany","Argentina",4,0,None,"Green Point, Cape Town",64100,"Germany"),
    (2010,"Quarter-Final","Spain","Paraguay",1,0,None,"Ellis Park, Joburg",55359,"Spain"),
    (2010,"Quarter-Final","Netherlands","Brazil",2,1,None,"Nelson Mandela Bay",46696,"Netherlands"),
    (2010,"Round of 16","Spain","Portugal",1,0,None,"Green Point, Cape Town",63000,"Spain"),
    (2010,"Round of 16","Germany","England",4,1,None,"Free State, Bloemfontein",40510,"Germany"),
    (2010,"Round of 16","Argentina","Mexico",3,1,None,"Soccer City, Joburg",84377,"Argentina"),
    (2010,"Group Stage","England","USA",1,1,None,"Royal Bafokeng",38000,"Draw"),
    (2010,"Group Stage","South Africa","Mexico",1,1,None,"Soccer City, Joburg",84490,"Draw"),
    # 2006
    (2006,"Final","Italy","France",1,1,"5-3 pens","Olympiastadion, Berlin",69000,"Italy"),
    (2006,"Semi-Final","Germany","Italy",0,2,"AET","Westfalenstadion",65000,"Italy"),
    (2006,"Semi-Final","France","Portugal",1,0,None,"Allianz Arena, Munich",66000,"France"),
    (2006,"Quarter-Final","England","Portugal",0,0,"1-3 pens","Gelsenkirchen",52000,"Portugal"),
    (2006,"Quarter-Final","Germany","Argentina",1,1,"4-2 pens","Olympiastadion, Berlin",72000,"Germany"),
    (2006,"Quarter-Final","Italy","Ukraine",3,0,None,"Fritz Walter, Kaiserslautern",46000,"Italy"),
    (2006,"Quarter-Final","France","Brazil",1,0,None,"Commerzbank, Frankfurt",48000,"France"),
    (2006,"Round of 16","Germany","Sweden",2,0,None,"Allianz Arena, Munich",66000,"Germany"),
    (2006,"Round of 16","Italy","Australia",1,0,None,"Fritz Walter, Kaiserslautern",46000,"Italy"),
    (2006,"Group Stage","Germany","Costa Rica",4,2,None,"Allianz Arena, Munich",66000,"Germany"),
    (2006,"Group Stage","Ecuador","Poland",2,0,None,"Stadium Gelsenkirchen",52000,"Ecuador"),
]

# ── PLAYERS ──────────────────────────────────────────────────────────────────
PLAYERS = [
    # (name, country, flag, goals, tournaments, matches, position, era)
    ("Miroslav Klose",     "Germany",    "🇩🇪", 16, 4, 24, "Forward",  "2002-2014"),
    ("Ronaldo Nazário",    "Brazil",     "🇧🇷", 15, 4, 19, "Forward",  "1994-2006"),
    ("Gerd Müller",        "West Germany","🇩🇪", 14, 2, 13, "Forward", "1970-1974"),
    ("Just Fontaine",      "France",     "🇫🇷", 13, 1,  6, "Forward",  "1958"),
    ("Pelé",               "Brazil",     "🇧🇷", 12, 4, 14, "Forward",  "1958-1970"),
    ("Sandor Kocsis",      "Hungary",    "🇭🇺", 11, 1,  5, "Forward",  "1954"),
    ("Jürgen Klinsmann",   "Germany",    "🇩🇪", 11, 3, 17, "Forward",  "1990-1998"),
    ("Helmut Rahn",        "West Germany","🇩🇪", 10, 2,  9, "Forward", "1954-1958"),
    ("Gary Lineker",       "England",    "🏴󠁧󠁢󠁥󠁮󠁧󠁿", 10, 2, 12, "Forward", "1986-1990"),
    ("Teofilo Cubillas",   "Peru",       "🇵🇪", 10, 2, 13, "Forward",  "1970-1978"),
    ("Grzegorz Lato",      "Poland",     "🇵🇱", 10, 3, 20, "Forward",  "1974-1982"),
    ("Gabriel Batistuta",  "Argentina",  "🇦🇷", 10, 3, 12, "Forward",  "1994-2002"),
    ("Thomas Müller",      "Germany",    "🇩🇪", 10, 3, 20, "Forward",  "2010-2022"),
    ("Ronaldo (CR7)",      "Portugal",   "🇵🇹",  8, 5, 22, "Forward",  "2006-2022"),
    ("Lionel Messi",       "Argentina",  "🇦🇷", 13, 5, 26, "Forward",  "2006-2022"),
    ("Kylian Mbappé",      "France",     "🇫🇷", 12, 2, 14, "Forward",  "2018-2022"),
    ("Eusébio",            "Portugal",   "🇵🇹",  9, 1,  6, "Forward",  "1966"),
    ("Ademir",             "Brazil",     "🇧🇷",  9, 1,  6, "Forward",  "1950"),
    ("Leônidas",           "Brazil",     "🇧🇷",  8, 2,  8, "Forward",  "1934-1938"),
    ("Roberto Baggio",     "Italy",      "🇮🇹",  9, 3, 16, "Forward",  "1990-1998"),
    ("Karl-Heinz Rummenigge","West Germany","🇩🇪", 9, 2, 19, "Forward","1978-1986"),
    ("Uwe Seeler",         "West Germany","🇩🇪",  9, 4, 21, "Forward", "1958-1970"),
    ("Laszlo Kiss",        "Hungary",    "🇭🇺",  3, 1,  2, "Forward",  "1982"),
    ("Oleg Salenko",       "Russia",     "🇷🇺",  6, 1,  5, "Forward",  "1994"),
    ("Harry Kane",         "England",    "🏴󠁧󠁢󠁥󠁮󠁧󠁿",  8, 2, 14, "Forward", "2018-2022"),
    ("Antoine Griezmann",  "France",     "🇫🇷",  7, 3, 18, "Forward",  "2014-2022"),
    ("Neymar Jr",          "Brazil",     "🇧🇷",  8, 3, 17, "Forward",  "2014-2022"),
    ("Luka Modric",        "Croatia",    "🇭🇷",  3, 4, 23, "Midfielder","2006-2022"),
    ("Franz Beckenbauer",  "West Germany","🇩🇪",  5, 4, 18, "Defender", "1966-1974"),
    ("Cafu",               "Brazil",     "🇧🇷",  2, 4, 20, "Defender", "1994-2006"),
]

# ── TEAM STATS ────────────────────────────────────────────────────────────────
TEAMS = [
    ("Brazil",       "🇧🇷", 5, 22, 114, 76, 18, 20, 229, 105),
    ("Germany",      "🇩🇪", 4, 20, 109, 67, 21, 21, 226, 125),
    ("Italy",        "🇮🇹", 4, 18,  83, 45, 21, 17, 128,  77),
    ("Argentina",    "🇦🇷", 3, 18,  88, 45, 22, 21, 145,  97),
    ("France",       "🇫🇷", 2, 16,  72, 39, 16, 17, 120,  76),
    ("England",      "🏴󠁧󠁢󠁥󠁮󠁧󠁿", 1, 16,  69, 29, 24, 16,  80,  57),
    ("Spain",        "🇪🇸", 1, 16,  63, 33, 16, 14, 100,  60),
    ("Uruguay",      "🇺🇾", 2, 14,  56, 27, 14, 15,  90,  62),
    ("Netherlands",  "🇳🇱", 0, 12,  52, 25, 14, 13,  87,  62),
    ("Croatia",      "🇭🇷", 0,  8,  34, 17, 10,  7,  44,  29),
    ("Portugal",     "🇵🇹", 0,  9,  37, 17, 13,  7,  51,  35),
    ("Belgium",      "🇧🇪", 0, 14,  48, 21, 17, 10,  68,  52),
    ("Poland",       "🇵🇱", 0, 10,  36, 17, 12,  7,  48,  45),
    ("Sweden",       "🇸🇪", 0, 12,  50, 19, 16, 15,  74,  69),
    ("Mexico",       "🇲🇽", 0, 17,  59, 14, 22, 23,  58,  98),
    ("Russia",       "🇷🇺", 0, 11,  43, 17, 13, 13,  64,  50),
    ("Morocco",      "🇲🇦", 0,  9,  28,  9, 14,  5,  26,  24),
    ("Japan",        "🇯🇵", 0,  8,  24,  9,  9,  6,  24,  27),
    ("South Korea",  "🇰🇷", 0, 11,  38, 12, 15, 11,  48,  58),
    ("USA",          "🇺🇸", 0, 11,  38, 13, 15, 10,  44,  58),
]

def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    PRAGMA foreign_keys = ON;
    PRAGMA journal_mode = WAL;

    CREATE TABLE IF NOT EXISTS tournaments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        year        INTEGER UNIQUE NOT NULL,
        host        TEXT NOT NULL,
        winner      TEXT NOT NULL,
        teams       INTEGER,
        matches     INTEGER,
        goals       INTEGER,
        notes       TEXT,
        goals_per_match REAL GENERATED ALWAYS AS (ROUND(CAST(goals AS REAL)/matches,2)) STORED
    );

    CREATE TABLE IF NOT EXISTS matches (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        year        INTEGER NOT NULL,
        stage       TEXT NOT NULL,
        team1       TEXT NOT NULL,
        team2       TEXT NOT NULL,
        score1      INTEGER,
        score2      INTEGER,
        extra       TEXT,
        venue       TEXT,
        attendance  INTEGER,
        winner      TEXT,
        total_goals INTEGER GENERATED ALWAYS AS (score1 + score2) STORED,
        FOREIGN KEY (year) REFERENCES tournaments(year)
    );

    CREATE TABLE IF NOT EXISTS players (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        country     TEXT NOT NULL,
        flag        TEXT,
        goals       INTEGER DEFAULT 0,
        tournaments INTEGER DEFAULT 0,
        matches     INTEGER DEFAULT 0,
        position    TEXT,
        era         TEXT,
        goals_per_match REAL GENERATED ALWAYS AS (
            CASE WHEN matches > 0 THEN ROUND(CAST(goals AS REAL)/matches,2) ELSE 0 END
        ) STORED
    );

    CREATE TABLE IF NOT EXISTS teams (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL UNIQUE,
        flag        TEXT,
        titles      INTEGER DEFAULT 0,
        appearances INTEGER DEFAULT 0,
        matches_played INTEGER DEFAULT 0,
        wins        INTEGER DEFAULT 0,
        draws       INTEGER DEFAULT 0,
        losses      INTEGER DEFAULT 0,
        goals_scored INTEGER DEFAULT 0,
        goals_conceded INTEGER DEFAULT 0,
        win_rate    REAL GENERATED ALWAYS AS (
            CASE WHEN matches_played > 0 THEN ROUND(CAST(wins AS REAL)/matches_played*100,1) ELSE 0 END
        ) STORED,
        goal_difference INTEGER GENERATED ALWAYS AS (goals_scored - goals_conceded) STORED
    );

    CREATE TABLE IF NOT EXISTS kpi_cache (
        key         TEXT PRIMARY KEY,
        value       TEXT NOT NULL,
        updated_at  TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_matches_year  ON matches(year);
    CREATE INDEX IF NOT EXISTS idx_matches_stage ON matches(stage);
    CREATE INDEX IF NOT EXISTS idx_matches_team1 ON matches(team1);
    CREATE INDEX IF NOT EXISTS idx_matches_team2 ON matches(team2);
    CREATE INDEX IF NOT EXISTS idx_players_goals ON players(goals DESC);
    CREATE INDEX IF NOT EXISTS idx_teams_titles  ON teams(titles DESC);
    """)

    # Insert tournaments
    c.executemany(
        "INSERT OR IGNORE INTO tournaments (year,host,winner,teams,matches,goals,notes) VALUES (?,?,?,?,?,?,?)",
        TOURNAMENTS
    )

    # Insert matches
    c.executemany(
        "INSERT OR IGNORE INTO matches (year,stage,team1,team2,score1,score2,extra,venue,attendance,winner) VALUES (?,?,?,?,?,?,?,?,?,?)",
        MATCHES
    )

    # Insert players
    c.executemany(
        "INSERT OR IGNORE INTO players (name,country,flag,goals,tournaments,matches,position,era) VALUES (?,?,?,?,?,?,?,?)",
        PLAYERS
    )

    # Insert teams
    c.executemany(
        "INSERT OR IGNORE INTO teams (name,flag,titles,appearances,matches_played,wins,draws,losses,goals_scored,goals_conceded) VALUES (?,?,?,?,?,?,?,?,?,?)",
        TEAMS
    )

    # Pre-compute KPIs into cache
    kpis = {
        "total_tournaments": len(TOURNAMENTS),
        "total_matches": len(MATCHES),
        "total_goals": sum(m[4]+m[5] for m in MATCHES),
        "total_nations": len(TEAMS),
        "avg_goals_per_match": round(sum(m[4]+m[5] for m in MATCHES) / len(MATCHES), 2),
        "highest_scoring_match": "Brazil 7-1 Germany (2014)",
        "most_goals_tournament": "France 1998 (171 goals)",
        "all_time_top_scorer": "Miroslav Klose (16 goals)",
    }
    for k, v in kpis.items():
        c.execute("INSERT OR REPLACE INTO kpi_cache(key,value) VALUES (?,?)", (k, json.dumps(v)))

    conn.commit()
    conn.close()
    print(f"✅ Database created at {DB_PATH}")
    print(f"   Tournaments: {len(TOURNAMENTS)}")
    print(f"   Matches:     {len(MATCHES)}")
    print(f"   Players:     {len(PLAYERS)}")
    print(f"   Teams:       {len(TEAMS)}")

if __name__ == "__main__":
    create_db()
