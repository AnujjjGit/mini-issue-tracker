from tests.conftest import create_issue,create_project

def _seed(client,user,pid):
    create_issue(client,user,pid,title="Alpha",status="Todo",priority="Low");create_issue(client,user,pid,title="Beta",status="Done",priority="High");create_issue(client,user,pid,title="Gamma",status="Done",priority="Low");create_issue(client,user,pid,title="Delta",status="In Progress",priority="High")

def test_filter_by_status(client,user_a):
    p=create_project(client,user_a);_seed(client,user_a,p["id"]);assert {i["title"] for i in client.get("/issues",params={"status_filter":"Done"},headers=user_a.headers).json()}=={"Beta","Gamma"}

def test_filter_by_priority(client,user_a):
    p=create_project(client,user_a);_seed(client,user_a,p["id"]);assert {i["title"] for i in client.get("/issues",params={"priority":"High"},headers=user_a.headers).json()}=={"Beta","Delta"}

def test_search_by_title(client,user_a):
    p=create_project(client,user_a);_seed(client,user_a,p["id"]);assert {i["title"] for i in client.get("/issues",params={"search":"amm"},headers=user_a.headers).json()}=={"Gamma"}

def test_search_is_case_insensitive(client,user_a):
    p=create_project(client,user_a);_seed(client,user_a,p["id"]);assert {i["title"] for i in client.get("/issues",params={"search":"ALPHA"},headers=user_a.headers).json()}=={"Alpha"}

def test_combined_status_and_priority_filter(client,user_a):
    p=create_project(client,user_a);_seed(client,user_a,p["id"]);resp=client.get("/issues",params={"status_filter":"Done","priority":"High"},headers=user_a.headers);assert resp.status_code==200;assert {i["title"] for i in resp.json()}=={"Beta"}

def test_filter_by_assignee(client,user_a,user_b):
    p=create_project(client,user_a);unassigned=create_issue(client,user_a,p["id"],title="Unassigned");assigned=create_issue(client,user_a,p["id"],title="Assigned");client.patch(f"/issues/{assigned['id']}",json={"assignee_id":user_b.id},headers=user_a.headers);titles={i["title"] for i in client.get("/issues",params={"assignee_id":user_b.id},headers=user_a.headers).json()};assert titles=={"Assigned"};assert unassigned["title"] not in titles

def test_search_returns_only_own_issues(client,user_a,user_b):
    pa=create_project(client,user_a);create_issue(client,user_a,pa["id"],title="Shared Name");pb=create_project(client,user_b);create_issue(client,user_b,pb["id"],title="Shared Name");results=client.get("/issues",params={"search":"Shared"},headers=user_a.headers).json();assert len(results)==1;assert results[0]["project_id"]==pa["id"]

def test_no_filters_returns_all_own_issues(client,user_a):
    p=create_project(client,user_a);_seed(client,user_a,p["id"]);assert len(client.get("/issues",headers=user_a.headers).json())==4
