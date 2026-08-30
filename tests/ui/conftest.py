import os,uuid
import httpx,pytest
API_URL=os.environ.get("API_URL","http://127.0.0.1:8000");FRONTEND_URL=os.environ.get("FRONTEND_URL","http://127.0.0.1:5173")
@pytest.fixture()
def frontend_url(): return FRONTEND_URL
@pytest.fixture()
def api_user():
    email=f"ui_{uuid.uuid4().hex[:12]}@example.com";password="password123";name="UI Tester"
    with httpx.Client(base_url=API_URL,timeout=15) as c:
        reg=c.post("/auth/register",json={"name":name,"email":email,"password":password});assert reg.status_code==201,reg.text;user_id=reg.json()["id"];login=c.post("/auth/login",json={"email":email,"password":password});assert login.status_code==200,login.text;token=login.json()["access_token"]
    return {"id":user_id,"name":name,"email":email,"password":password,"token":token}
@pytest.fixture()
def project(api_user):
    with httpx.Client(base_url=API_URL,timeout=15,headers={"Authorization":f"Bearer {api_user['token']}"}) as c:
        resp=c.post("/projects",json={"name":f"UI Project {uuid.uuid4().hex[:6]}","description":"ui test"});assert resp.status_code==201,resp.text;return resp.json()
@pytest.fixture()
def logged_in_page(page,api_user,frontend_url):
    page.add_init_script(f"window.localStorage.setItem('token', {api_user['token']!r});window.localStorage.setItem('email', {api_user['email']!r});");page.goto(f"{frontend_url}/");return page
