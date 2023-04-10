from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, models, utils
from jose import jwt
from config import settings

router = APIRouter(
    tags=["Authentification"]
)

@router.post('/login')
def login(response: Response, user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    data = {"sub": user_credentials.username}
    access_token = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}
