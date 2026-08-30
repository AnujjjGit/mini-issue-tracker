import re
from playwright.sync_api import expect

def test_valid_login_loads_dashboard(page,api_user,frontend_url):
    page.goto(f"{frontend_url}/login");page.get_by_label("Email").fill(api_user["email"]);page.get_by_label("Password").fill(api_user["password"]);page.get_by_role("button",name="Log in").click();expect(page.get_by_role("heading",name="Dashboard")).to_be_visible();expect(page.get_by_test_id("current-user")).to_have_text(api_user["email"])

def test_invalid_login_shows_error_and_stays(page,api_user,frontend_url):
    page.goto(f"{frontend_url}/login");page.get_by_label("Email").fill(api_user["email"]);page.get_by_label("Password").fill("definitely-wrong");page.get_by_role("button",name="Log in").click();expect(page.get_by_test_id("login-error")).to_be_visible();expect(page).to_have_url(re.compile(r"/login$"))
