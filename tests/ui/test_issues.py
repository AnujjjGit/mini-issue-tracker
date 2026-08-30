import uuid
from playwright.sync_api import expect

def _add_issue(page,title): page.get_by_placeholder("Title",exact=True).fill(title);page.get_by_role("button",name="Add issue").click()

def test_create_issue_appears_on_board(logged_in_page,project,frontend_url):
    page=logged_in_page;page.goto(f"{frontend_url}/projects/{project['id']}");expect(page.get_by_test_id("project-name")).to_be_visible();title=f"Issue {uuid.uuid4().hex[:6]}";_add_issue(page,title);expect(page.get_by_test_id("column-todo").get_by_text(title)).to_be_visible()

def test_change_status_moves_card_across_columns(logged_in_page,project,frontend_url):
    page=logged_in_page;page.goto(f"{frontend_url}/projects/{project['id']}");title=f"Issue {uuid.uuid4().hex[:6]}";_add_issue(page,title);expect(page.get_by_test_id("column-todo").get_by_text(title)).to_be_visible();card=page.locator(".issue-card",has_text=title);card.get_by_role("button",name="In Progress").click();expect(page.get_by_test_id("column-in-progress").get_by_text(title)).to_be_visible();expect(page.get_by_test_id("column-todo").get_by_text(title)).to_have_count(0)
