import os
import uuid
from dataclasses import dataclass

os.environ.setdefault("DATABASE_URL", "sqlite://")

import app.models  # noqa: E402,F401
import pytest  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

@pytest.fixture()
def db_engine():
    test_db_url=os.environ.get("TEST_DATABASE_URL")
    if test_db_url: engine=create_engine(test_db_url)
    else: engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine);engine.dispose()

@pytest.fixture()
def TestingSessionLocal(db_engine): return sessionmaker(bind=db_engine,autoflush=False,autocommit=False)

@pytest.fixture()
def client(db_engine,TestingSessionLocal):
    def override_get_db():
        db=TestingSessionLocal()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db]=override_get_db
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()

@pytest.fixture()
def db_session(TestingSessionLocal)->Session:
    db=TestingSessionLocal()
    try: yield db
    finally: db.close()

@dataclass
class UserCtx:
    id:int;name:str;email:str;password:str;token:str
    @property
    def headers(self)->dict: return {"Authorization":f"Bearer {self.token}"}

@pytest.fixture()
def make_user(client):
    def _make(password="password123",name="Test User"):
        email=f"user_{uuid.uuid4().hex[:12]}@example.com"
        reg=client.post("/auth/register",json={"name":name,"email":email,"password":password});assert reg.status_code==201,reg.text
        user_id=reg.json()["id"]
        login=client.post("/auth/login",json={"email":email,"password":password});assert login.status_code==200,login.text
        return UserCtx(id=user_id,name=name,email=email,password=password,token=login.json()["access_token"])
    return _make

@pytest.fixture()
def user_a(make_user): return make_user(name="Alice")
@pytest.fixture()
def user_b(make_user): return make_user(name="Bob")

def create_project(client,user,name="Project X",description=None):
    resp=client.post("/projects",json={"name":name,"description":description},headers=user.headers);assert resp.status_code==201,resp.text;return resp.json()

def create_issue(client,user,project_id,**overrides):
    body={"title":"Sample issue","priority":"Medium","status":"Todo","project_id":project_id};body.update(overrides)
    resp=client.post("/issues",json=body,headers=user.headers);assert resp.status_code==201,resp.text;return resp.json()
