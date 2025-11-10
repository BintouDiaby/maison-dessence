from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth.models import Group
import os
import time


class SeleniumE2ETest(StaticLiveServerTestCase):
    """E2E Selenium tests: login -> add to cart -> open cart -> checkout page.

    Run visible for demos by setting SELENIUM_HEADLESS=0 in PowerShell:
      $env:SELENIUM_HEADLESS='0'; python manage.py test selenium_tests.test_e2e.SeleniumE2ETest
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        headless_env = os.environ.get('SELENIUM_HEADLESS', '1').lower()
        headless = headless_env not in ('0', 'false', 'no')
        if headless:
            options.add_argument('--headless=new')
        else:
            options.add_argument('--window-size=1400,900')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(5)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.driver.quit()
        except Exception:
            pass
        super().tearDownClass()

    def setUp(self):
        User = get_user_model()
        # create a normal user
        self.user = User.objects.create_user(username='testuser@example.com', email='testuser@example.com', password='testpass123')
        # create a vendor user and a product
        vendor = User.objects.create_user(username='vendor@example.com', email='vendor@example.com', password='vendpass')
        vendor_group, _ = Group.objects.get_or_create(name='vendor')
        # add via the user's groups so the m2m_changed signal receives the User instance
        vendor.groups.add(vendor_group)

        # create a product directly in DB so the frontend can fetch it
        from products.models import Product
        self.product = Product.objects.create(
            owner=vendor,
            name='E2E Product',
            description='Product for E2E testing',
            price=4.5,
            stock=10,
            image_url='https://via.placeholder.com/600x400'
        )

    def test_login_add_to_cart_and_checkout(self):
        driver = self.driver
        wait = self.wait

        # 1) Login via UI
        driver.get(self.live_server_url + '/login.html')
        email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        pwd_input = driver.find_element(By.NAME, 'password')
        email_input.send_keys(self.user.email)
        pwd_input.send_keys('testpass123')
        # submit
        submit = driver.find_element(By.CSS_SELECTOR, 'form#login-form button[type="submit"]')
        submit.click()

        # after submit, wait for either a redirect to / or an error message in the login form
        try:
            wait.until(EC.url_matches(self.live_server_url + '/'))
        except Exception:
            # not redirected quickly; continue to check tokens
            pass

        # wait up to a few seconds for JS to store tokens in localStorage
        token = None
        for _ in range(10):
            token = driver.execute_script("return window.localStorage.getItem('md_access_token');")
            if token:
                break
            time.sleep(0.3)

        if not token:
            # collect browser console logs and page feedback to aid debugging
            logs = []
            try:
                for entry in driver.get_log('browser'):
                    logs.append(f"{entry.get('level')}:{entry.get('message')}")
            except Exception:
                pass
            # read feedback text if present
            fb_text = ''
            try:
                fb = driver.find_element(By.ID, 'login-feedback')
                fb_text = fb.text
            except Exception:
                fb_text = ''

            extra = f"console_logs={' | '.join(logs)}; feedback={fb_text}; page_url={driver.current_url}"
            self.fail(f'Token not set in localStorage after login. {extra}')

        # 2) Wait for products to be fetched and rendered (button[data-add]) then click add
        # The page is dynamic and may re-render items; avoid StaleElementReference by
        # locating elements at click time and retrying when stale.
        def try_click_add(driver):
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-add]')
                for b in buttons:
                    try:
                        if b.is_displayed() and b.is_enabled():
                            b.click()
                            return True
                    except StaleElementReferenceException:
                        # element was detached between find and use — try next
                        continue
                return False
            except Exception:
                return False

        clicked = wait.until(try_click_add)
        assert clicked, 'Failed to click any add-to-cart button'

        # The app may update cart-count; wait for it to show a number > 0
        cart_count = wait.until(lambda d: d.find_element(By.ID, 'cart-count'))
        # allow a short time for update
        time.sleep(0.5)
        self.assertTrue(int(cart_count.text.strip()) >= 1 or cart_count.text.strip() != '0')

        # 3) Open cart drawer
        open_cart = driver.find_element(By.ID, 'open-cart')
        open_cart.click()

        # wait for drawer items to contain at least one child
        drawer_items = wait.until(EC.presence_of_element_located((By.ID, 'drawer-items')))
        # allow JS to populate
        time.sleep(0.5)
        children = drawer_items.find_elements(By.XPATH, './*')
        self.assertTrue(len(children) >= 1, msg='Cart drawer has no items')

        # 4) Click checkout link in drawer
        checkout_link = driver.find_element(By.CSS_SELECTOR, 'aside#cart-drawer a[href="/checkout.html"]')
        checkout_link.click()

        # Wait navigation to checkout page
        wait.until(EC.url_contains('/checkout.html'))
        # Assert checkout page elements exist
        self.assertTrue(driver.find_element(By.ID, 'checkout-page'))
        total = driver.find_element(By.ID, 'checkout-total')
        self.assertIsNotNone(total)
