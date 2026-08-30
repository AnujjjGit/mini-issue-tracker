import uuid
from playwright.sync_api import expect

def test_create_project_appears_in_list(logged_in_page):
    page=logged_in_page;expect(page.get_by_role("heading",name="Dashboard")).to_be_visible();name=f"Project {uuid.uuid4().hex[:6]}";page.get_by_placeholder("Project name").fill(name);page.get_by_role("button",name="Add project").click();expect(page.get_by_test_id("project-list").get_by_text(name)).to_be_visible()
