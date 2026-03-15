import pytest
from sql.db import session
from tests.fixtures_test import async_client_fix, admin_token, db_fix, user_token
from main_app.jwt_auth import de_code, verify_password, get_token_from_header
from sql.models import User, Protected  #table models
from sql.mine_sql_functions import del_from_db
api_url = "http://127.0.0.1:8000"

@pytest.mark.parametrize(
    "login_data",
    [
        {"user_name": "adm_one", "password": "admin123"},
        {"user_name": "adm", "password": "admin456"},
        {"user_name": "moder_one", "password": "moder123"},
        {"user_name": "moder_two", "password": "moder4"},
        {"user_name": "user_one", "password": "user123"},
        {"user_name": "us_two", "password": "user46"},
        {"user_name": "guest_one", "password": "gues23"},
        {"user_name": "gue_two", "password": "gues56"},
        {"user_name": "user_tee", "password": "user789"},
        {"user_name": "gue_three", "password": "guest789"},
        {"user_name": "admi_one", "password": "admin_one_11"},
        {"user_name": "moder_oe", "password": "moer_one_12"},
        {"user_name": "user_one", "password": "user_oe_13"},
        {"user_name": "gust_ne", "password": "guestne_14"},
        {"user_name": "user_wo", "password": "user_wo_15"},
    ]
)

@pytest.mark.anyio
async def test_login_ex(login_data, async_client_fix):
    """Testing '/login' endpoint with wrong data  -> raises code [404, 401]"""

    as_client = async_client_fix
    response = await as_client.post("/login", json=login_data)
    assert response.status_code in [404, 401]
    resp_json = response.json()
    if response.status_code == 404:
       assert resp_json["message"] == "Please, check spelling of your input"
       assert resp_json["detail"] == "User_name wasn't found in the base"

    if response.status_code == 401:
        assert resp_json["message"] == "Authorization failed"
#pytest test_exceptions.py::test_login_ex   ->   to start test



@pytest.mark.parametrize(
    "select_data",
    [
        {"user_name": "ghost_user_001"},
        {"id": 102, "user_name": "unknown_admin"},
        {"id": 103, "user_name": "deleted_user", "role": "user", "completed": 0, "description": "Removed info",
         "title": "Old record"},
        {"id": 104, "user_name": "no_such_moder", "role": "moder", "completed": 0, "description": "Missing task",
         "title": "Moderation X"},
        {"title": "Random title"},
        {"id": 106, "user_name": "void_account", "role": "admin", "completed": 0, "description": "Nothing here",
         "title": "Empty profile"},
        {"id": 107, "user_name": "fake_profile", "role": "user", "completed": 1,
         "description": "Fake description with extra info", "title": "Fake task"},
        {"user_name": "null_user_case", "description": "Null description",
         "title": "Null title"},
        {"id": 109, "user_name": "test_absent_1", "role": "user", "completed": 0, "description": "Test desc A",
         "title": "Test title A"},
        {"description": "Test desc B with extra", "title": "Test title B"},
        {"id": 111, "user_name": "phantom_admin", "role": "admin", "completed": 0,
         "description": "Invisible admin data", "title": "Phantom Admin"},
        {"id": 112, "user_name": "lost_moderator", "role": "moder", "completed": 1, "description": "Moderation lost",
         "title": "Lost Moderator"},
        {"id": 113, "user_name": "ghost_guest", "role": "guest"},
        {"id": 114, "user_name": "void_user", "role": "user", "completed": 1, "description": "Void description",
         "title": "Void Title"},
        {"user_name": "absent_profile", "description": "Profile not found",
         "title": "Absent Profile"},
    ]
)

@pytest.mark.anyio
async def test_select_data_ex(select_data, async_client_fix):
    """Testing '/select' endpoint, -> returns None
     """
    as_client = async_client_fix
    resp = await as_client.post("/select/", json=select_data)
    assert resp.status_code == 400
    data_resp = resp.json()
    assert data_resp["message"] == "No data for your request"
    assert data_resp["detail"] == "Nothing was found in the base"
#pytest test_exceptions.py::test_select_data_ex    ->   to start test



@pytest.mark.parametrize(
    "id, role",[
    (130, {"user_name": "admin_two", "password": "admin456"}),
    (290, {"user_name": "guest_three", "password": "guest_three_18"}),
    (370, {"user_name": "admin_two", "password": "admin456"}),
    (730, {"user_name": "admin_two", "password": "admin456"}),
    (450, {"user_name": "guest_three", "password": "guest_three_18"}),
    (337, {"user_name": "admin_two", "password": "admin456"}),
    (630, {"user_name": "admin_two", "password": "admin456"}),
    (450, {"user_name": "guest_three", "password": "guest_three_18"}),
    (130, {"user_name": "admin_two", "password": "admin456"}),
    (380, {"user_name": "admin_two", "password": "admin456"})])


@pytest.mark.anyio
async def test_delete_ex(id, async_client_fix, role):
    """Testing '/delete/{id}' endpoint, token required, -> returns code 404'"""
    as_client = async_client_fix
    login_req = await as_client.post("/login", json=role)
    token = login_req.json()["token"]
    request = await as_client.delete(f"/delete/{id}", headers={"Authorization": f"Bearer {token}"})

    assert request.status_code in [404, 403]
    resp_json = request.json()

    if request.status_code == 404:
        assert resp_json["message"] == "id doesn't exist"

    if request.status_code == 403:
        assert resp_json["detail"] == "Not enough permissions"
#pytest test_exceptions.py::test_delete_ex    -> to start test




@pytest.mark.parametrize(
    "create_data, login_data",
    [
        (
            {"user": "user_two", "title": "User task 2", "description": "Standard permissions", "completed": 0, "role": "user", "password": "a9k2m1"},
            {"user_name": "guest_four", "password": "guest_four_20"}
        ),
        (
            {"user": "guest_two", "title": "Lead", "description": "Limited access", "completed": 0, "role": "moderator", "password": "q3w8e1"},
            {"user_name": "guest_three", "password": "guest_three_18"}
        ),
        (
            {"user": "user_three", "title": "User task 3", "description": "Basic workflow", "completed": 1, "role": "user", "password": "z7x2c4"},
            {"user_name": "guest_four", "password": "guest_four_20"}
        ),
        (
            {"user": "guest_three", "title": "Guest task 3", "description": "Short info", "completed": 0, "role": "guest", "password": "p0l9k8"},
            {"user_name": "guest_three", "password": "guest_three_18"}
        ),
        (
            {"user": "user_four", "title": "User task 4", "description": "Normal user access", "completed": 0, "role": "user", "password": "m5n2b7"},
            {"user_name": "guest_four", "password": "guest_four_20"}
        ),
        (
            {"user": "guest_four", "title": "Guest task 4", "description": "Read-only mode", "completed": 1, "role": "guest", "password": "t6y1u3"},
            {"user_name": "guest_three", "password": "guest_three_18"}
        ),
        (
            {"user": "alex01", "title": "Manager", "description": "Updated desc", "completed": 0, "role": "admin", "password": "admin123"},
            {"user_name": "guest_four", "password": "guest_four_20"}
        ),
        (
            {"user": "neo_user1", "title": "Research", "description": "New workflow", "completed": 0, "role": "user", "password": "r4s8d2"},
            {"user_name": "guest_three", "password": "guest_three_18"}
        ),
        (
            {"user": "temp_guest7", "title": "Temp task", "description": "External access", "completed": 1, "role": "guest", "password": "g7h3j1"},
            {"user_name": "guest_four", "password": "guest_four_20"}
        ),
        (
            {"user": "alpha_dev", "title": "DevOps", "description": "Pipeline", "completed": 1, "role": "user", "password": "dev456"},
            {"user_name": "guest_three", "password": "guest_three_18"}


        ),#correct test but creating a new data with admin as role with user token
        (   {"user": "Some_dude", "title": "DevOps", "description": "Pipeline", "completed": 1, "role": "admin", "password": "deVA456"},
            {"user_name": "guest_three", "password": "guest_three_18"}
        ),
        (   {"user": "Lol_hdkc", "title": "DevOps", "description": "Pipeline", "completed": 1, "role": "admin", "password": "Oh_god34A"},
            {"user_name": "guest_three", "password": "guest_three_18"}
        )
    ]
)

@pytest.mark.anyio
async def test_create_data_ex(async_client_fix, create_data, login_data):
    as_client = async_client_fix
    login_req = await as_client.post("/login", json=login_data)
    token = login_req.json()["token"]

    create_req = await as_client.post("/create", json=create_data, headers=token)
    create_resp_json = create_req.json()
    assert create_req.status_code in [400, 403, 401]

    if create_req.status_code == 400:
        assert create_resp_json["message"] == "user_name already exists"

    if create_req.status_code == 401:
        assert create_resp_json["message"] == "Password is unsafe, please use numbers, and high register letters"

    if create_req.status_code == 403 and create_resp_json["er_code"] == "Role creating -> create":
        assert create_resp_json["message"] == "You can't create role 'admin' or 'moder', if you are 'user'"

    elif create_req.status_code == 403 and create_resp_json["er_code"] == "Not enter to endpoint -> auth token":
        assert create_resp_json["detail"] == "Not enough permissions"





















