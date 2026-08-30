from tests.conftest import create_issue,create_project

def test_tampered_jwt_returns_401(client,user_a):
    tampered=user_a.token[:-3]+("abc" if not user_a.token.endswith("abc") else "xyz");assert client.get("/projects",headers={"Authorization":f"Bearer {tampered}"}).status_code==401

def test_garbage_token_returns_401(client): assert client.get("/projects",headers={"Authorization":"Bearer not.a.realjwt"}).status_code==401

def test_missing_token_returns_401(client): assert client.get("/projects").status_code==401 and client.get("/issues").status_code==401

def test_token_signed_with_wrong_secret_returns_401(client,user_a):
    import jwt
    forged=jwt.encode({"sub":str(user_a.id)},"a-different-secret-of-sufficient-length-32b",algorithm="HS256");assert client.get("/projects",headers={"Authorization":f"Bearer {forged}"}).status_code==401

def test_userb_cannot_edit_useras_project(client,user_a,user_b):
    p=create_project(client,user_a,name="A-owned");assert client.patch(f"/projects/{p['id']}",json={"name":"hijacked"},headers=user_b.headers).status_code==403;assert client.get(f"/projects/{p['id']}",headers=user_a.headers).json()["name"]=="A-owned"

def test_userb_cannot_archive_useras_project(client,user_a,user_b):
    p=create_project(client,user_a);assert client.post(f"/projects/{p['id']}/archive",headers=user_b.headers).status_code==403

def test_userb_cannot_update_useras_issue(client,user_a,user_b):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"],status="Todo");assert client.patch(f"/issues/{issue['id']}",json={"status":"Done"},headers=user_b.headers).status_code==403;assert client.get(f"/issues/{issue['id']}",headers=user_a.headers).json()["status"]=="Todo"

def test_userb_cannot_delete_useras_issue(client,user_a,user_b):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"]);assert client.delete(f"/issues/{issue['id']}",headers=user_b.headers).status_code==403;assert client.get(f"/issues/{issue['id']}",headers=user_a.headers).status_code==200

def test_userb_cannot_read_useras_issue(client,user_a,user_b):
    p=create_project(client,user_a);issue=create_issue(client,user_a,p["id"]);assert client.get(f"/issues/{issue['id']}",headers=user_b.headers).status_code==403

def test_sql_injection_in_search_is_neutralized(client,user_a):
    p=create_project(client,user_a);create_issue(client,user_a,p["id"],title="Real issue one");create_issue(client,user_a,p["id"],title="Real issue two");resp=client.get("/issues",params={"search":"' OR 1=1--"},headers=user_a.headers);assert resp.status_code==200;assert resp.json()==[]

def test_sql_injection_drop_table_payload_is_harmless(client,user_a):
    p=create_project(client,user_a);create_issue(client,user_a,p["id"],title="Keep me");assert client.get("/issues",params={"search":"'; DROP TABLE issues;--"},headers=user_a.headers).json()==[];survivors=client.get("/issues",headers=user_a.headers).json();assert len(survivors)==1;assert survivors[0]["title"]=="Keep me"

def test_search_matches_literal_substring(client,user_a):
    p=create_project(client,user_a);create_issue(client,user_a,p["id"],title="Payment gateway error");create_issue(client,user_a,p["id"],title="Login bug");titles=[i["title"] for i in client.get("/issues",params={"search":"gateway"},headers=user_a.headers).json()];assert titles==["Payment gateway error"]
