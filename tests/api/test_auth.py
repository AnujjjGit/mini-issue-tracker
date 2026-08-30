import uuid

def _unique_email(): return f"user_{uuid.uuid4().hex[:12]}@example.com"

def test_register_valid_returns_201(client):
    email=_unique_email();resp=client.post("/auth/register",json={"name":"Alice","email":email,"password":"password123"});assert resp.status_code==201;body=resp.json();assert body["email"]==email;assert body["name"]=="Alice";assert "id" in body;assert "password" not in body;assert "hashed_password" not in body

def test_register_invalid_email_returns_422(client):
    assert client.post("/auth/register",json={"name":"X","email":"not-an-email","password":"password123"}).status_code==422

def test_register_short_password_returns_422(client):
    assert client.post("/auth/register",json={"name":"X","email":_unique_email(),"password":"short"}).status_code==422

def test_register_duplicate_email_returns_409(client):
    email=_unique_email();assert client.post("/auth/register",json={"name":"A","email":email,"password":"password123"}).status_code==201;dup=client.post("/auth/register",json={"name":"B","email":email,"password":"password123"});assert dup.status_code==409;assert dup.json()["error"]=="Email already registered"

def test_password_is_stored_hashed_not_plaintext(client,db_session):
    from app.models import User
    email=_unique_email();password="supersecret123";assert client.post("/auth/register",json={"name":"Hash","email":email,"password":password}).status_code==201;user=db_session.query(User).filter(User.email==email).first();assert user.hashed_password!=password;assert user.hashed_password.startswith("$2");assert len(user.hashed_password)>=60

def test_login_valid_returns_token(client,make_user):
    user=make_user();resp=client.post("/auth/login",json={"email":user.email,"password":user.password});assert resp.status_code==200;assert resp.json()["token_type"]=="bearer";assert resp.json()["access_token"].count(".")==2

def test_login_wrong_password_returns_401(client,make_user):
    user=make_user();assert client.post("/auth/login",json={"email":user.email,"password":"wrong-password"}).status_code==401

def test_login_unknown_email_returns_401_without_enumeration(client,make_user):
    user=make_user();wrong=client.post("/auth/login",json={"email":user.email,"password":"wrong-password"});unknown=client.post("/auth/login",json={"email":_unique_email(),"password":"password123"});assert wrong.status_code==401;assert unknown.status_code==401;assert wrong.json()==unknown.json()

def test_logout_requires_auth_and_succeeds(client,user_a):
    assert client.post("/auth/logout").status_code==401;assert client.post("/auth/logout",headers=user_a.headers).status_code==200
