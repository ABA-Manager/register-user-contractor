import re
import requests

from fastapi import FastAPI, Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import setting
from Models.model import Database

app = FastAPI()
templates = Jinja2Templates(directory="Template/")
app.mount("/static", StaticFiles(directory="static/"), name="static")

@app.get("/register/{contractor_id}")
async def form_get(request: Request,contractor_id: int):
    db = Database(
        setting.DB_HOST,
        setting.DB_NAME,
        setting.DB_USER,
        setting.DB_PASSWORD
    )
    company=db.getComapnyname(contractor_id)
    image_name = None
    if str(company[0]) == "Expanding Possibilities":
        image_name = "expanding.png"
    elif str(company[0]) == "Villa Lyan":
        image_name = "villa.png"
    return templates.TemplateResponse("index.html", {"request": request,"image_name":image_name})

@app.post("/register/{contractor_id}")
async def form_post(request: Request,contractor_id: int,email: str = Form(...), username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    form_data = {"username": username, "password": password,"confirmPassword":confirm_password,"email":email}
    if not re.match(r"^(?=.*[.,])(?=.*[a-zA-Z])(?=.*\d)[\w.,$!%*?&]{8,}$", password):
        return templates.TemplateResponse("index.html",{"request": request, "error_message": "The password must be at least 8 characters long and contain either '.' or ','.","form_data": form_data})
    if password != confirm_password:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "The passwords do not match.","form_data": form_data})

    response = requests.post(f"{setting.URL_COMPANY}/auth/register", json={"username": username, "password": password,"confirmPassword":confirm_password,
                                                                                           "rol": ["Contractor"],"email":email,})
    if response.status_code == 200:
        db = Database(
            setting.DB_HOST,
            setting.DB_NAME,
            setting.DB_USER,
            setting.DB_PASSWORD
        )
        UserId=db.get_userid(username)
        response2=requests.post(f"{setting.URL_COMPANY}/servicelogbycontractor/createuser",json={"ContractorId":contractor_id,"UserId":str(UserId[0])})
        if response2.status_code==204:
            return {"message": "User registered successfully"}
        else:
            return {"message": "Error registering userContractor"}
    else:
            return {"message": "Error registering user"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8080)
