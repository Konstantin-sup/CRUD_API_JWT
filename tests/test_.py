import pytest
from sql.db import session
from tests.fixtures_test import async_client_fix, admin_token, db_fix
from main_app.jwt_auth import de_code, verify_password
from sql.models import User, Protected  #table models
from sql.mine_sql_functions import del_from_db
api_url = "http://127.0.0.1:8000"


@pytest.mark.parametrize(
    "login_data", [
    {"user_name": "admin_two", "password": "admin456", "role": "admin"},
    {"user_name": "moder_two", "password": "moder456", "role": "admin"},
    {"user_name": "alex_new", "password": "admin_one_11", "role": "admin"},
    {"user_name": "moder_one", "password": "moder_one_12", "role": "admin"},
    {"user_name": "user_one", "password": "user_one_13", "role": "user"},
    {"user_name": "maria22", "password": "guest_one_14", "role": "guest"},
    {"user_name": "user_two", "password": "user_two_15", "role": "user"},
    {"user_name": "guest_two", "password": "guest_two_16", "role": "moderator"},
    {"user_name": "user_three", "password": "user_three_17", "role": "user"},
    {"user_name": "guest_three", "password": "guest_three_18", "role": "guest"},
    {"user_name": "user_four", "password": "user_four_19", "role": "user"},
    {"user_name": "guest_four", "password": "guest_four_20", "role": "guest"},
    {"user_name": "alex01", "password": "Pass1A", "role": "admin"},
    {"user_name": "maria02", "password": "Design2B", "role": "user"},
    {"user_name": "john03", "password": "Code3C", "role": "user"},
    {"user_name": "kate04", "password": "Data4D", "role": "moder"},
    {"user_name": "max_power", "password": "Build5E", "role": "user"},
    {"user_name": "kate_dev", "password": "Secure6F", "role": "user"},
    {"user_name": "johnny", "password": "Strong7G", "role": "user"},
    {"user_name": "olga08", "password": "Market8H", "role": "user"},
]
)

@pytest.mark.anyio
async def test_login(login_data, async_client_fix):
    """Testing '/login' endpoint output token, -> returns token"""

    as_client = async_client_fix
    response = await as_client.post("/login", json=login_data)
    assert response.status_code == 200
    resp_json = response.json()
    data = de_code(resp_json["token"])
    assert data.get("sub") == login_data.get("role")
    assert data.get("user_name") == login_data.get("user_name")
    assert login_data.get("user_name") in resp_json["message"]
#pytest test_.py::test_login     -> to start test



@pytest.mark.parametrize(
    "select_data",
    [
        {"role": "admin", "limit": 2},
        {"id": 1, "user_name": "admin_one", "title": "Admin task 1", "description": "System control",
         "completed": False, "role": "admin"},
        {"description": "Manage users", "role": "admin",},
        {"title": "Moder task 1", "role": "moder"},
        {"id": 4, "user_name": "moder_two", "title": "Moder task 2", "description": "Ban users", "completed": True,
         "role": "moder"},
        {"id": 5, "user_name": "user_one", "title": "User task 1", "description": "Create post", "completed": False,
         "role": "user"},
        {"title": "User task 2", "description": "Edit profile", "completed": True,
         "role": "user"},
        {"id": 7, "user_name": "guest_one", "title": "Guest task 1", "description": "Read only", "completed": False,
         "role": "guest"},
        {"user_name": "guest_two", "title": "Guest task 2", "description": "View content", "completed": True,
         "role": "guest"},
        {"role": "user"},
        {"id": 10, "user_name": "guest_three", "title": "Guest task 3", "description": "Browse site", "completed": True,
         "role": "guest"},
        {"id": 11},
        {"description": "Can moderate content", "completed": False, "role": "moder"},
        {"user_name": "user_one", "completed": False, "role": "user"},
        {"description": "Read only", "completed": True, "role": "guest"},
        {"title": "User task 2", "description": "Standard permissions", "completed": False, "role": "user"},
        {"id": 16, "user_name": "guest_two", "title": "Guest task 2", "description": "Limited access",
         "completed": False, "role": "guest"},
        {"id": 17},
        {"title": "Guest task 3", "description": "View only", "completed": False, "role": "guest"},
        {"completed": False, "role": "user", "limit": 3},
        {"completed": True, "role": "guest", "limit": 5},
    ]

)

@pytest.mark.anyio
async def test_select_data(select_data, async_client_fix):
    """Testing '/select' endpoint,
       loop is for the case when as output I get several dicts in list,
       -> returns list[dict, dict .....]
     """
    as_client = async_client_fix
    resp = await as_client.post("/select/", json=select_data)
    assert resp.status_code == 200
    data_resp = resp.json()

    if "er_code" not in data_resp:
        assert data_resp
        if "limit" in select_data:
            assert len(data_resp["data"]) <= select_data["limit"]

        for item in data_resp.get("data"):
            for field, value in select_data.items():
                if field == "limit":
                    continue

                assert field in item
                assert item[field] == value

    if "er_code" in data_resp:
        assert data_resp["er_code"] == "Empty response -> select"
        assert data_resp["message"] == "No data for your request"


#could be status_code 400 becouse i changed data in db so it could return nothing
#pytest test_.py::test_select_data -x     -> to start test


@pytest.mark.parametrize(
    "id",
    [5, 2, 4, 6, 7, 10, 12, 16, 1, 3])


@pytest.mark.anyio
async def test_delete(id, db_fix):
    """Sometimes it's better to test the 'main func of endpoint itself',
       here main func 'del_from_db' takes 2 args 'id' and 'session'
       and then deleting user with this id, if 'id' doesn't exist
       raises Error, so I don't accidentally delete some data from the base
       (even if its test one), so better to test func
       -> returns None 'just deleting'"""

    ses = db_fix
    user = ses.query(User).filter(User.id == id).first()
    assert user is not None
    del_from_db(ses, id)
    user = ses.query(User).filter(User.id == id).first()
    assert user is None
#pytest test_.py::test_delete -x      -> to start test

@pytest.mark.parametrize(
    "create_data",
    [
        {"user_name": "alex01", "password": "Pass1A", "title": "Manager", "description": "TeamLead", "completed": False,
         "role": "admin"},
        {"user_name": "maria02", "password": "Design2B", "title": "Designer", "description": "UiUxWork",
         "completed": True, "role": "user"},
        {"user_name": "john03", "password": "Code3C", "title": "Developer", "description": "Backend",
         "completed": False, "role": "user"},
        {"user_name": "kate04", "password": "Data4D", "title": "Analyst", "description": "DataProc", "completed": True,
         "role": "moder"},
        {"user_name": "mike05", "password": "Build5E", "title": "Engineer", "description": "Systems",
         "completed": False, "role": "user"},
        {"user_name": "lena06", "password": "Secure6F", "title": "Support", "description": "HelpDesk",
         "completed": True, "role": "user"},
        {"user_name": "ivan07", "password": "Strong7G", "title": "Tester", "description": "QaChecks",
         "completed": False, "role": "user"},
        {"user_name": "olga08", "password": "Market8H", "title": "Marketer", "description": "AdsPlan",
         "completed": True, "role": "user"},
        {"user_name": "peter09", "password": "Sales9I", "title": "Salesman", "description": "ClientOps",
         "completed": False, "role": "user"},
        {"user_name": "sara10", "password": "Write1J", "title": "Writer", "description": "Content", "completed": True,
         "role": "user"},
        {"user_name": "tom11", "password": "Admin2K", "title": "Operator", "description": "SysWork", "completed": False,
         "role": "admin"},
        {"user_name": "nina12", "password": "Plan3L", "title": "Planner", "description": "RoadMap", "completed": True,
         "role": "user"},
        {"user_name": "oleg13", "password": "Dev4M", "title": "Coder", "description": "ApiWork", "completed": False,
         "role": "user"},
        {"user_name": "rita14", "password": "Test5N", "title": "Reviewer", "description": "CheckIt", "completed": True,
         "role": "moder"},
        {"user_name": "dima15", "password": "Fix6O", "title": "Maintainer", "description": "BugFix", "completed": False}
    ])

@pytest.mark.anyio
async def test_create_data(admin_token, create_data, async_client_fix, db_fix):
    """Testing '/create' endpoint, token required["admin", "moder", "user"]
    -> returns created user dict"""
    as_client = async_client_fix
    ses = db_fix
    response = await as_client.post('/create', json=create_data, headers=admin_token)
    assert response.status_code == 201
    created_user_dict = response.json()["created_data"]
    user_obj_protected = ses.query(Protected).filter(Protected.id == created_user_dict["id"]).first()
    assert created_user_dict["user_name"] == create_data["user_name"]
    assert created_user_dict["role"] == create_data.get("role", "user")
    assert created_user_dict["title"] == create_data["title"]
    #Here testing Protected table with passwords
    assert user_obj_protected.id == created_user_dict["id"]
    assert user_obj_protected.role == created_user_dict["role"]
    assert user_obj_protected.user_name == created_user_dict["user_name"]
    assert verify_password(create_data["password"], user_obj_protected.password)  #verify_password(password, he_password)
#pytest test_.py::test_create_data -x  -> to start test


@pytest.mark.parametrize(
    "update_data, id",
    [
        ({"user_name": "alex_new"}, 11),
        ({"title": "Manager"}, 2),
        ({"description": "Updated desc"}, 34),
        ({"completed": True}, 48),
        ({"role": "admin"}, 12),

        ({"user_name": "maria22", "title": "Designer"}, 14),
        ({"description": "Short info", "completed": False}, 18),
        ({"role": "moderator", "title": "Lead"}, 16),
        ({"user_name": "johnny", "description": "Profile"}, 40),
        ({"completed": True, "role": "user"}, 36),

        ({"title": "Analyst", "description": "Data team"}, 37),
        ({"user_name": "kate_dev", "completed": False}, 39),
        ({"role": "user", "description": "Bio"}, 35),
        ({"user_name": "max_power", "title": "Engineer", "completed": True}, 38),
        ({"description": "Test update", "role": "admin"}, 12),
    ]
)

@pytest.mark.anyio
async def test_update(admin_token, async_client_fix, update_data, id, db_fix):
    """Testing '/update/{id}/' endpoint, token required["admin", "moder"]
    -> returns updated user dict"""
    as_client = async_client_fix
    ses = db_fix
    request = await as_client.patch(f"/update/{id}", json=update_data, headers=admin_token)
    assert request.status_code == 200
    user_obj = ses.query(User).where(User.id == id).first()
    protected_user_obj = ses.query(Protected).where(Protected.id == id).first()

    for field in update_data:
        if field in ["user_name", "role"]:  #no desc, or title in this table, so only those 2 could be updated
            assert getattr(protected_user_obj, field) == update_data[field]

        assert getattr(user_obj, field) == update_data[field]

#pytest test_.py::test_update -x    -> to start test




