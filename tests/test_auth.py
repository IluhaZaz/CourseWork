from httpx import AsyncClient
from json import loads

from conftest import ac, test_async_session_maker
from src.main import User



async def test_register(ac: AsyncClient):
    res = await ac.post(url="http://localhost:7000/auth/register", json={
                    "email": "user@example.com",
                    "password": "string",
                    "is_active": True,
                    "is_superuser": False,
                    "is_verified": False,
                    "username": "string"
                    }
                )
    global user_id
    user_id = loads(res.content.decode(encoding="utf-8"))["id"]
    assert res.status_code == 201


async def test_login(ac: AsyncClient):
    res = await ac.post(url="http://localhost:7000/auth/login", data={
            "username":"user@example.com", "password":"string"
            }
    )
    assert res.status_code == 200


async def test_make_verified():
    async with test_async_session_maker() as session:
        res = await session.get(User, user_id)
        res.is_verified = True
        await session.commit()