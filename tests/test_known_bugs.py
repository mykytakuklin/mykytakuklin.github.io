"""
Approach: SauceDemo ships several "broken" demo personas on purpose
(error_user, visual_user, problem_user). Rather than asserting the
"correct" behavior (which would FAIL against these personas and turn
the live dashboard red for a bug that isn't ours to fix), each test
here pins down the CURRENT known-buggy behavior. The test stays green
as long as the practice site's seeded bug keeps reproducing; it would
only go red if SauceDemo changed that persona's behavior - which is
itself useful signal, not noise.

All 12 bugs below were confirmed live against https://www.saucedemo.com/
before drafting these tests. Two things were checked and explicitly
ruled OUT as bugs (not included as tests): the hamburger menu's closed
position/open panel are identical for visual_user and standard_user
(the visible glitch is the icon's own rotation, see bug #7, not its
position); visual_user's cart-page price is stable on reload (the
price-instability bug is isolated to the inventory listing page).
"""

import re

from playwright.sync_api import expect

STANDARD_USER = "standard_user"
ERROR_USER = "error_user"
VISUAL_USER = "visual_user"
PROBLEM_USER = "problem_user"
PASSWORD = "secret_sauce"


def login_as(page, username):
    page.goto("/")
    page.fill("#user-name", username)
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    page.wait_for_url("**/inventory.html")


def add_first_item_to_cart(page):
    page.locator(".inventory_item").first.locator("button").click()


# ==== error_user (3 known bugs) ====

def test_known_bug_error_user_price_sort_is_broken(page):
    login_as(page, ERROR_USER)
    page.select_option("[data-test='product-sort-container']", "lohi")
    prices = [float(p.replace("$", "")) for p in page.locator(".inventory_item_price").all_text_contents()]
    assert prices != sorted(prices), "error_user's low-to-high sort is expected to be broken (seeded demo bug)"


def test_known_bug_error_user_cannot_remove_item_from_cart(page):
    login_as(page, ERROR_USER)
    btn = page.locator(".inventory_item").first.locator("button")
    btn.click()
    btn.click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("1"), "error_user's Remove button is expected to not actually remove the item (seeded demo bug)"


def test_known_bug_error_user_checkout_skips_last_name_validation(page):
    login_as(page, ERROR_USER)
    add_first_item_to_cart(page)
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "Mykyta")
    page.fill("#last-name", "Kuklin")
    page.fill("#postal-code", "21000")
    assert page.input_value("#last-name") == "", "error_user's Last Name field is expected to reject typed input (seeded demo bug)"
    page.click("#continue")
    expect(page).to_have_url(re.compile(r".*checkout-step-two\.html")), "error_user is expected to bypass Last Name validation and proceed anyway (seeded demo bug)"


# ==== visual_user (4 known bugs) ====

def test_known_bug_visual_user_shows_wrong_product_image(page):
    login_as(page, VISUAL_USER)
    backpack_src = page.locator(".inventory_item", has_text="Sauce Labs Backpack").locator("img").get_attribute("src")
    assert "sl-404" in backpack_src, "visual_user is expected to show a placeholder image for the backpack (seeded demo bug)"


def test_known_bug_visual_user_inventory_prices_are_unstable_on_reload(page):
    login_as(page, VISUAL_USER)
    prices_before = page.locator(".inventory_item_price").all_text_contents()
    page.reload()
    page.wait_for_selector(".inventory_item_price")
    prices_after = page.locator(".inventory_item_price").all_text_contents()
    assert prices_before != prices_after, "visual_user's inventory prices are expected to randomize on every reload (seeded demo bug)"


def test_known_bug_visual_user_cart_icon_is_mispositioned(page):
    login_as(page, VISUAL_USER)
    cart_box = page.locator(".shopping_cart_link").bounding_box()
    assert cart_box["x"] < 1100, "visual_user's cart icon is expected to render shifted left of its normal x≈1205 position (seeded demo bug)"


def test_known_bug_visual_user_burger_icon_has_visual_failure_class(page):
    login_as(page, VISUAL_USER)
    icon_class = page.locator(".bm-icon").get_attribute("class")
    assert "visual_failure" in icon_class, "visual_user's menu icon is expected to carry the 'visual_failure' class that tilts it (seeded demo bug)"


# ==== problem_user (5 known bugs) ====

def test_known_bug_problem_user_all_product_images_are_identical(page):
    login_as(page, PROBLEM_USER)
    srcs = page.locator(".inventory_item img").evaluate_all("els => els.map(e => e.getAttribute('src'))")
    assert len(set(srcs)) == 1, "problem_user is expected to show the same placeholder image for every product (seeded demo bug)"


def test_known_bug_problem_user_price_sort_is_broken(page):
    login_as(page, PROBLEM_USER)
    page.select_option("[data-test='product-sort-container']", "lohi")
    prices = [float(p.replace("$", "")) for p in page.locator(".inventory_item_price").all_text_contents()]
    assert prices != sorted(prices), "problem_user's low-to-high sort is expected to be broken (seeded demo bug)"


def test_known_bug_problem_user_cannot_remove_item_from_cart(page):
    login_as(page, PROBLEM_USER)
    btn = page.locator(".inventory_item").first.locator("button")
    btn.click()
    btn.click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("1"), "problem_user's Remove button is expected to not actually remove the item (seeded demo bug)"


def test_known_bug_problem_user_checkout_fields_are_swapped(page):
    login_as(page, PROBLEM_USER)
    add_first_item_to_cart(page)
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "Mykyta")
    page.fill("#last-name", "Kuklin")
    assert page.input_value("#first-name") == "Kuklin", "problem_user's First Name field is expected to end up holding the Last Name value (seeded demo bug)"
    assert page.input_value("#last-name") == "", "problem_user's Last Name field is expected to end up empty (seeded demo bug)"


def test_known_bug_problem_user_checkout_blocked_by_field_swap(page):
    login_as(page, PROBLEM_USER)
    add_first_item_to_cart(page)
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "Mykyta")
    page.fill("#last-name", "Kuklin")
    page.fill("#postal-code", "21000")
    page.click("#continue")
    expect(page.locator("[data-test='error']")).to_contain_text("Last Name is required"), "problem_user is expected to get blocked at checkout due to the field-swap bug, even with all fields filled in (seeded demo bug)"


# ==== Regular functional tests (real regressions here SHOULD go red) ====

def test_cannot_access_inventory_without_logging_in(page):
    page.goto("/inventory.html")
    expect(page).to_have_url(re.compile(r".*saucedemo\.com/?$"))
    expect(page.locator("[data-test='error']")).to_contain_text("You can only access")


def test_login_username_is_case_sensitive(page):
    page.goto("/")
    page.fill("#user-name", "Standard_User")
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    expect(page.locator("[data-test='error']")).to_contain_text("do not match")
