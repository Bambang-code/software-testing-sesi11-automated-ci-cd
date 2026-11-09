from playwright.sync_api import expect

from .seller_page import SellerPage


def test_ui_01_submit_valid_shop(page, seller_url):
    seller = SellerPage(page, seller_url)
    seller.open()
    expect(seller.status).to_have_text("Draf")

    seller.submit("  Kedai Rumpun  ")

    expect(page).to_have_url(seller_url)
    expect(seller.status).to_have_text("Menunggu peninjauan")
    expect(seller.submitted_shop).to_have_text("Kedai Rumpun")


def test_ui_02_reject_whitespace_only_shop(page, seller_url):
    seller = SellerPage(page, seller_url)
    seller.open()

    with page.expect_response(seller_url + "pengajuan") as submission:
        seller.submit("   ")

    assert submission.value.status == 400
    expect(seller.error).to_have_text("Nama toko wajib diisi.")
    expect(seller.shop_name).to_have_attribute("aria-invalid", "true")
    expect(seller.status).to_have_text("Draf")
    expect(seller.submitted_shop).to_have_count(0)


def test_ui_03_pending_application_survives_reload(page, seller_url):
    seller = SellerPage(page, seller_url)
    seller.open()
    seller.submit("Rumah Laras")
    expect(seller.status).to_have_text("Menunggu peninjauan")

    seller.reload()

    expect(seller.status).to_have_text("Menunggu peninjauan")
    expect(seller.submitted_shop).to_have_text("Rumah Laras")


def test_ui_04_withdraw_then_resubmit(page, seller_url):
    seller = SellerPage(page, seller_url)
    seller.open()
    seller.submit("Toko Pertama")
    expect(seller.status).to_have_text("Menunggu peninjauan")

    seller.withdraw()

    expect(seller.status).to_have_text("Draf")
    expect(seller.submitted_shop).to_have_count(0)
    seller.submit("Toko Pengganti")
    expect(seller.status).to_have_text("Menunggu peninjauan")
    expect(seller.submitted_shop).to_have_text("Toko Pengganti")


def test_ui_05_different_browser_session_has_own_application(page, browser, seller_url):
    seller = SellerPage(page, seller_url)
    seller.open()
    seller.submit("Toko Sesi Pertama")
    expect(seller.status).to_have_text("Menunggu peninjauan")

    second_context = browser.new_context()
    try:
        visitor = SellerPage(second_context.new_page(), seller_url)
        visitor.open()
        expect(visitor.status).to_have_text("Draf")
        expect(visitor.submitted_shop).to_have_count(0)
    finally:
        second_context.close()
