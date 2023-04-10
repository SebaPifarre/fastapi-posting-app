from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas, oauth2
from database import  get_db
from typing import List, Optional
from oauth2 import oauth2_scheme
from utils import get_user_from_cookie




router = APIRouter(
    prefix="/posts",
    tags= ['Posts']
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user),
             limit: int = 10, skip: int =0, search: Optional[str] = ""):

    results= db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):    # Validation of Post
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/autocomplete")
def autocomplete(term:Optional[str], db:Session = Depends(get_db)):
    
    posts = db.query(models.Post).filter(models.Post.title.contains(term))
    suggestions = []
    for post in posts:
        suggestions.append(post.title)
    return suggestions


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")

    return post



@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_user_from_cookie(db, token)
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not authorized to perform request action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    content = {"message": f"Post ID {id} has been successfully deleted"}
    response = JSONResponse(content=content)

    return response



@router.put("/update/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_user_from_cookie(db, token)
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")


    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not authorized to perform request action")                      
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    
    db.commit()
    
    return {"message": f"Details succesfully updated for post ID={id}"}

