import re
import requests

from fastapi import FastAPI, Request,Form
from fastapi.templating import Jinja2Templates

import setting
from Models.model import Database

app = FastAPI()
templates = Jinja2Templates(directory="Template/")

@app.get("/register/{contractor_id}")
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register/{contractor_id}")
async def form_post(request: Request,contractor_id: int,email: str = Form(...), username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    form_data = {"username": username, "password": password,"confirmPassword":confirm_password,"email":email}
    if not re.match(r"^(?=.*[.,])(?=.*[a-zA-Z])(?=.*\d)[\w.,$!%*?&]{8,}$", password):
        return templates.TemplateResponse("index.html",{"request": request, "error_message": "The password must be at least 8 characters long and contain either '.' or ','.","form_data": form_data})
    if password != confirm_password:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "The passwords do not match.","form_data": form_data})

    response = requests.post("https://test.abaanalystgroup.live/api/Auth/Register", json={"username": username, "password": password,"confirmPassword":confirm_password,
                                                                                           "rol": ["Contractor"],"email":email,},verify=False)
    if response.status_code == 200:
        db = Database(
            setting.DB_HOST,
            setting.DB_NAME,
            setting.DB_USER,
            setting.DB_PASSWORD
        )
        UserId=db.get_userid(username)
        response2=requests.post("https://test.abaanalystgroup.live/api/servicelogbycontractor/createuser",json={"ContractorId":contractor_id,"UserId":str(UserId[0])})
        if response2.status_code==204:
            return {"message": "User registered successfully"}
        else:
            return {"message": "Error registering userContractor"}
    else:
            return {"message": "Error registering user"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8080)