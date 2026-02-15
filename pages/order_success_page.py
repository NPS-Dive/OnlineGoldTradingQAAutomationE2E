# pages/order_success_page.py
# Success receipt assertions.

class OrderSuccessPage:
    def __init__(self, page):
        self.page = page
        self.success_title = page.locator('[data-testid="order-success-title"]')
        self.order_id = page.locator('[data-testid="order-id"]')

    def expect_success(self):
        self.success_title.wait_for(state="visible")

    def get_order_id(self) -> str:
        self.order_id.wait_for(state="visible")
        return self.order_id.inner_text().strip()
