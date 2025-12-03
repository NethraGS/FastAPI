from TodoApp.database import SessionLocal
from .utils import *
from ..routers.auth import get_current_user, get_db,authenticate_user,create_access_token,SECRET_KEY,ALGORITHM
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException
app.dependency_overrides[get_db]=override_get_db

def test_authenticate_user(test_user):
    db=TestingSessionLocal()

    authenticated_user=authenticate_user(test_user.username,'neo',db)
    assert authenticated_user is not None
    assert authenticated_user.username==test_user.username
    non_existent_user=authenticate_user('wrongusername','test',db)
    assert non_existent_user is False

    wrong_password_user=authenticate_user(test_user.username,'wrongpassword',db)
    assert wrong_password_user is False

def test_create_access_token():
    username='testuser'
    user_id=1
    role='user'
    expires_delta=timedelta(days=1)

    token=create_access_token(username,user_id,role,expires_delta)
    decoded_token=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM],options={'verify_signature':False})
    assert decoded_token['sub']==username
    assert decoded_token['id']==user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_user):
    encode = {'sub': test_user.username, 'id': test_user.id, 'role': test_user.role}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    db = TestingSessionLocal()

    user = await get_current_user(token=token, db=db)

    assert user == {
        'username': test_user.username,
        'id': test_user.id,
        'user_role': test_user.role
    }

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}  
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    db = TestingSessionLocal()

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token, db=db) 

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Invalid credentials'
