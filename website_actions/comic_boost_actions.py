"""
Website actions for comic-boost.com
"""

import base64

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

try:
    from abstract_website_actions import WebsiteActions
except ImportError:
    from website_actions.abstract_website_actions import WebsiteActions


class ComicBoost(WebsiteActions):
    """
    comic-boost.com
    """

    login_url = "https://comic-boost.com/login"
    js = ""

    @staticmethod
    def check_url(manga_url):
        return manga_url.find("comic-boost.com") != -1

    def get_sum_page_count(self, driver):
        return int(
            str(
                driver.find_element(By.ID, "pageSliderCounter").get_attribute(
                    "textContent"
                )
            ).split("/")[1]
        )

    def move_to_page(self, driver, page):
        driver.execute_script(
            f"NFBR.a6G.Initializer.{self.js}.menu.options.a6l.moveToPage(%d)" % page
        )

    def wait_loading(self, driver):
        def _check_is_loading(elements):
            return any(e.is_displayed() for e in elements)

        WebDriverWait(driver, 600).until_not(
            lambda x: _check_is_loading(x.find_elements(By.CSS_SELECTOR, ".loading"))
        )

    def get_imgdata(self, driver, now_page):
        canvas = driver.find_element(By.CSS_SELECTOR, ".currentScreen canvas")
        img_base64 = driver.execute_script(
            "return arguments[0].toDataURL('image/png', 1.0).substring(21);", canvas
        )
        return base64.b64decode(img_base64)

    def get_now_page(self, driver):
        return int(
            str(
                driver.find_element(By.ID, "pageSliderCounter").get_attribute(
                    "textContent"
                )
            ).split("/")[0]
        )

    def before_download(self, driver):
        for key in driver.execute_script("return Object.keys(NFBR.a6G.Initializer)"):
            if "menu" in driver.execute_script(
                f"return Object.keys(NFBR.a6G.Initializer.{key})"
            ):
                self.js = key
                break
