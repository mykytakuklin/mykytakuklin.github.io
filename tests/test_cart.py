import re

from playwright.sync_api import expect


def test_cart_shows_added_items(logged_in_page):
    name = logged_in_page.locator(".inventory_item_name").first.text_content()
    logged_in_page.locator(".inventory_item").first.locator("button").click()
    logged_in_page.click(".shopping_cart_link")
    expect(logged_in_page.locator(".cart_item")).to_have_count(1)
    expect(logged_in_page.locator(".inventory_item_name")).to_have_text(name)


def test_continue_shopping_returns_to_inventory(logged_in_page):
    logged_in_page.click(".shopping_cart_link")
    logged_in_page.click("#continue-shopping")
    expect(logged_in_page).to_have_url(re.compile(r".*inventory\.html"))


def test_remove_item_from_cart_page(logged_in_page):
    logged_in_page.locator(".inventory_item").first.locator("button").click()
    logged_in_page.click(".shopping_cart_link")
    logged_in_page.locator(".cart_item").first.locator("button").click()
    expect(logged_in_page.locator(".cart_item")).to_have_count(0)
    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_count(0)
