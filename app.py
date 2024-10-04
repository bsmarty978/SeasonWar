from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os

app = FastAPI(
    title="Seasons-War API",
    version="0.1",
    description="This is API for Seasons War Game, where user can vote to any season they want to. Also, can check the current votes of each season."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*', 'http://localhost:3000'],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for votes
class VoteCounter:
    def __init__(self):
        self.votes = {
            "spring": 0,
            "summer": 0,
            "autumn": 0,
            "winter": 0
        }

    def get_votes(self):
        return self.votes

    def cast_vote(self, season: str):
        if season not in self.votes:
            raise HTTPException(status_code=404, detail="Season not found")
        self.votes[season] += 1
        return self.votes

    def reset_votes(self, seasons: Optional[List[str]] = None):
        if seasons:
            for season in seasons:
                if season not in self.votes:
                    raise HTTPException(status_code=404, detail=f"Season '{season}' not found")
                self.votes[season] = 0
        else:
            # Reset all seasons
            for season in self.votes:
                self.votes[season] = 0
        return self.votes

# Initialize vote counter
vote_counter = VoteCounter()

# Pydantic model for vote input
class Vote(BaseModel):
    season: str

# Pydantic model for reset input (optional list of seasons)
class ResetVotes(BaseModel):
    seasons: Optional[List[str]] = None

# Redirect from root to docs
@app.get("/")
async def read_root():
    return RedirectResponse(url="/docs")

@app.get("/votes")
def get_votes():
    return vote_counter.get_votes()

@app.post("/vote")
def cast_vote(vote: Vote):
    return vote_counter.cast_vote(vote.season)

@app.post("/reset")
def reset_votes(reset_votes: ResetVotes):
    return vote_counter.reset_votes(reset_votes.seasons)
