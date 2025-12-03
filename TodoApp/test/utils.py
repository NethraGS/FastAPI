from sqlalchemy import StaticPool, create_engine, text
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
from ..database import Base
from sqlalchemy.orm import sessionmaker
from ..main import app
from fastapi.testclient import TestClient
import pytest
from ..models import Todo, Users as User
from ..routers.auth import bcrypt_context
engine= create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username':'neo','id':1,'user_role':'admin'}

client=TestClient(app)
@pytest.fixture
def test_todo():
    todo=Todo(
        title="fastapi",
        description="fastapi",
        priority=5,
        complete=False,
        owner_id=1
    )

    db=TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("Delete from todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    hashed_password=bcrypt_context.hash("matrix")
    user=User(
        username="neo",
        email="string",
        first_name="string",
        last_name="string",
        hashed_password=bcrypt_context.hash("neo"),
        role="admin",
        phone_number="90980089"   
    )
    db=TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("Delete from users;"))
        connection.commit()
