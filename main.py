from fastapi import FastAPI, Request
import models
from fastapi.templating import Jinja2Templates
from database import engine
from routers import post, user, auth, vote
from webapps.routers import post as web_post, user as web_user, auth as web_auth
from config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(web_post.router)
app.include_router(web_user.router)
app.include_router(web_auth.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def root(request: Request, msg:str=None):

    return templates.TemplateResponse("homepage.html", {"request": request, "msg":msg})

