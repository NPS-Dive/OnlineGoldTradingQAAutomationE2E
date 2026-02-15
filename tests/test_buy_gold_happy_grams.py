# tests/test_buy_gold_happy_grams.py
# Happy path: Buy gold by entering grams.

from pages.buy_gold_page import BuyGoldPage
from pages.order_success_page import OrderSuccessPage

def test_buy_gold_happy_path_by_grams(logged_in_page):
    page = logged_in_page

    buy = BuyGoldPage(page)
    buy.open()

    buy.buy_by_grams("0.5")  # example grams
    buy.confirm()

    success = OrderSuccessPage(page)
    success.expect_success()

    order_id = success.get_order_id()
    assert order_id != ""
