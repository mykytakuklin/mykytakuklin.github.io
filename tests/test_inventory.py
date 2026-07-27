from playwright.sync_api import expect


def prices_of(page):
    texts = page.locator(".inventory_item_price").all_text_contents()
    return [float(t.replace("$", "")) for t in texts]


def names_of(page):
    return page.locator(".inventory_item_name").all_text_contents()


def test_inventory_displays_six_products(logged_in_page):
    expect(logged_in_page.locator(".inventory_item")).to_have_count(6)


def test_sort_products_price_low_to_high(logged_in_page):
    logged_in_page.select_option("[data-test='product-sort-container']", "lohi")
    values = prices_of(logged_in_page)
    assert values == sorted(values)


def test_sort_products_price_high_to_low(logged_in_page):
    logged_in_page.select_option("[data-test='product-sort-container']", "hilo")
    values = prices_of(logged_in_page)
    assert values == sorted(values, reverse=True)


def test_sort_products_name_a_to_z(logged_in_page):
    logged_in_page.select_option("[data-test='product-sort-container']", "az")
    values = names_of(logged_in_page)
    assert values == sorted(values)


def test_sort_products_name_z_to_a(logged_in_page):
    logged_in_page.select_option("[data-test='product-sort-container']", "za")
    values = names_of(logged_in_page)
    assert values == sorted(values, reverse=True)


def test_add_product_to_cart_updates_badge(logged_in_page):
    logged_in_page.locator(".inventory_item").first.locator("button").click()
    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_text("1")


def test_add_multiple_products_updates_badge_count(logged_in_page):
    items = logged_in_page.locator(".inventory_item")
    items.nth(0).locator("button").click()
    items.nth(1).locator("button").click()
    items.nth(2).locator("button").click()
    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_text("3")


def test_remove_product_from_cart(logged_in_page):
    button = logged_in_page.locator(".inventory_item").first.locator("button")
    button.click()
    button.click()
    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_count(0)


def test_add_to_cart_button_toggles_to_remove(logged_in_page):
    button = logged_in_page.locator(".inventory_item").first.locator("button")
    expect(button).to_have_text("Add to cart")
    button.click()
    expect(button).to_have_text("Remove")


def test_view_product_details_page(logged_in_page):
    first_name = logged_in_page.locator(".inventory_item_name").first.text_content()
    logged_in_page.locator(".inventory_item_name").first.click()
    expect(logged_in_page.locator(".inventory_details_name")).to_have_text(first_name)


def test_add_to_cart_from_product_details_page(logged_in_page):
    logged_in_page.locator(".inventory_item_name").first.click()
    logged_in_page.locator("button", has_text="Add to cart").click()
    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_text("1")
