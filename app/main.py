import uvicorn
from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.routes import login, registration, password
from core.middleware import limiter, rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded 

app = FastAPI(title="User Auth API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# startup event
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# include routers
app.include_router(registration.router, prefix="/user", tags=["Registration"])
app.include_router(login.router, prefix="/user", tags=["Login"])
app.include_router(password.router, prefix="/user", tags=["Passwords"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)