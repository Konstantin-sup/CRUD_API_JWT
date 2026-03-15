#uvicorn main_app.main_file:app --reload
from http.client import responses

from fastapi import FastAPI, HTTPException,Depends, Request
from fastapi.responses import JSONResponse
from main_app.jwt_auth import verify_password, code_jwt, role_required, role_control
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import ValidationException
from main_app.exeptions_alert import validator_err, WasNotFound, NoEnter, EmptyRequest
from sql.models import LogIn, UserFilter, CreateUser, UpdateData
from sql.db import engine
from sql.mine_sql_functions import  (select_data_login, create_db_select_request,
                                     del_from_db, create_user_data, create_data_to_protected,
                                     add_secret, update_user)

app = FastAPI()
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db  #сессия
    finally:
        db.close()


@app.exception_handler(ValidationException)
def err_info(request: Request, ex: ValidationException):
    validator_err(request, ex)


@app.exception_handler(IntegrityError)
def unique_err(request: Request):
    return JSONResponse(status_code=400,
                        content={"message": "user_name already exists"})


@app.exception_handler(WasNotFound)
def err_not_found(request: Request, ex: WasNotFound):
    return JSONResponse(
        status_code=ex.status_code,
        content={
            "status": ex.status_code,
            "message": ex.message,
            "detail": ex.detail,
            "er_code": ex.er_code
        },
    )

@app.exception_handler(NoEnter)
def no_enter_err(request: Request, ex: NoEnter):
    return JSONResponse(status_code=ex.status_code,
                        content={"message": ex.message,
                                 "detail": ex.detail,
                                 "required_role": ex.required_role,
                                 "user_status": ex.users_role,
                                 "er_code": ex.er_code})

@app.exception_handler(EmptyRequest)
def unique_err(request: Request, ex: EmptyRequest):
    return JSONResponse(status_code=400,
                        content={"detail": ex.detail,
                                 "er_code": ex.er_code})



@app.post("/login")
def log_user(user_data: LogIn, db_session: Session = Depends(get_db)):
    """Takes json {user_name, password}, and returns jwt with users_role"""
    user_in_db = select_data_login(db_session, user_data.user_name)

    if not user_in_db:
         raise WasNotFound(status_code=404,
                           detail="User_name wasn't found in the base",
                           message="Please, check spelling of your input",
                           er_code="Wrong user_name -> login")


    for data in user_in_db:   #could be multiple same us_names in base
        if verify_password(user_data.password, data.password):
            return JSONResponse({"token": code_jwt({"sub": data.role, "id": data.id, "user_name": data.user_name}),
                                 "message": f"Hello, {user_data.user_name}"},
                                status_code=200)



    return JSONResponse(status_code=401,
                        content={"message": "Authorization failed"})


@app.post("/select/")
def send_data(request_filter_class: UserFilter,
              db : Session = Depends(get_db),
              ):
    """Takes json with params of request, and returns list[dict] with data,
    could be several dicts as output, can also take empty {} json"""

    query, values = create_db_select_request(request_filter_class)
    result = db.execute(text(query), values)
    rows = result.mappings().all()

    if not rows:
        raise WasNotFound(status_code=200,
                          message="No data for your request",
                          detail="Nothing was found in the base",
                          er_code="Empty response -> select")


    rows_dict = [dict(row) for row in rows]

    return JSONResponse({"data": rows_dict})


@app.delete("/delete/{id}")
def del_data(id: int,
            current_user = Depends(role_required(["admin", "moder"])),
            db: Session = Depends(get_db),):
    """Required jwt token with 'admin' or 'moder' as 'sub', and id"""

    try:
        del_from_db(db, id)
        return JSONResponse(status_code=204,
                            content={"message": f"id: {id}, was deleted"})

    except HTTPException as ex:
        return JSONResponse(status_code=ex.status_code,
                            content={"message": ex.detail})


@app.post("/create")
def create_new_user(create_data: CreateUser,
                    db: Session = Depends(get_db),
                    current_user = Depends(role_required(["admin", "moder", "user"]))):
    """Takes json with request params, required jwt with 'sub' in ["admin", "moder", "user"]"""

    role_control(current_user["sub"], create_data.role)
    us_id, us_password, user_obj = create_user_data(db, create_data)
    create_data_to_protected(db, create_data, us_id)
    secret_info = {"id": us_id, "password": us_password}
    add_secret(secret_info)
    response_data = {
        "id": user_obj.id,
        "user_name": user_obj.user_name,
        "title": user_obj.title,
        "description": user_obj.description,
        "completed": user_obj.completed,
        "role": user_obj.role
    }

    return JSONResponse(status_code=201,
                        content={"message": "user was created",
                                 "created_data": response_data})


@app.patch("/update/{id}")
def update_data(update_class: UpdateData,
                id: int,
                current_user = Depends(role_required(["admin", "moder"])),
                db: Session = Depends(get_db)):
    """Required jwt token with 'admin' or 'moder' as 'sub' with users 'id',
    and json with update data(couldn't be empty {})"""

    fresh_user_obj = update_user(db, update_class, id)
    response_data = {"user_name": fresh_user_obj.user_name, "title": fresh_user_obj.title,
                     "description": fresh_user_obj.description, "completed": fresh_user_obj.completed,
                     "role": fresh_user_obj.role}

    # I haven't done a func that returns user_info dict like in "/create"(response_data) or here,
    #becouse sometimes I have to return different dicts with different keys in it,
    #so I would spend some time to write the func and only use it twice.

    return JSONResponse(status_code=200, content=response_data)







#uvicorn main_app.main_file:app --reload


#curl -X POST http://127.0.0.1:8000/select/ -H "Content-Type: application/json" -d "{\"user_name\":\"admin_one\",\"password\":\"admin123\"}"




