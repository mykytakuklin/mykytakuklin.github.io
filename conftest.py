import base64

import pytest
from pytest_html import extras

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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extras", [])

    if report.when == "call":
        page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
        if page:
            try:
                screenshot = base64.b64encode(page.screenshot()).decode("ascii")
                extra.append(extras.image(screenshot, mime_type="image/png"))
            except Exception:
                pass

    report.extras = extra
