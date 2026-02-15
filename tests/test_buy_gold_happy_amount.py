# tests/test_buy_gold_happy_amount.py
# Happy path: Buy gold by entering amount (currency).

from pages.buy_gold_page import BuyGoldPage
from pages.order_success_page import OrderSuccessPage

def test_buy_gold_happy_path_by_amount(logged_in_page):
    page = logged_in_page

    buy = BuyGoldPage(page)
    buy.open()

    buy.buy_by_amount("500000")  # example currency amount
    buy.confirm()

    success = OrderSuccessPage(page)
    success.expect_success()

    order_id = success.get_order_id()
    assert order_id != ""
