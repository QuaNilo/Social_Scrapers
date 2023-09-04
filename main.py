try:
    from dotenv import load_dotenv
    from ensta import Guest
    from flask import Flask, request, jsonify
    import json
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support import expected_conditions as EC
    import praw
    import time
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


#TODO Facebook asks for a login on some user profiles and not others, find a way to log in selenium to scrape
#TODO twitter and instagram make it hard to pinpoint if handle is blocked due to account being suspended, or whatever reason they have

class SocialMediaChecker:
    def __init__(self):
        self.initdriver()
        load_dotenv("variables.env")
    def initdriver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('detach', False)
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

                response = instagram.checkUsername()
                app.logger.info("Instagram : Checking if handle is available....")
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
                profile_name = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ekmpd5l3 .e1457k4r8'))).text
                output = {
                    'profile_name': profile_name
                }
                app.logger.info("tiktok : Found user with that handle")
                return output
            except Exception as e:
                app.logger.info("tiktok : Couldn't find user with that handle")
                return None

        except Exception as e:
            app.logger.info(f"Unexpected error occurred : {str(e)}")


    def twitter_checker(self, handle):
        try:
            url = f'https://twitter.com/{handle}'
            self.driver.get(url)

            try:
                # following = self.driver.find_element('css selector', '.r-1mf7evn .r-b88u0q .r-qvutc0').text
                following = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.r-1mf7evn .r-b88u0q .r-qvutc0'))).text
                if not following:
                    return None

                output = {
                    'Handle': f"@{handle}"
                }
                app.logger.info("Twitter : Found user with that handle")
                return output

            except Exception as e:
                app.logger.info("Twitter : Couldn't find user with that handle")
                suspended = WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[1]/span'))).text
                if suspended.lower() == 'Account suspended'.lower():
                    app.logger.info('twitter account suspended')
                    return True
                else:
                    return None

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
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('detach', True)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(url)

    def checkUsername(self):

        try:
            cookies = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.CLASS_NAME, '_a9_1')))
            cookies.click()
        except Exception as e:
            app.logger.info(f"Cookies button not found. {str(e)} \n Continuing without clicking. ")
        try:
            email_input = WebDriverWait(self.driver, 4).until(
                EC.presence_of_element_located(((By.NAME, 'emailOrPhone')))
            )
            email_input.send_keys('quanojo@gmail.com')
            time.sleep(0.2)

            fullName_input = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.NAME, 'fullName')))
            fullName_input.send_keys('johnnypecados')
            time.sleep(0.2)

            username_input = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.NAME, 'username')))
            username_input.send_keys(self.handle)
            time.sleep(0.2)

            password_input = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.NAME, 'password')))
            password_input.send_keys('randompassword1235gndfsjaksda')

            next_button = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Next']"))).click()

            error_taken = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.ID, "ssfErrorAlert")))
            if error_taken.text == 'A user with that username already exists.' or error_taken.text == "This username isn't available. Please try another.":
                return True
            else:
                return None

        except Exception as e:
            app.logger.info("Some elements couldn't be located")
            return True

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
    valid_social_networks = ['twitter', 'instagram', 'reddit', 'tiktok', 'youtube', 'twitch'] ##Facebook removed temporarily

    if not handle:
        response_data = {'success': False,'error': {'type': 'HandleNotProvided', 'message': "Handle not provided"}}
        return jsonify(response_data), 400

    # if len(handle) < 5 and social_network == 'facebook':
    #     response_data = {'success': False, 'error': {'type': 'invalidHandle', 'message': f"Handle({str(handle)}) needs to be at least 5 characters"}}
    #     return jsonify(response_data), 400

    if not social_network:
        response_data = {'success': False, 'error': {'type': 'socialNotProvided', 'message': "social network not provided"}}
        return jsonify(response_data), 400

    if social_network not in valid_social_networks:
        response_data = {'success': False, 'error': {'type': 'invalidSocial', 'message': f"Social network is not valid, please choose a social network from this list : {valid_social_networks}"}}
        return jsonify(response_data), 400

    if social_network == "twitter":
        try:
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
            'twitter': False if social_media_checker.twitter_checker(handle) else True,
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


