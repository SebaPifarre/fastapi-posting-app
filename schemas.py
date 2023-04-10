from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic import conint

# This class defines the schema of how the data should look like so the request and the respose have the same format.
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True  # If the user doesn't provide "published" than it is defaulted to True

# By using inheritance, we can create a new class that inherites from the PostBase and control which fields is the user allowed to modify. 
class PostCreate(PostBase):
    pass

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

        
class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr # This validates if the user enters a valid email and not some random text.
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)