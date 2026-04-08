# app.py - Detroit Tigers Dashboard Backend
# This file is the "server" - it fetches Tigers data from MLB and sends it to your webpage

from flask import Flask, jsonify, render_template  # Flask is our web server
from flask_cors import CORS        # This allows your webpage to talk to this server
import requests                    # This lets us fetch data from the MLB API
from datetime import datetime      # For getting today's date

app = Flask(__name__)
CORS(app)  # Allow the frontend (HTML page) to call this server

# The Detroit Tigers team ID in the MLB system
TIGERS_TEAM_ID = 116


# -------------------------------------------------------
# HELPER FUNCTION: fetch data from MLB API
# -------------------------------------------------------
def mlb_get(path):
    """Fetches data from the MLB Stats API and returns it as a Python dictionary."""
    base_url = "https://statsapi.mlb.com/api/v1"
    response = requests.get(base_url + path, timeout=10)
    return response.json()


# -------------------------------------------------------
# ROUTE 0: Serve the dashboard webpage
# -------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------------
# ROUTE 1: Today's game score (or most recent game)
# -------------------------------------------------------
@app.route("/api/score")
def get_score():
    today = datetime.now().strftime("%Y-%m-%d")
    data = mlb_get(f"/schedule?teamId={TIGERS_TEAM_ID}&date={today}&sportId=1&hydrate=linescore")

    games = data.get("dates", [])
    if not games or not games[0].get("games"):
        # No game today - get last 5 games
        data = mlb_get(f"/schedule?teamId={TIGERS_TEAM_ID}&season=2025&sportId=1&hydrate=linescore&gameType=R")
        all_games = []
        for d in data.get("dates", []):
            all_games.extend(d.get("games", []))
        # Filter to completed games only
        completed = [g for g in all_games if g.get("status", {}).get("abstractGameState") == "Final"]
        recent = completed[-5:] if completed else []
        return jsonify({"today": None, "recent": format_games(recent)})

    game = games[0]["games"][0]
    return jsonify({"today": format_game(game), "recent": []})


def format_game(g):
    """Pull the important bits out of a raw MLB game object."""
    teams = g.get("teams", {})
    away = teams.get("away", {})
    home = teams.get("home", {})
    status = g.get("status", {}).get("detailedState", "Scheduled")
    linescore = g.get("linescore", {})

    return {
        "status": status,
        "inning": linescore.get("currentInningOrdinal", ""),
        "away_team": away.get("team", {}).get("name", ""),
        "away_score": away.get("score", 0),
        "home_team": home.get("team", {}).get("name", ""),
        "home_score": home.get("score", 0),
        "venue": g.get("venue", {}).get("name", ""),
    }

def format_games(games):
    return [format_game(g) for g in games]


# -------------------------------------------------------
# ROUTE 2: AL Central Standings
# -------------------------------------------------------
@app.route("/api/standings")
def get_standings():
    data = mlb_get("/standings?leagueId=103&season=2025&standingsTypes=regularSeason")
    records = data.get("records", [])

    # AL Central division ID is 202
    al_central = next((r for r in records if r.get("division", {}).get("id") == 202), None)
    if not al_central:
        return jsonify([])

    teams = []
    for entry in al_central.get("teamRecords", []):
        teams.append({
            "team": entry["team"]["name"],
            "wins": entry["wins"],
            "losses": entry["losses"],
            "pct": entry["winningPercentage"],
            "gb": entry.get("gamesBack", "-"),
            "streak": entry.get("streak", {}).get("streakCode", ""),
        })
    return jsonify(teams)


# -------------------------------------------------------
# ROUTE 3: Tigers roster with batting stats
# -------------------------------------------------------
@app.route("/api/stats")
def get_stats():
    # Batting leaders
    batting = mlb_get(f"/teams/{TIGERS_TEAM_ID}/stats?stats=season&group=hitting&season=2025&sportId=1")
    # Pitching leaders
    pitching = mlb_get(f"/teams/{TIGERS_TEAM_ID}/stats?stats=season&group=pitching&season=2025&sportId=1")

    batters = []
    for split in batting.get("stats", [{}])[0].get("splits", []):
        s = split.get("stat", {})
        p = split.get("player", {})
        if int(s.get("atBats", 0)) >= 20:  # Only show players with enough at-bats
            batters.append({
                "name": p.get("fullName", ""),
                "avg": s.get("avg", ".000"),
                "hr": s.get("homeRuns", 0),
                "rbi": s.get("rbi", 0),
                "hits": s.get("hits", 0),
            })
    # Sort by batting average
    batters.sort(key=lambda x: float(x["avg"]), reverse=True)

    pitchers = []
    for split in pitching.get("stats", [{}])[0].get("splits", []):
        s = split.get("stat", {})
        p = split.get("player", {})
        if float(s.get("inningsPitched", "0")) >= 10:  # Only meaningful sample
            pitchers.append({
                "name": p.get("fullName", ""),
                "era": s.get("era", "0.00"),
                "wins": s.get("wins", 0),
                "losses": s.get("losses", 0),
                "strikeouts": s.get("strikeOuts", 0),
                "innings": s.get("inningsPitched", "0"),
            })
    pitchers.sort(key=lambda x: float(x["era"]))

    return jsonify({"batting": batters[:10], "pitching": pitchers[:10]})


# -------------------------------------------------------
# Run the app
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)  # debug=True shows helpful error messages while developing
