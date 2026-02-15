# pages/buy_gold_page.py
# Buy Gold screen actions + assertions.

class BuyGoldPage:
    def __init__(self, page):
        self.page = page

        self.buy_gold_nav = page.locator('[data-testid="nav-buy-gold"]')

        # Inputs - amount or grams
        self.amount_input = page.locator('[data-testid="buy-amount"]')
        self.grams_input = page.locator('[data-testid="buy-grams"]')

        # Summary fields
        self.price_per_gram = page.locator('[data-testid="price-per-gram"]')
        self.total_payable = page.locator('[data-testid="total-payable"]')

        # Actions
        self.confirm_button = page.locator('[data-testid="buy-confirm"]')

        # Errors
        self.error_box = page.locator('[data-testid="buy-error"]')

    def open(self):
        self.buy_gold_nav.click()
        self.page.wait_for_load_state("networkidle")

    def buy_by_amount(self, amount: str):
        # Fill amount; app calculates grams based on live price.
        self.amount_input.fill(amount)

    def buy_by_grams(self, grams: str):
        self.grams_input.fill(grams)

    def confirm(self):
        self.confirm_button.click()

    def expect_error_contains(self, text: str):
        self.error_box.wait_for(state="visible")
        assert text in self.error_box.inner_text()
