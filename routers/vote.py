from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
import database, models, oauth2
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/vote",
    tags= ['Vote']
)

@router.post("/{id}", status_code=status.HTTP_201_CREATED)
def vote(id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == id, models.Vote.user_id == current_user.id)
    
    found_vote = vote_query.first()
    

    if found_vote:
            content = {"message": f"User with ID={current_user.id} has already voted on post {id}"}
            response = JSONResponse(content=content)
            return response
    new_vote = models.Vote(post_id= id, user_id = current_user.id)
    db.add(new_vote)
    db.commit()
    content = {"message": "Succesfully added a vote"}
    response = JSONResponse(content=content)
    return response

 