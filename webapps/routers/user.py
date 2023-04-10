import models, utils
from fastapi import status, Depends, APIRouter, Request, responses
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import  get_db

router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(directory="templates")

@router.get("/register")
def registration(request: Request):
    return templates.TemplateResponse("user_register.html", {"request": request})

@router.post("/register")
async def registration(request: Request, db: Session = Depends(get_db)):
    
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    
    # hashed_pass = utils.hash(password)
    # user.password = hashed_pass

    errors = []
    if len(password)<4:
        errors.append("Password should be > 4 characters")
        return templates.TemplateResponse("user_register.html", {"request":request, "errors":errors})

    new_user = models.User(email=email, password=utils.hash(password))
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return responses.RedirectResponse("/loginweb?msg=Succesfully registered!", status_code=status.HTTP_302_FOUND)
    except IntegrityError:
        errors.append("Email already exists")
        return templates.TemplateResponse("user_register.html", {"request":request, "errors":errors})
    
    




