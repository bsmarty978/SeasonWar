from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

app = FastAPI()

# Initialize the database when the app starts
def init_db():
    conn = sqlite3.connect('votes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            season TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        )
    ''')
    
    # Insert default values for each season if they don't exist
    seasons = ["spring", "summer", "autumn", "winter"]
    for season in seasons:
        cursor.execute('''
            INSERT OR IGNORE INTO votes (season, count) VALUES (?, 0)
        ''', (season,))
    
    conn.commit()
    conn.close()

init_db()

# Connect to the database
def get_db_connection():
    conn = sqlite3.connect('votes.db')
    conn.row_factory = sqlite3.Row  # To return results as dictionaries
    return conn

# Pydantic model for vote input
class Vote(BaseModel):
    season: str

# Pydantic model for reset input (optional list of seasons)
class ResetVotes(BaseModel):
    seasons: Optional[List[str]] = None

@app.get("/votes")
def get_votes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM votes")
    results = cursor.fetchall()
    
    votes = {row["season"]: row["count"] for row in results}
    
    conn.close()
    
    return votes

@app.post("/vote")
def cast_vote(vote: Vote):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the season exists in the database
    cursor.execute("SELECT count FROM votes WHERE season = ?", (vote.season,))
    result = cursor.fetchone()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Season not found")
    
    # Update the vote count for the selected season
    cursor.execute("UPDATE votes SET count = count + 1 WHERE season = ?", (vote.season,))
    conn.commit()

    # Fetch updated votes
    cursor.execute("SELECT * FROM votes")
    updated_results = cursor.fetchall()

    updated_votes = {row["season"]: row["count"] for row in updated_results}
    
    conn.close()
    
    return updated_votes

# New endpoint to reset votes
@app.post("/reset")
def reset_votes(reset_votes: ResetVotes):
    conn = get_db_connection()
    cursor = conn.cursor()

    if reset_votes.seasons:
        # Reset votes for specific seasons
        for season in reset_votes.seasons:
            cursor.execute("SELECT count FROM votes WHERE season = ?", (season,))
            result = cursor.fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail=f"Season '{season}' not found")
            
            cursor.execute("UPDATE votes SET count = 0 WHERE season = ?", (season,))
    else:
        # Reset all seasons
        cursor.execute("UPDATE votes SET count = 0")

    conn.commit()

    # Fetch updated votes after reset
    cursor.execute("SELECT * FROM votes")
    updated_results = cursor.fetchall()

    updated_votes = {row["season"]: row["count"] for row in updated_results}
    
    conn.close()
    
    return updated_votes
