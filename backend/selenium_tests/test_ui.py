from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os


class SimpleSeleniumUITest(StaticLiveServerTestCase):
    """A minimal Selenium test that opens the homepage and checks title/body exists.

        Requirements (install in backend venv):
            pip install selenium webdriver-manager

        Run (headless, default):
            python manage.py test selenium_tests.test_ui.SimpleSeleniumUITest

        Run visible (show the browser window) in PowerShell:
            $env:SELENIUM_HEADLESS='0'; python manage.py test selenium_tests.test_ui.SimpleSeleniumUITest

        Notes:
        - The test respects the environment variable `SELENIUM_HEADLESS`.
            Set it to '0' or 'false' to run with a visible browser for demos.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        # By default run headless. To see the browser during a demo set
        # SELENIUM_HEADLESS=0 (or in PowerShell: $env:SELENIUM_HEADLESS='0')
        headless_env = os.environ.get('SELENIUM_HEADLESS', '1').lower()
        headless = headless_env not in ('0', 'false', 'no')
        if headless:
            # use new headless mode when available
            options.add_argument('--headless=new')
        else:
            # visible mode - set a reasonable window size
            options.add_argument('--window-size=1400,900')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Install driver automatically
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.driver.quit()
        except Exception:
            pass
        super().tearDownClass()

    def test_homepage_static_site_served(self):
        url = self.live_server_url + '/'
        self.driver.get(url)
        body = self.driver.find_elements(By.TAG_NAME, 'body')
        self.assertTrue(len(body) >= 1)
