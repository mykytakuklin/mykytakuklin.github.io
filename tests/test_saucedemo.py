import re

from playwright.sync_api import expect

STANDARD_USER = "standard_user"
LOCKED_OUT_USER = "locked_out_user"
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


def test_add_product_to_cart_updates_badge(logged_in_page):
    page = logged_in_page
    page.click("#add-to-cart-sauce-labs-backpack")
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")


def test_remove_product_from_cart(logged_in_page):
    page = logged_in_page
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click("#remove-sauce-labs-backpack")
    expect(page.locator(".shopping_cart_badge")).to_have_count(0)


def test_sort_products_price_low_to_high(logged_in_page):
    page = logged_in_page
    page.select_option("[data-test='product-sort-container']", "lohi")
    prices = page.locator(".inventory_item_price").all_text_contents()
    values = [float(p.replace("$", "")) for p in prices]
    assert values == sorted(values)


def test_complete_checkout_flow(logged_in_page):
    page = logged_in_page
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "Mykyta")
    page.fill("#last-name", "Kuklin")
    page.fill("#postal-code", "21000")
    page.click("#continue")
    page.click("#finish")
    expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")


def test_logout_returns_to_login_page(logged_in_page):
    page = logged_in_page
    page.click("#react-burger-menu-btn")
    page.click("#logout_sidebar_link")
    expect(page.locator("#login-button")).to_be_visible()
