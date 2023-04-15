import time
from urllib.parse import unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

from constants import (
    HINDI_CHARS, H5_CLASS, MENU_P, SECT_1_CLASS, SECT_2_CLASS,
    SECT_3_CLASS, SECT_4_CLASS, SECT_5_CLASS, H2_CLASS
)


class WebsiteValidator:
    def __init__(self,):
        self.driver = None

    def __enter__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        chrome_prefs = {"profile.default_content_settings": {"images": 2}}
        options.experimental_options["prefs"] = chrome_prefs
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def page_translated(self, url: str) -> bool:
        self.driver.get(url)
        h2 = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, f"h2.{H2_CLASS.replace(' ', '.')}"))
        )
        ref_text = h2.text.strip().replace(" ", "").replace(".", "")
        none_hindi = 0
        for char in ref_text:
            if char not in HINDI_CHARS:
                none_hindi += 1
        if none_hindi / len(ref_text) > 0.2:
            return False

        return True

    def js_drop_downs(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 3)
            # Open report dropdown
            passed = self._presence_on_hover(
                wait, [By.XPATH, '//div[@data-name="NAV_DROPDOWN"]'],
                (By.CSS_SELECTOR, f"h5.{H5_CLASS.replace(' ', '.')}")
            )
            if not passed:
                return False

            # Move out of the dropdown
            out = self.driver.find_element(By.CSS_SELECTOR, 'section#home-discover')
            ActionChains(self.driver).move_to_element(out).perform()

            # Open menu dropdown
            passed = self._presence_on_hover(
                wait, [By.XPATH, '//div[@data-name="MAIN_NAV_TRIGGER_CONTAINER"]'],
                (By.CSS_SELECTOR, f"p.{MENU_P.replace(' ', '.')}")
            )
            if not passed:
                return False

            # Hover on submenus
            passed = self._presence_on_hover(
                wait, [By.XPATH, '//a[@data-detail=\'{"childListId":"rankings"}\']'],
                (By.XPATH, '//img[@alt="Most Popular of All Time"]')
            )
            if not passed:
                return False
            passed = self._presence_on_hover(
                wait, [By.XPATH, '//a[@data-detail=\'{"childListId":"subject-business"}\']'],
                (By.CSS_SELECTOR, 'a.main-nav-dropdown__item-control--highlighted')
            )
            if not passed:
                return False

            # Move out of the dropdown
            out = self.driver.find_element(By.CSS_SELECTOR, 'section#home-discover')
            ActionChains(self.driver).move_to_element(out).perform()

            return True
        except Exception as e:
            print(e)
            return False

    def images_high_resolution(self) -> bool:
        try:
            # Scroll to the bottom in order to load all images
            document_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_increment = 200
            for i in range(0, document_height, scroll_increment):
                self.driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(0.5)
            # Scroll back to the top
            self.driver.execute_script("window.scrollTo(0, 0);")

            # Images of main sections
            images = []
            for section in [SECT_1_CLASS, SECT_2_CLASS, SECT_3_CLASS, SECT_4_CLASS, SECT_5_CLASS]:
                images.extend(self.driver.find_elements(By.XPATH, f'//section[@class="{section}"]//img'))

            for img in images:
                src = img.get_attribute("src")
                if " " in unquote(src):
                    return False
                if ".svg" in src:
                    continue

                blur = [arg for arg in src.split("&") if "blur" in arg]
                if blur and int(blur[0].split("=")[-1]) > 10:
                    return False
        except (ValueError, Exception) as e:
            print(e)
            return False

        return True

    def inner_page_translated(self) -> bool:
        digits = {1, 2, 3, 4, 5, 6, 7, 8, 9, 0}
        home_subs = self.driver.find_elements(By.XPATH, f'//ul[@id="home-subjects"]//a')[:4]
        wait = WebDriverWait(self.driver, 3)
        for sub in home_subs:
            self.driver.get(sub.get_attribute("href"))
            h1 = wait.until(ec.presence_of_element_located((By.TAG_NAME, 'h1')))
            ref_text = h1.text.strip().replace(" ", "").replace(".", "")
            none_hindi = 0
            for char in ref_text:
                if char not in HINDI_CHARS and char not in digits:
                    none_hindi += 1
            if none_hindi / len(ref_text) > 0.2:
                return False
            self.driver.back()
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'ul#home-subjects')))

        return True

    def _presence_on_hover(self, wait, find_args: list, presence_args: tuple) -> bool:
        tag = self.driver.find_element(*find_args)
        ActionChains(self.driver).move_to_element(tag).perform()
        present = wait.until(
            ec.presence_of_element_located(presence_args)
        )
        if not present:
            return False
        return True
