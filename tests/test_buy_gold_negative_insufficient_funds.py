# tests/test_buy_gold_negative_insufficient_funds.py
# Negative: Attempt to buy with an amount higher than wallet balance.

from pages.buy_gold_page import BuyGoldPage

def test_buy_gold_negative_insufficient_funds(logged_in_page):
    page = logged_in_page

    buy = BuyGoldPage(page)
    buy.open()

    # Intentionally huge amount to trigger insufficient funds
    buy.buy_by_amount("999999999999")
    buy.confirm()

    buy.expect_error_contains("insufficient")  # adjust expected text to real message
