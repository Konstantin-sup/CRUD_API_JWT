from sql.models import User, Protected
from sqlalchemy import select
from fastapi import HTTPException
from main_app.jwt_auth import hash_password
import csv
from main_app.exeptions_alert import WasNotFound, EmptyRequest


def del_check(session, id: int):  #checks if deleted id still in db
    user = session.get(User, id)

    if not user:
        return True

    return False


def del_from_db(session, id: int):
    """No commit, so i don't accidentally delete sme data(even from test base)"""
    user = session.get(User, id)
    user_protected = session.get(Protected, id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="id doesn't exist"
        )

    session.delete(user)
    session.delete(user_protected)
    session.flush()


def select_data_login(session_factory, us_name):
    with session_factory as session:
        req = select(Protected).where(
            Protected.user_name == us_name
        )
        res = session.execute(req)
        users = res.scalars().all()
        return users


def create_db_select_request(filter_class):
    filter = []
    values = {"limit": filter_class.limit, "offset": filter_class.offset}

    if filter_class.completed is not None:
        filter.append("completed = :completed")
        values["completed"] = filter_class.completed

    if filter_class.user_name is not None:
        filter.append("user_name = :user_name")
        values["user_name"] = filter_class.user_name

    if filter_class.title is not None:
        filter.append("title = :title")
        values["title"] = filter_class.title

    if filter_class.role is not None:
        filter.append("role = :role")
        values["role"] = filter_class.role

    if filter_class.id is not None:
        filter.append("id = :id")
        values["id"] = filter_class.id

    if filter_class.description is not None:
        filter.append("description = :description")
        values["description"] = filter_class.description

    where_expression = f'WHERE {" AND ".join(filter)}' if filter else ''

    query = f"""
                SELECT id, user_name, title, description, completed, role 
                FROM test_api_sql
                {where_expression}
                LIMIT  :limit OFFSET :offset
            """

    return query, values


def create_user_data(session, create_user_class):
    data = User(user_name=create_user_class.user_name, title=create_user_class.title,
                description=create_user_class.description, completed=create_user_class.completed,
                role=create_user_class.role)

    session.add(data)
    session.commit()
    session.refresh(data)

    return data.id, create_user_class.password, data


def create_data_to_protected(session, create_user_class_protected, us_id):
    he_pass = hash_password(create_user_class_protected.password)

    protected_data = Protected(user_name=create_user_class_protected.user_name,
                               password=he_pass,
                               role=create_user_class_protected.role,
                               id=us_id)

    session.add(protected_data)
    session.commit()


def add_secret(data: dict):
    with open(r"/\SQL\secrets.csv", "a", newline="",
              encoding="utf-8") as f_obj:
        field_names = ["id", "password"]
        writer = csv.DictWriter(f_obj, fieldnames=field_names)

        writer.writerow(data)


def update_user(session, update_class, us_id):
    values = {}
    user_obj = session.query(User).where(User.id == us_id).first()
    protected_user_obj = session.query(Protected).where(Protected.id == us_id).first()

    if not user_obj:
        raise WasNotFound(status_code=404,
                          detail=f"No user found with id '{us_id}'",
                          message=f"id '{us_id}' doesn't exist",
                          er_code="No id in base -> update")

    if update_class.completed is not None:
        values["completed"] = update_class.completed

    if update_class.user_name is not None:
        values["user_name"] = update_class.user_name
        protected_user_obj.user_name = update_class.user_name

    if update_class.title is not None:
        values["title"] = update_class.title

    if update_class.role is not None:
        values["role"] = update_class.role
        protected_user_obj.role = update_class.role

    if update_class.description is not None:
        values["description"] = update_class.description

    if not values:
        raise EmptyRequest(status_code=400,
                           detail="Your body request is empty",
                           er_code="Empty req -> update")

    for field, value in values.items():
        setattr(user_obj, field, value)

    session.commit()
    session.refresh(user_obj)
    return user_obj


