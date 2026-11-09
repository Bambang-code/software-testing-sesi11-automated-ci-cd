from threading import Thread

import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from zenta_auth.web import create_app


@pytest.fixture(scope="module")
def seller_url(tmp_path_factory):
    database = tmp_path_factory.mktemp("seller-ui") / "seller.sqlite3"
    with make_server("127.0.0.1", 0, create_app(database)) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/"
        finally:
            server.shutdown()
            thread.join()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    try:
        yield context.new_page()
    finally:
        context.close()
