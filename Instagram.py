import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from randomizeInput import generate_randomName, generate_randomEmail, generate_random_password

import time


with open('user-agents.txt', 'r') as file:
    # Read all lines into a list
    all_user_agents = file.readlines()


class Instagram():

    def __init__(self, handle):
        self.handle = handle
        self.init_driver()

    def init_driver(self):
        url = 'https://www.instagram.com/accounts/emailsignup/'
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--window-size={random.randint(1024,1920)},{random.randint(768,1024)}")
        options.add_argument("--no-sandbox")
        user_agent = random.choice(all_user_agents)
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-dev-shm-usage")

        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # Turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)
        # Setting the driver path and requesting a page
        driver = webdriver.Chrome(options=options)
        # Changing the property of the navigator value for webdriver to undefined
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        ##Proxy
        # random_proxy = '103.159.90.6:8080'
        # options.add_argument(f'--proxy-server={random_proxy}')
        options.add_experimental_option('detach', False)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(url)

    def killdriver(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("Closed driver")

    def checkUsername(self):
        time.sleep(random.uniform(1,4))
        self.driver.execute_script('window.scrollTo(0, 700)')
        try:
            cookies = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, '_a9_1')))
            ActionChains(self.driver).move_to_element_with_offset(cookies,1,2).perform()
            time.sleep(random.uniform(0.4, 1))
            cookies.click()
        except Exception as e:
            print(f"Cookies button not found. {str(e)} \n Continuing without clicking. ")
        try:
            email_input = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located(((By.NAME, 'emailOrPhone')))
            )
            ActionChains(self.driver).move_to_element_with_offset(email_input,1, 2).perform()
            time.sleep(random.uniform(0.4, 1))
            random_email = generate_randomEmail()
            print(f'Instagram: inputing random email > {random_email}')
            email_input.send_keys(random_email)

            fullName_input = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.NAME, 'fullName')))
            ActionChains(self.driver).move_to_element_with_offset(fullName_input,1, 2).perform()
            time.sleep(random.uniform(0.4, 1))
            random_fullName = generate_randomName()
            print(f'Instagram: inputing random full name > {random_fullName}')
            fullName_input.send_keys(random_fullName)

            username_input = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.NAME, 'username')))
            ActionChains(self.driver).move_to_element_with_offset(username_input,1, 2).perform()
            time.sleep(random.uniform(0.4, 1))
            username_input.send_keys(self.handle)

            password_input = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.NAME, 'password')))
            ActionChains(self.driver).move_to_element_with_offset(password_input,1, 2).perform()
            time.sleep(random.uniform(0.4, 1))
            random_password = generate_random_password()
            print(f'Instagram: inputing random password > {random_password}')
            password_input.send_keys(random_password)

            next_button = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Next']"))).click()
            try:
                error_taken = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, "ssfErrorAlert")))
                print(error_taken.text)
                if error_taken.text == 'A user with that username already exists.' or error_taken.text == "This username isn't available. Please try another.":
                    return True
                else:
                    return None
            except Exception as e:
                print('entered exception')
                birthday_page = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.x1fhwpqd.xo1l8bm.x1roi4f4.x2b8uid.x1s3etm8.x676frb.x10wh9bi.x1wdrske.x8viiok.x18hxmgj[style*="line-height"][dir="auto"]'.replace(' ', '.'))))
                birthday_page = birthday_page.text
                print(birthday_page)
                return None if 'birthday' in birthday_page else True

        except Exception as e:
            print(f"some elements couldn't be located : {str(e)}")
            print("Some elements couldn't be located")
            return 'Failure'