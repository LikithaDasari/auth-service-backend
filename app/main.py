import uvicorn
from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.routes import users

app = FastAPI(title="User Auth API")

# startup event
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# include routers
app.include_router(users.router, prefix="/users", tags=["Users"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)