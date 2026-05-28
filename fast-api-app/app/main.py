from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

# Absolute import matching Uvicorn's root search path
from app.database import r, init_db, WORD_POOL_KEY

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Shutting down application...")

app = FastAPI(lifespan=lifespan)

current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = os.path.join(current_dir, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/get-word")
def get_random_word():
    random_word = r.srandmember(WORD_POOL_KEY)
    
    if not random_word:
        raise HTTPException(
            status_code=500, 
            detail=f"Database Error: No words found in the '{WORD_POOL_KEY}' pool."
        )
    
    word_details = r.hgetall(f"word:{random_word}")
    return {
        "word": random_word,
        "details": word_details
    }