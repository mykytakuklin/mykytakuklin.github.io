from playwright.sync_api import expect


def test_logout_returns_to_login_page(logged_in_page):
    page = logged_in_page
    page.click("#react-burger-menu-btn")
    page.click("#logout_sidebar_link")
    expect(page.locator("#login-button")).to_be_visible()


def test_reset_app_state_clears_cart(logged_in_page):
    page = logged_in_page
    page.locator(".inventory_item").first.locator("button").click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")

    page.click("#react-burger-menu-btn")
    page.click("#reset_sidebar_link")

    expect(page.locator(".shopping_cart_badge")).to_have_count(0)
