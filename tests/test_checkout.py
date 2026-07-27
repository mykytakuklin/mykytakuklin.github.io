import re

from playwright.sync_api import expect


def add_item_and_go_to_checkout(page):
    page.locator(".inventory_item").first.locator("button").click()
    page.click(".shopping_cart_link")
    page.click("#checkout")


def test_complete_checkout_flow(logged_in_page):
    page = logged_in_page
    add_item_and_go_to_checkout(page)
    page.fill("#first-name", "Mykyta")
    page.fill("#last-name", "Kuklin")
    page.fill("#postal-code", "21000")
    page.click("#continue")
    page.click("#finish")
    expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")


def test_checkout_missing_first_name_shows_error(logged_in_page):
    page = logged_in_page
    add_item_and_go_to_checkout(page)
    page.fill("#last-name", "Kuklin")
    page.fill("#postal-code", "21000")
    page.click("#continue")
    expect(page.locator("[data-test='error']")).to_contain_text("First Name is required")


def test_checkout_missing_last_name_shows_error(logged_in_page):
    page = logged_in_page
    add_item_and_go_to_checkout(page)
    page.fill("#first-name", "Mykyta")
    page.fill("#postal-code", "21000")
    page.click("#continue")
    expect(page.locator("[data-test='error']")).to_contain_text("Last Name is required")


def test_checkout_missing_postal_code_shows_error(logged_in_page):
    page = logged_in_page
    add_item_and_go_to_checkout(page)
    page.fill("#first-name", "Mykyta")
    page.fill("#last-name", "Kuklin")
    page.click("#continue")
    expect(page.locator("[data-test='error']")).to_contain_text("Postal Code is required")


def test_checkout_overview_shows_correct_total(logged_in_page):
    page = logged_in_page
    add_item_and_go_to_checkout(page)
    page.fill("#first-name", "Mykyta")
    page.fill("#last-name", "Kuklin")
    page.fill("#postal-code", "21000")
    page.click("#continue")

    subtotal = float(page.locator(".summary_subtotal_label").text_content().replace("Item total: $", ""))
    tax = float(page.locator(".summary_tax_label").text_content().replace("Tax: $", ""))
    total = float(page.locator(".summary_total_label").text_content().replace("Total: $", ""))

    assert round(subtotal + tax, 2) == round(total, 2)


def test_checkout_cancel_returns_to_cart(logged_in_page):
    page = logged_in_page
    add_item_and_go_to_checkout(page)
    page.click("#cancel")
    expect(page).to_have_url(re.compile(r".*cart\.html"))
