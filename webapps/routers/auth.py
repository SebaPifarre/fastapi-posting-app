from fastapi import APIRouter, Depends, Request, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User
from utils import verify
from oauth2 import create_access_token

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")

@router.get("/loginweb")
def loginweb(request: Request, msg:str=None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@router.post("/loginweb")
async def loginweb(response: Response, request: Request, db:Session = Depends(get_db)):
    form = await request.form()
    cred_email = form.get("email")
    cred_password = form.get("password")
    errors=[]
    if not cred_email:
        errors.append("Please enter valid email")
    if not cred_password or len(cred_password) < 4:
        errors.append("password should be > 4")

    try:
        user = db.query(User).filter(User.email==cred_email).first()
        if not user:
            errors.append("Email does not exist")
            return templates.TemplateResponse("login.html", {"request":request, "errors":errors})
        else:
            if verify(cred_password, user.password):
                data = {"sub": user.email}
                jwt_token = create_access_token(data)
                msg = "Login succesful!"
                response = templates.TemplateResponse("login.html", {"request":request, "msg":msg})
                response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
                return response
            else:
                errors.append("Invalid password")
                return templates.TemplateResponse("login.html", {"request":request, "errors":errors}) 
    except:
        errors.append("Something went wrong!")
        return templates.TemplateResponse("login.html", {"request":request, "errors":errors})


