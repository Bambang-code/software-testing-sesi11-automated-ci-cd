from playwright.sync_api import Page


class SellerPage:
    def __init__(self, page: Page, url: str):
        self.page = page
        self.url = url
        self.status = page.get_by_test_id("application-status")
        self.shop_name = page.get_by_test_id("shop-name")
        self.submitted_shop = page.get_by_test_id("submitted-shop")
        self.submit_button = page.get_by_test_id("submit-application")
        self.withdraw_button = page.get_by_test_id("withdraw-application")
        self.error = page.get_by_test_id("application-error")

    def open(self):
        self.page.goto(self.url, wait_until="domcontentloaded")

    def submit(self, shop_name: str):
        self.shop_name.fill(shop_name)
        self.submit_button.click()

    def reload(self):
        self.page.reload(wait_until="domcontentloaded")

    def withdraw(self):
        self.withdraw_button.click()
