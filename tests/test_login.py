import re

from playwright.sync_api import expect

STANDARD_USER = "standard_user"
LOCKED_OUT_USER = "locked_out_user"
PROBLEM_USER = "problem_user"
PERFORMANCE_GLITCH_USER = "performance_glitch_user"
PASSWORD = "secret_sauce"


def test_login_with_valid_credentials(page):
    page.goto("/")
    page.fill("#user-name", STANDARD_USER)
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    expect(page).to_have_url(re.compile(r".*inventory\.html"))
    expect(page.locator(".title")).to_have_text("Products")


def test_login_locked_out_user_shows_error(page):
    page.goto("/")
    page.fill("#user-name", LOCKED_OUT_USER)
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    expect(page.locator("[data-test='error']")).to_contain_text("locked out")


def test_login_with_wrong_password_shows_error(page):
    page.goto("/")
    page.fill("#user-name", STANDARD_USER)
    page.fill("#password", "wrong-password")
    page.click("#login-button")
    expect(page.locator("[data-test='error']")).to_contain_text("do not match")


def test_login_with_empty_username_shows_error(page):
    page.goto("/")
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    expect(page.locator("[data-test='error']")).to_contain_text("Username is required")


def test_login_with_empty_password_shows_error(page):
    page.goto("/")
    page.fill("#user-name", STANDARD_USER)
    page.click("#login-button")
    expect(page.locator("[data-test='error']")).to_contain_text("Password is required")


def test_login_problem_user_can_log_in(page):
    page.goto("/")
    page.fill("#user-name", PROBLEM_USER)
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    expect(page).to_have_url(re.compile(r".*inventory\.html"))


def test_login_performance_glitch_user_can_log_in(page):
    page.goto("/")
    page.fill("#user-name", PERFORMANCE_GLITCH_USER)
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    expect(page).to_have_url(re.compile(r".*inventory\.html"), timeout=10000)
