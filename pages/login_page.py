# pages/login_page.py
# Login page actions.
# NOTE: Selectors here are placeholders. We'll map them to the real app once you confirm UI.

class LoginPage:
    def __init__(self, page):
        self.page = page

        # Prefer data-testid if exists in product:
        self.username_input = page.locator('[data-testid="login-username"]')
        self.password_input = page.locator('[data-testid="login-password"]')
        self.login_button = page.locator('[data-testid="login-submit"]')

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

        # Post-login landing can be verified by URL or presence of some element
        self.page.wait_for_load_state("networkidle")
