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
    import dotenv
    import chromedriver_binary

except ModuleNotFoundError as e:
    print(f"Please download dependencies from requirements.txt : {str(e)}")
except Exception as ex:
    print(ex)

app = Flask(__name__)

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
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('detach', True)
        ##Proxy
        # random_proxy = '103.159.90.6:8080'
        # options.add_argument(f'--proxy-server={random_proxy}')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def killdriver(self):
        self.driver.quit()

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
                instagram = Instagram(handle)
                app.logger.info("Instagram : Couldn't find user with that handle")

                app.logger.info("Instagram : Checking if handle is available....")
                response = instagram.checkUsername()
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

        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")

    def tiktok_checker(self, handle):
        try:
            url = f'https://www.tiktok.com/@{handle}'
            self.driver.get(url)

            try:
                profile_name = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ekmpd5l3 .e1457k4r8')))
                ActionChains(self.driver).move_to_element_with_offset(profile_name, 1, 1).perform()
                time.sleep(random.uniform(0.01, 0.1))
                profile_name = profile_name.text
                output = {
                    'profile_name': profile_name
                }
                app.logger.info("tiktok : Found user with that handle")
                return output
            except Exception as e:
                app.logger.info(f"tiktok : Couldn't find user with that handle \n {str(e)}")
                return None

        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")


    def twitter_checker(self, handle):
        try:
            url = f'https://twitter.com/{handle}'
            self.driver.get(url)

            try:
                # following = self.driver.find_element('css selector', '.r-1mf7evn .r-b88u0q .r-qvutc0').text
                message = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[1]/span'))).text
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
            url = f'https://m.facebook.com/{handle}'
            self.driver.get(url)

            try:
                profile_name = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, '._391s'))).text
                output = {
                    'profile_name': profile_name
                }
                app.logger.info("Facebook : Found user with that handle")
                return output
            except Exception as e:
                app.logger.info("Facebook : Couldn't find user with that handle")
                return None

        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")

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
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-dev-shm-usage")
        ##Proxy
        # random_proxy = '103.159.90.6:8080'
        # options.add_argument(f'--proxy-server={random_proxy}')
        options.add_experimental_option('detach', False)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(url)

    def checkUsername(self):

        try:
            cookies = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, '_a9_1')))
            ActionChains(self.driver).move_to_element_with_offset(cookies,1,2).perform()
            time.sleep(random.uniform(0.05, 0.15))
            cookies.click()
        except Exception as e:
            app.logger.info(f"Cookies button not found. {str(e)} \n Continuing without clicking. ")
        try:
            email_input = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located(((By.NAME, 'emailOrPhone')))
            )
            ActionChains(self.driver).move_to_element_with_offset(email_input,1, 2).perform()
            time.sleep(random.uniform(0.05,0.15))
            random_email = generate_randomEmail()
            app.logger.info(f'Instagram: inputing random email > {random_email}')
            email_input.send_keys(random_email)

            fullName_input = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.NAME, 'fullName')))
            ActionChains(self.driver).move_to_element_with_offset(fullName_input,1, 2).perform()
            time.sleep(random.uniform(0.05,0.15))
            random_fullName = generate_randomName()
            app.logger.info(f'Instagram: inputing random full name > {random_fullName}')
            fullName_input.send_keys(random_fullName)

            username_input = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.NAME, 'username')))
            ActionChains(self.driver).move_to_element_with_offset(username_input,1, 2).perform()
            time.sleep(random.uniform(0.05,0.15))
            username_input.send_keys(self.handle)

            password_input = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.NAME, 'password')))
            ActionChains(self.driver).move_to_element_with_offset(password_input,1, 2).perform()
            time.sleep(random.uniform(0.05,0.15))
            random_password = generate_random_password()
            app.logger.info(f'Instagram: inputing random password > {random_password}')
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
            app.logger.info("Some elements couldn't be located")
            return None

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
    valid_social_networks = ['twitter', 'instagram', 'reddit', 'tiktok', 'youtube', 'twitch'] ##Facebook removed temporarily


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
            # social_media_checker.killdriver()
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

    # if social_network == "facebook":
        # if not validator.is_valid_facebook_handle():
        #     response_data = {'success': False, 'error': {'type': 'invalidHandle',
        #      'message': f"Handle({str(handle)}) Usernames can only contain letters, numbers, underscore and the dash Longer than 4 chars and Shorter than 15 Chars"}}
        #     return jsonify(response_data), 400
    #     try:
    #         response = social_media_checker.facebook_checker(handle)
    #         social_media_checker.killdriver()
    #         if response:
    #             user_data = {
    #                 "is_available": False,
    #                 "success": True,
    #                 "data": {
    #                     "response": response
    #                 }
    #             }
    #             return user_data, 200
    #         else:
    #             return jsonify({"is_available": True, "success": True, 'data': { 'response': [response]}})
    #
    #     except Exception as e:
    #         return jsonify({"success": False, 'error': {'type': 'genericError', 'message': str(e)}})

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

    if not handle:
        response_data = {'success': False,'error': {'type': 'HandleNotProvided', 'message': "Handle not provided"}}
        return jsonify(response_data), 400

    results = check_single_handle(handle, social_media_checker)
    return jsonify(results), 200

def check_single_handle(handle, social_media_checker):
    results = {
        'success': True,
        'data': {
            ##True if available, False if not available
            'twitter': False if social_media_checker.twitter_checker(handle) or len(handle) <= 4 or len(handle) >= 15 else True,
            #'facebook': False if social_media_checker.facebook_checker(handle) or len(handle) < 5 else True,
            'reddit': False if social_media_checker.reddit_checker(handle) else True,
            'tiktok': False if social_media_checker.tiktok_checker(handle) else True,
            'youtube': False if social_media_checker.youtube_checker(handle) else True,
            'instagram': False if social_media_checker.instagram_checker(handle) else True,
            'twitch': False if social_media_checker.twitch_checker(handle) else True
        }
    }
    social_media_checker.killdriver()
    return results

if __name__ == '__main__':
    app.run(debug=False)


