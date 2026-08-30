from tests.conftest import create_issue,create_project

def test_create_issue_valid_returns_201(client,user_a):
    p=create_project(client,user_a);resp=client.post("/issues",json={"title":"Login bug","description":"cannot log in","priority":"High","status":"Todo","project_id":p["id"]},headers=user_a.headers);assert resp.status_code==201;body=resp.json();assert body["title"]=="Login bug";assert body["priority"]=="High";assert body["status"]=="Todo"

def test_create_issue_invalid_priority_returns_422(client,user_a):
    p=create_project(client,user_a);assert client.post("/issues",json={"title":"x","priority":"Urgent","project_id":p["id"]},headers=user_a.headers).status_code==422

def test_create_issue_invalid_status_returns_422(client,user_a):
    p=create_project(client,user_a);assert client.post("/issues",json={"title":"x","status":"Blocked","project_id":p["id"]},headers=user_a.headers).status_code==422

def test_owner_changes_status_updates_updated_at(client,user_a):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"],status="Todo");resp=client.patch(f"/issues/{issue['id']}",json={"status":"In Progress"},headers=user_a.headers);assert resp.status_code==200;assert resp.json()["status"]=="In Progress";assert resp.json()["updated_at"]>=issue["updated_at"]

def test_full_status_lifecycle(client,user_a):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"],status="Todo")
    for s in ("In Progress","Done"): resp=client.patch(f"/issues/{issue['id']}",json={"status":s},headers=user_a.headers);assert resp.status_code==200;assert resp.json()["status"]==s

def test_assign_issue_to_user(client,user_a,user_b):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"]);resp=client.patch(f"/issues/{issue['id']}",json={"assignee_id":user_b.id},headers=user_a.headers);assert resp.status_code==200;assert resp.json()["assignee_id"]==user_b.id

def test_assign_to_nonexistent_user_returns_404(client,user_a):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"]);assert client.patch(f"/issues/{issue['id']}",json={"assignee_id":999999},headers=user_a.headers).status_code==404

def test_delete_issue(client,user_a):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"]);assert client.delete(f"/issues/{issue['id']}",headers=user_a.headers).status_code==204;assert client.get(f"/issues/{issue['id']}",headers=user_a.headers).status_code==404

def test_create_issue_in_unowned_project_is_forbidden(client,user_a,user_b):
    p=create_project(client,user_a);assert client.post("/issues",json={"title":"intrusion","project_id":p["id"]},headers=user_b.headers).status_code==403
