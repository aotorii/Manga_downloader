"""
Website actions for comic-boost.com
"""

import base64
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 1500

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

    def wake_viewer(self, driver):
        canvas = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".currentScreen canvas"))
        )
        ActionChains(driver).move_to_element(canvas).click().perform()
        time.sleep(1)

    def set_window(self, driver, width, height):
        driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": False,
            },
        )
        WebDriverWait(driver, 10).until(
            lambda d: (
                d.execute_script(
                    "return document.querySelector('.currentScreen canvas').width"
                )
                > 0
            )
        )

    def set_single_page_mode(self, driver):
        label = driver.find_element(By.CSS_SELECTOR, 'label[for="spread_false"]')
        if label.get_attribute("aria-pressed") != "true":
            label.click()

    def before_download(self, driver):
        for key in driver.execute_script("return Object.keys(NFBR.a6G.Initializer)"):
            if "menu" in driver.execute_script(
                f"return Object.keys(NFBR.a6G.Initializer.{key})"
            ):
                self.js = key
                break

        self.set_window(driver, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # spread_off toggle is cosmetic for now, don't know why
        # self.wake_viewer(driver)
        # driver.execute_script(f"""
        #     NFBR.a6G.Initializer.{self.js}.menu.showSettingPanel({{
        #         preventDefault: function(){{}}, stopPropagation: function(){{}}
        #     }});
        # """)
        # self.set_single_page_mode(driver)

        # w, h = driver.execute_script(
        #     "var c = document.querySelector('.currentScreen canvas'); return [c.width, c.height];"
        # )
        # print(f"Using canvas size: {w}x{h}")

    def get_imgdata(self, driver, now_page):
        canvas = driver.find_element(By.CSS_SELECTOR, ".currentScreen canvas")
        img_base64 = driver.execute_script(
            """
            var canvas = arguments[0];
            var ctx = canvas.getContext('2d');
            var w = canvas.width, h = canvas.height;
            var imgData = ctx.getImageData(0, 0, w, h).data;
            var bg = [imgData[0], imgData[1], imgData[2]];

            function isBg(x, y) {
                var i = (y * w + x) * 4;
                return Math.abs(imgData[i]-bg[0])<8 && Math.abs(imgData[i+1]-bg[1])<8 && Math.abs(imgData[i+2]-bg[2])<8;
            }
            function rowIsBg(y) { for (var x=0; x<w; x++) if (!isBg(x,y)) return false; return true; }
            function colIsBg(x) { for (var y=0; y<h; y++) if (!isBg(x,y)) return false; return true; }

            var top=0, bottom=h-1, left=0, right=w-1;
            while (top<bottom && rowIsBg(top)) top++;
            while (bottom>top && rowIsBg(bottom)) bottom--;
            while (left<right && colIsBg(left)) left++;
            while (right>left && colIsBg(right)) right--;

            var cropW = right-left+1, cropH = bottom-top+1;

            if (cropW < w * 0.5 || cropH < h * 0.5) {
                cropW = w; cropH = h; left = 0; top = 0;
            }

            var out = document.createElement('canvas');
            out.width = cropW; out.height = cropH;
            out.getContext('2d').drawImage(canvas, left, top, cropW, cropH, 0, 0, cropW, cropH);
            return out.toDataURL('image/png', 1.0).substring(21);
            """,
            canvas,
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
