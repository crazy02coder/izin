from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import Base, engine
from app.routers import auth, users, leaves, dashboard, catalog

Base.metadata.create_all(engine)
app = FastAPI(title="OSTİM Teknik Üniversitesi İzin Portalı", version="1.0.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(leaves.router)
app.include_router(dashboard.router)
app.include_router(catalog.router)
