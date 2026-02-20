from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_health import health

from backend.app.rest import seasons, sessions


def check_api() -> dict[str, str]:
    return {"api": "online"}


app = FastAPI(
    title="F1 Analysis Tool API",
    description="REST API for my formula 1 analysis tool project",
    version="0.1.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api_route("/health", health([check_api]))
app.include_router(seasons.router)
app.include_router(sessions.router)
