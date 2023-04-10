from fastapi import status, HTTPException, Depends, APIRouter, Request, responses
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from models import User, Post
from database import  get_db
from typing import List, Optional
from utils import get_authorization_scheme_param
from jose import jwt
from config import settings



router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(directory="templates")

@router.get("/details", response_model=List[schemas.PostOut])
def get_posts(request: Request, db: Session = Depends(get_db),
             limit: int = 10, skip: int =0, search: Optional[str] = ""):


    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return templates.TemplateResponse("posts_display.html",{"request": request, "posts": results})


@router.get("/details/{id}", response_model=schemas.PostOut)
def get_post(request: Request, id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")

    return templates.TemplateResponse("post_detail.html", {"request": request, "post": post})


@router.get("/update-a-post/{id}")
def edit_post(id:int,  request:Request, db:Session=Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id==id).first()
    return templates.TemplateResponse("update_post.html", {"request": request, "post": post})


@router.get("/create-a-post")
def create_a_post(request: Request):
    return templates.TemplateResponse("create_a_post.html", {"request": request})


@router.post("/create-a-post")
async def create_a_post(request: Request, db:Session=Depends(get_db)):
    form = await request.form()
    new_title = form.get("title")
    new_content = form.get("content")
    errors = []
    if not new_title or len(new_title) < 4:
        errors.append("Title should be > 4 chars")
    if not new_content or len(new_content) < 4:
        errors.append("Content shold be > 4 chars")
    if len(errors) > 0:
        return templates.TemplateResponse("create_a_post.html", {"request":request, "errors": errors})
    try:
        token = request.cookies.get("access_token")
        if token is None:
            errors.append("Please login first")
            return templates.TemplateResponse("create_a_post.html", {"request":request, "errors": errors})
        else:
            scheme, param = get_authorization_scheme_param(token)
            payload = jwt.decode(param, settings.secret_key, settings.algorithm)
            email = payload.get("sub")
            user = db.query(User).filter(User.email==email).first()

            if user is None:
                errors.append("You are not authenticated, please create an account or login first")
                return templates.TemplateResponse("create_a_post.html", {"request":request, "errors": errors})
            else:
                new_post = Post(title=new_title, content=new_content, owner_id=user.id)
                db.add(new_post)
                db.commit()
                db.refresh(new_post)
                return responses.RedirectResponse(f"/details/{new_post.id}", status_code=status.HTTP_302_FOUND)


    except Exception as e:
        errors.append("Something went wrong")
        return templates.TemplateResponse("create_a_post.html", {"request":request, "errors": errors})


@router.get("/update-delete-post")
def show_posts_to_delete(request: Request, db: Session= Depends(get_db)):
    token = request.cookies.get("access_token")
    errors = []
    if token is None:
        errors.append("You are not logged in / Authenticated")
        return templates.TemplateResponse("show_posts_to_update_delete.html", {"request": request, "errors": errors})
    else:
        try:
            scheme, param = get_authorization_scheme_param(token)
            payload = jwt.decode(param, settings.secret_key, settings.algorithm)
            email = payload.get("sub")
            user = db.query(User).filter(User.email==email).first()
            posts = db.query(models.Post).filter(models.Post.owner_id==user.id).all()
            return templates.TemplateResponse("show_posts_to_update_delete.html", {"request":request, "posts": posts})
        except Exception as e:
            errors.append("Something is wrong")
            print(e)
            return templates.TemplateResponse("show_posts_to_update_delete.html", {"request": request, "errors": errors})


@router.get("/search")
def search(request: Request, query:Optional[str], db:Session=Depends(get_db)):
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(query)).all()
    return templates.TemplateResponse("posts_display.html", {"request": request,"posts": posts})


