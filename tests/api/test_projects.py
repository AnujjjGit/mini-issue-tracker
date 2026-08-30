from tests.conftest import create_project

def test_list_projects_requires_auth(client): assert client.get("/projects").status_code==401

def test_create_project_sets_owner_to_caller(client,user_a):
    resp=client.post("/projects",json={"name":"Apollo","description":"first project"},headers=user_a.headers);assert resp.status_code==201;body=resp.json();assert body["name"]=="Apollo";assert body["owner_id"]==user_a.id;assert body["archived"] is False

def test_create_project_missing_name_returns_422(client,user_a): assert client.post("/projects",json={"description":"no name"},headers=user_a.headers).status_code==422

def test_owner_can_edit_project_name(client,user_a):
    project=create_project(client,user_a,name="Old Name");resp=client.patch(f"/projects/{project['id']}",json={"name":"New Name"},headers=user_a.headers);assert resp.status_code==200;assert resp.json()["name"]=="New Name";assert client.get(f"/projects/{project['id']}",headers=user_a.headers).json()["name"]=="New Name"

def test_list_returns_only_own_projects(client,user_a,user_b):
    create_project(client,user_a,name="A-project");create_project(client,user_b,name="B-project");assert {p["name"] for p in client.get("/projects",headers=user_a.headers).json()}=={"A-project"}

def test_duplicate_project_name_for_same_owner_returns_409(client,user_a):
    create_project(client,user_a,name="Dup");resp=client.post("/projects",json={"name":"Dup"},headers=user_a.headers);assert resp.status_code==409

def test_archive_is_non_destructive(client,user_a):
    project=create_project(client,user_a,name="ToArchive");archived=client.post(f"/projects/{project['id']}/archive",headers=user_a.headers);assert archived.status_code==200;assert archived.json()["archived"] is True;assert all(p["id"]!=project["id"] for p in client.get("/projects",headers=user_a.headers).json());assert client.get(f"/projects/{project['id']}",headers=user_a.headers).status_code==200
