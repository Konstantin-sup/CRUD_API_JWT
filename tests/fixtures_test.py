import pytest
from httpx import ASGITransport, AsyncClient
from main_app.main_file import app
from sqlalchemy.orm import Session
from sql.db import engine
api_url = "http://127.0.0.1:8000"

@pytest.fixture
def db_fix():
    connection = engine.connect()
    session = Session(bind=connection)

    try:
        yield session

    finally:

        session.rollback()
        session.close()
        connection.close()


@pytest.fixture
async def async_client_fix():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=api_url) as async_client:
        yield async_client


@pytest.fixture  #returns token with admin as sub
async def admin_token(async_client_fix):
    as_client = async_client_fix

    response = await as_client.post("/login", json={"user_name": "admin_two", "password": "admin456"})
    resp_json = response.json()

    return {"Authorization": f"Bearer {resp_json['token']}"}


@pytest.fixture  #returns token with user as sub
async def user_token(async_client_fix):
    as_client = async_client_fix

    response = await as_client.post("/login", json={"user_name": "guest_three", "password": "guest_three_18"})
    resp_json = response.json()

    return {"Authorization": f"Bearer {resp_json['token']}"}


@pytest.fixture  #returns token with guest as sub
async def guest_token(async_client_fix):
    as_client = async_client_fix

    response = await as_client.post("/login", json={"user_name": "guest_four", "password": "guest_four_20"})
    resp_json = response.json()

    return {"Authorization": f"Bearer {resp_json['token']}"}


