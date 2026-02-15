# pages/base_page.py
# Base helpers shared across all pages.

class BasePage:
    def __init__(self, page):
        self.page = page

    def wait_for_url_contains(self, text: str):
        # Useful for confirming navigation happened.
        self.page.wait_for_url(f"**{text}**")
