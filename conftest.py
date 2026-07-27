import pytest

STANDARD_USER = "standard_user"
PASSWORD = "secret_sauce"


@pytest.fixture
def logged_in_page(page):
    page.goto("/")
    page.fill("#user-name", STANDARD_USER)
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    page.wait_for_url("**/inventory.html")
    return page
