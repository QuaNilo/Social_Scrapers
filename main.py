try:
    from dotenv import load_dotenv
    from ensta import Guest
    from flask import Flask, request, jsonify
    import json
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.proxy import Proxy, ProxyType
    from selenium.webdriver.support import expected_conditions as EC
    from SocialMediaNorms import SocialMediaHandleValidator
    from selenium.common.exceptions import NoSuchElementException
    from randomizeInput import generate_randomName, generate_randomEmail, generate_random_password
    import praw
    import time
    import random
    import logging
    import os
    import googleapiclient.discovery
    import googleapiclient.errors
    from googleapiclient.discovery import build
    import prawcore
    import requests
    from Instagram import Instagram
    import chromedriver_binary

except ModuleNotFoundError as e:
    print(f"Please download dependencies from requirements.txt : {str(e)}")
except Exception as ex:
    print(ex)

app = Flask(__name__)

with open('login.json', 'r') as file:
    login_data = json.load(file)

# Open the file for reading
with open('user-agents.txt', 'r') as file:
    # Read all lines into a list
    all_user_agents = file.readlines()

# Configure the logger
app.logger.setLevel(logging.INFO)  # Set the desired log level
handler = logging.StreamHandler()  # Log to the console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


#TODO Facebook asks for a login on some user profiles and not others, find a way to log in selenium to scrape
#TODO twitter and instagram make it hard to pinpoint if handle is blocked due to account being suspended, or whatever reason they have

class SocialMediaChecker:
    def __init__(self):
        self.initdriver()
        load_dotenv("variables.env")
    def initdriver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--window-size={random.randint(1024,1920)},{random.randint(768,1024)}")
        options.add_argument("--no-sandbox")
        user_agent = random.choice(all_user_agents)
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('detach', False)

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
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def killdriver(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            app.logger.info("Closed driver")

    def reddit_checker(self, handle):
        try:
            self.reddit = praw.Reddit(
                client_id=os.environ.get('reddit_client_id'),
                client_secret=os.environ.get('reddit_client_secret'),
                user_agent=os.environ.get('reddit_user_agent')
            )

            redditor = self.reddit.redditor(handle)
            if redditor:
                user_data = redditor._fetch_data()
                app.logger.info("Reddit : Found user with that handle")
                return user_data

        except prawcore.exceptions.NotFound:
            app.logger.info("Reddit : Couldn't find user with that handle")
            return None

    def instagram_checker(self, handle):
        try:
            self.guest = Guest()
            profile = self.guest.profile(handle)
            if profile is not None:
                json_data = {
                        "handle": handle,
                        "full_name": profile.full_name,
                        "biography": profile.biography,
                        "followers": profile.follower_count,
                        "following": profile.following_count
                }
                app.logger.info("Instagram : Found user with that handle")
                return json_data
            else:
                app.logger.info("Instagram : Couldn't find user with that handle")
                app.logger.info("Instagram : Checking if handle is available....")

                instagram = Instagram(handle)
                response = instagram.checkUsername()

                instagram.killdriver()

                if response:
                    json_data = {
                        "handle": handle,
                        'response': 'It may mean that the name was used before and the account was suspended or removed from Instagram, or that the username is not allowed, or that it is simply not available for use.'
                    }
                    app.logger.info("Instagram : handle is not available")
                    return json_data
                else:
                    app.logger.info("Instagram : Handle is available")
                    return None

        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")

    def youtube_checker(self, handle):
        try:
            API_KEY = os.environ.get('yt_API_KEY')

            youtube = build('youtube', 'v3', developerKey=API_KEY)
            response = youtube.search().list(
                part='id,snippet',
                q=handle,
                type='channel'
            ).execute()

            if 'items' in response and len(response['items']) > 0:
                channel = response['items'][0]
                channel_id = channel['id']['channelId']
                channel_title = channel['snippet']['title']
                channel_description = channel['snippet']['description']
                app.logger.info("Youtube : Found user with that handle")

                output = {
                    'channel_id': channel_id,
                    'channel_name': handle,
                    'channel_title': channel_title
                }
                return output

            else:
                app.logger.info("Youtube : Couldn't find user with that handle")
                return None

        except Exception as e:

            app.logger.info(f'Error : {str(e)}')

    def tiktok_checker(self, handle):
        try:
            url = f'https://www.tiktok.com/@{handle}'
            self.driver.get(url)
            time.sleep(random.uniform(1, 4))
            try:
                profile_name = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ekmpd5l3 .e1457k4r8')))
                time.sleep(random.uniform(0.4, 1))
                ActionChains(self.driver).move_to_element_with_offset(profile_name, random.randint(1,3), random.randint(1,3)).perform()
                profile_name = profile_name.text
                output = {
                    'profile_name': profile_name
                }
                app.logger.info("tiktok : Found user with that handle")
                return output
            except Exception as e:
                app.logger.info(f"tiktok : Couldn't find user with that handle \n")
                return None

        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")
            return 'Failure'

    def twitter_checker(self, handle):
        try:
            url = f'https://twitter.com/{handle}'
            self.driver.get(url)
            time.sleep(random.uniform(1, 4))
            try:
                # following = self.driver.find_element('css selector', '.r-1mf7evn .r-b88u0q .r-qvutc0').text

                message = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[1]/span'))).text
                time.sleep(random.uniform(0.5, 1))
                app.logger.info("Twitter : Couldn't find user with that handle")
                if message == 'This account doesn’t exist':
                    return None
                elif message == 'Account suspended':
                    output = { 'account-status': 'suspended'}
                    return output

            except Exception as e:
                output = {
                    'Handle': f"@{handle}"
                }
                app.logger.info("Twitter : Found user with that handle")
                return output

        except Exception as e:
            self.driver.quit()
            app.logger.info(f"Unexpected error occurred : {str(e)}")
            return 'Failure'

    def twitch_checker(self,handle):
        try:
            twitch = TwitchAPI(client_id=os.environ.get('twitch_client_id'), client_secret=os.environ.get('twitch_client_secret'))
            response = twitch.check_user(handle)
            data = response.json()
            if data['data']:
                output = {
                    'response': response.json()
                }
                app.logger.info("Twitch : Found user with that handle")
                return output
            else:
                app.logger.info("Twitch : Couldn't find user with that handle")
                return None

        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")

    def facebook_checker(self,handle):
        try:
            url = f'https://www.facebook.com/'
            self.driver.get(url)
            time.sleep(random.uniform(1, 4))
            try:
                decline_cookies = WebDriverWait(self.driver,3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="cookie-policy-manage-dialog-accept-button"]')))
                ActionChains(self.driver).move_to_element_with_offset(decline_cookies, random.randint(1, 3), random.randint(1, 3))
                decline_cookies.click()

            except Exception as e:
                print(f'No decline cookies element found : {str(e)}')

            try:
                email_input = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'email')))
                password_input = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'pass')))
                login_button = WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.NAME, 'login')))
                time.sleep(random.uniform(0.5,2))
            except Exception as e:
                app.logger.info(f"Failed to get form elements : {str(e)}")
                return 'Failure'



            ActionChains(self.driver).move_to_element_with_offset(email_input,random.randint(1, 3), random.randint(1, 3)).perform()
            time.sleep(random.uniform(0.5,1.5))
            email_input.send_keys(login_data['facebook']['email'])

            ActionChains(self.driver).move_to_element_with_offset(password_input,random.randint(1, 3), random.randint(1, 3)).perform()
            time.sleep(random.uniform(0.5,1.5))
            password_input.send_keys(login_data['facebook']['password'])

            ActionChains(self.driver).move_to_element_with_offset(login_button,random.randint(1, 3), random.randint(1, 3)).perform()
            time.sleep(random.uniform(0.5,1.5))
            login_button.click()

            ##LOGIN CHECK
            time.sleep(random.uniform(1,3))
            welcome = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x14z4hjw.x3x7a5m.xngnso2.x1qb5hxa.x1xlr1w8.xzsf02u[dir="auto"]')))
            if welcome:
                self.driver.get(f'https://m.facebook.com/{handle}')
                try:
                    time.sleep(random.uniform(0.4, 1))
                    profile_name = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.x1heor9g.x1qlqyl8.x1pd3egz.x1a2a7pz')))
                    print(f'profile found : {profile_name.text}')
                    output = {
                        'Handle': f"@{handle}"
                    }
                    return output
                except Exception as err:
                    app.logger.info(f"Facebook : Profile not found ")
                    return None

            else:
                return 'Failure'
        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")
            return 'Failure'

class TwitchAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def check_user(self,handle):
        url = f'https://api.twitch.tv/helix/users?login={handle}'
        headers = {
            'Authorization': f'Bearer {os.environ.get("twitch_access_token")}',
            'Client-ID': self.client_id
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            self.getAccessToken()
            headers['Authorization'] = f'Bearer {os.environ.get("twitch_access_token")}'

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            else:
                raise Exception(f"Something went wrong with request : {response}")

        elif response.status_code == 200:
            return response
        else:
            raise Exception(f"Unexpected Error occurred")


    def getAccessToken(self):
        tokenResponse = requests.post(url='https://id.twitch.tv/oauth2/token',
                                      data={'client_id': self.client_id,
                                               'client_secret': self.client_secret,
                                               'grant_type': 'client_credentials'})
        if tokenResponse.status_code == 200:
            response_data = tokenResponse.json()  # Get the JSON response content
            access_token = response_data.get('access_token')

            if access_token:
                os.environ['twitch_access_token'] = access_token
            else:
                app.logger.info("Access token not found in response.")
                return jsonify('FAILED TO GET ACCESS_TOKEN'), 500
        else:
            app.logger.info("Token request failed with status code:", tokenResponse.status_code)
            return jsonify("Token request failed with status code:", tokenResponse.status_code), 500

@app.route('/check_handle', methods=['GET'])
def check_handle():
    social_network = request.args.get('social_network')
    handle = request.args.get('handle')
    social_media_checker = SocialMediaChecker()
    validator = SocialMediaHandleValidator(handle)
    valid_social_networks = ['twitter', 'instagram', 'reddit', 'tiktok', 'youtube', 'twitch', 'facebook']


    if not handle:
        response_data = {'success': False,'error': {'type': 'HandleNotProvided', 'message': "Handle not provided"}}
        return jsonify(response_data), 400

    if not social_network:
        response_data = {'success': False, 'error': {'type': 'socialNotProvided', 'message': "social network not provided"}}
        return jsonify(response_data), 400

    if social_network not in valid_social_networks:
        response_data = {'success': False, 'error': {'type': 'invalidSocial', 'message': f"Social network is not valid, please choose a social network from this list : {valid_social_networks}"}}
        return jsonify(response_data), 400

    if social_network == "twitter":

        try:
            if not validator.is_valid_twitter_handle():
                response_data = {'success': False, 'error': {'type': 'invalidHandle', 'message': f"Handle({str(handle)}) Usernames can only contain letters, numbers, periods, and underscores Longer than 4 chars and Shorter than 15 Chars"}}
                return jsonify(response_data), 400
            response = social_media_checker.twitter_checker(handle)
            social_media_checker.killdriver()
            if response:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": response
                    }
                }
                return user_data, 200
            else:
                return jsonify({"is_available": True, "success": True, 'data': { 'response': [response]}})

        except Exception as e:
            return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

    if social_network == "reddit":

        try:
            if not validator.is_valid_reddit_handle():
                response_data = {'success': False, 'error': {'type': 'invalidHandle', 'message': f"Handle({str(handle)}) Usernames can only contain letters, numbers, underscore and the dash Longer than 4 chars and Shorter than 15 Chars"}}
                return jsonify(response_data), 400
            response = social_media_checker.reddit_checker(handle)
            social_media_checker.killdriver()
            if response:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": response
                    }
                }
                return user_data, 200
            else:
                return jsonify({"is_available": True, "success": True, 'data': { 'response': [response]}})

        except Exception as e:
            return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

    if social_network == 'tiktok':
        try:
            if not validator.is_valid_tiktok_handle():
                response_data = {'success': False, 'error': {'type': 'invalidHandle', 'message': f"Handle({str(handle)}) Usernames can only contain letters, numbers, periods, and underscores. Longer than 4 chars and Shorter than 24 Chars"}}
                return jsonify(response_data), 400
            response = social_media_checker.tiktok_checker(handle)

            social_media_checker.killdriver()
            if response:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": response
                    }
                }
                return user_data, 200
            else:
                return jsonify({"is_available": True, "success": True, 'data': { 'response': [response]}})

        except Exception as e:
            return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

    if social_network == 'twitch':
        try:
            if not validator.is_valid_twitch_handle():
                response_data = {'success': False, 'error': {'type': 'invalidHandle','message': f"Handle({str(handle)}) Usernames can only contain letters, numbers, underscore, Longer than 4 chars and Shorter than 25 Chars"}}
                return jsonify(response_data), 400
            response = social_media_checker.twitch_checker(handle)
            social_media_checker.killdriver()
            if response:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": response
                    }
                }
                return user_data, 200
            else:
                return jsonify({"is_available": True, "success": True, 'data': { 'response': [response]}})

        except Exception as e:
            return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

    if social_network == "youtube":
        try:
            if not validator.is_valid_youtube_handle():
                response_data = {'success': False, 'error': {'type': 'invalidHandle','message': f"Handle({str(handle)}) Usernames can only contain letters, numbers, space and the period Longer than 1 chars and Shorter than 50 Chars"}}
                return jsonify(response_data), 400
            response = social_media_checker.youtube_checker(handle)

            social_media_checker.killdriver()
            if response:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": response
                    }
                }
                return user_data, 200
            else:
                return jsonify({"is_available": True, "success": True, 'data': { 'response': [response]}})
        except Exception as e:
            return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

    if social_network == "facebook":
        if not validator.is_valid_facebook_handle():
            response_data = {'success': False, 'error': {'type': 'invalidHandle',
             'message': f"Handle({str(handle)}) Usernames can only contain letters, numbers, underscore and the dash Longer than 4 chars and Shorter than 15 Chars"}}
            return jsonify(response_data), 400
        try:
            response = social_media_checker.facebook_checker(handle)
            social_media_checker.killdriver()
            if response:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": response
                    }
                }
                return user_data, 200
            else:
                return jsonify({"is_available": True, "success": True, 'data': { 'response': [response]}})

        except Exception as e:
            return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

    if social_network == "instagram":
        try:
            if not validator.is_valid_instagram_handle():
                response_data = {'success': False, 'error': {'type': 'invalidHandle',
                'message': f"Handle({str(handle)})  An Instagram username is limited to 4-30 characters and must contain only letters, numbers, periods, and underscores."}}
                return jsonify(response_data), 400
            response = social_media_checker.instagram_checker(handle)
            social_media_checker.killdriver()
            if response:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": response
                    }
                }
                return user_data, 200
            else:
                return jsonify({"available": True, "success": True})
        except Exception as e:
            return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

@app.route('/checkall_handle', methods=['GET'])
def checkall_handle():
    handle = request.args.get('handle')
    social_media_checker = SocialMediaChecker()
    validator = SocialMediaHandleValidator(handle)

    if not handle:
        response_data = {'success': False,'error': {'type': 'HandleNotProvided', 'message': "Handle not provided"}}
        return jsonify(response_data), 400

    results = check_single_handle(handle, social_media_checker, validator)
    if results['success']:
        return jsonify(results), 200
    else:
        return jsonify(results), 500

def check_single_handle(handle, social_media_checker, validator):
    try:
        results = {
            'success': True,
            'data': {
                ##True if available, False if not available
                'twitter': {
                    'is_available': social_media_checker.twitter_checker(handle) if validator.is_valid_twitter_handle() else False,
                    'success': True
                },
                'reddit': {
                    'is_available': social_media_checker.reddit_checker(handle) if validator.is_valid_reddit_handle() else False,
                    'success': True
                },
                'tiktok': {
                    'is_available': social_media_checker.tiktok_checker(handle) if validator.is_valid_tiktok_handle() else False,
                    'success': True
                },
                'youtube': {
                    'is_available': social_media_checker.youtube_checker(handle) if validator.is_valid_youtube_handle() else False,
                    'success': True
                },
                'instagram': {
                    'is_available': social_media_checker.instagram_checker(handle) if validator.is_valid_instagram_handle() else False,
                    'success': True
                },
                'twitch': {
                    'is_available': social_media_checker.twitch_checker(handle) if validator.is_valid_twitch_handle() else False,
                    'success': True
                },
                'facebook': {
                    'is_available': social_media_checker.facebook_checker(handle) if validator.is_valid_facebook_handle() else False,
                    'success': True
                },
            }
        }
        social_media_checker.killdriver()
        for platform, platform_data in results['data'].items():
            if platform_data['is_available'] == 'Failure':
                platform_data['success'] = False
            elif platform_data['is_available'] == None:
                platform_data['is_available'] = True
            else:
                platform_data['is_available'] = False

        return results
    except Exception as e:
        response_data = {'success': False, 'error': {'type': 'genericError', 'message': f"{str(e)}"}}
        return response_data


if __name__ == '__main__':
    app.run(debug=True)


