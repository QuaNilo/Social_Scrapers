try:
    from dotenv import load_dotenv
    from ensta import Guest
    from flask import Flask, request, jsonify
    import argparse
    import json
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support import expected_conditions as EC
    import subprocess
    import praw
    import time
    import os
    import googleapiclient.discovery
    import googleapiclient.errors
    from googleapiclient.discovery import build
    import prawcore
    from multiprocessing import Pool
    import requests
    import dotenv
    import chromedriver_binary
    import requests
    from bs4 import BeautifulSoup

except ModuleNotFoundError:
    print("Please download dependencies from requirements.txt")
except Exception as ex:
    print(ex)

app = Flask(__name__)

class SocialMediaChecker:
    def __init__(self):
        self.initdriver()
        load_dotenv("variables.env")
    def initdriver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('detach', False)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


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
                return user_data

        except prawcore.exceptions.NotFound:
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
                return json_data
            else:
                instagram = Instagram(handle)
                response = instagram.checkUsername()
                if response:
                    json_data = {
                        "handle": handle,
                        'response': 'It may mean that the name was used before and the account was suspended or removed from Instagram, or that the username is not allowed, or that it is simply not available for use.'
                    }
                    return json_data
                else:
                    return None

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")

    def youtube_checker(self, handle):
        try:
            API_KEY = os.environ.get('yt_API_KEY')

            youtube = build('youtube', 'v3', developerKey=API_KEY)
            response = youtube.search().list(
                part='id,snippet',
                q=handle,
                type='channel'
            ).execute()

            print(response)
            if 'items' in response and len(response['items']) > 0:
                channel = response['items'][0]
                print(channel)
                channel_id = channel['id']['channelId']
                channel_title = channel['snippet']['title']
                channel_description = channel['snippet']['description']
                print(f"Channel '{channel_title}' with ID '{channel_id}' exists.")

                output = {
                    'channel_id': channel_id,
                    'channel_name': handle,
                    'channel_title': channel_title
                }
                return output

            else:
                print(f"Channel '{handle}' does not exist.")
                return None

        except Exception as e:
            print(f'Error : {str(e)}')

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")

    def tiktok_checker(self, handle):
        try:
            url = f'https://www.tiktok.com/@{handle}'
            self.driver.get(url)

            try:
                profile_name_element = self.driver.find_element('css selector', '.ekmpd5l3 .e1457k4r8')
                profile_name = profile_name_element.text
                output = {
                    'profile_name': profile_name
                }
                return output
            except Exception as e:
                return None

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")


    def twitter_checker(self, handle):
        try:
            url = f'https://twitter.com/{handle}'
            self.driver.get(url)

            try:
                profile_name_element = self.driver.find_element('css selector', '.r-1w6e6rj')
                not_found = profile_name_element.text
                if not not_found:
                    return None
                output = {
                    'Handle': f"@{handle}"
                }
                return output
            except Exception as e:
                return None

        except Exception as e:
            self.driver.quit()
            print(f"Unexpected error occurred : {str(e)}")



    def twitch_checker(self,handle):
        try:
            twitch = TwitchAPI(client_id=os.environ.get('twitch_client_id'), client_secret=os.environ.get('twitch_client_secret'))
            response = twitch.check_user(handle)
            data = response.json()
            if data['data']:
                output = {
                    'response': response.json()
                }
                return output
            else:
                return None

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")

    def facebook_checker(self,handle):
        try:
            url = f'https://m.facebook.com/{handle}'
            self.driver.get(url)

            try:
                profile_name_element = self.driver.find_element('css selector', '._391s')
                profile_name = profile_name_element.text
                output = {
                    'profile_name': profile_name
                }
                return output
            except Exception as e:
                return None

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")

class Instagram():

    def __init__(self, handle):
        self.handle = handle
        self.init_driver()

    def init_driver(self):
        url = 'https://www.instagram.com/accounts/emailsignup/'
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('detach', True)
        self.driver = driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(url)

    def checkUsername(self):

        try:
            cookies = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, '_a9_1')))
            cookies.click()
        except Exception as e:
            print(f"Cookies button not found. Continuing without clicking. {str(e)}")

        email_input = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located(((By.NAME, 'emailOrPhone')))
        )
        email_input.send_keys('quanojo@gmail.com')
        time.sleep(0.2)

        fullName_input = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.NAME, 'fullName')))
        fullName_input.send_keys('johnnypecados')
        time.sleep(0.2)

        username_input = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.NAME, 'username')))
        username_input.send_keys(self.handle)
        time.sleep(0.2)

        password_input = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.NAME, 'password')))
        password_input.send_keys('randompassword1235gndfsjaksda')

        next_button = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Next']"))).click()

        error_taken = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.ID, "ssfErrorAlert")))
        print(error_taken.text)
        if error_taken.text == 'A user with that username already exists.':
            return True
        else:
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
                print("Access token not found in response.")
                return jsonify('FAILED TO GET ACCESS_TOKEN'), 500
        else:
            print("Token request failed with status code:", tokenResponse.status_code)
            return jsonify("Token request failed with status code:", tokenResponse.status_code), 500


@app.route('/check_handle', methods=['GET'])
def check_handle():
    social_network = request.args.get('social_network')
    handle = request.args.get('handle')
    social_media_checker = SocialMediaChecker()

    if len(handle) < 5 and social_network == 'facebook':
        response_data = {"success": False, "error": "Handle needs to be at least 5 characters"}
        return jsonify(response_data), 400

    if not handle:
        response_data = {"success": False, "error": "Handle not provided"}
        return jsonify(response_data), 400

    if not social_network:
        response_data = {"success": "false", "error": "social_network not provided"}
        return jsonify(response_data), 400

    if social_network == "twitter":
        response = social_media_checker.twitter_checker(handle)
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

    if social_network == "reddit":
        response = social_media_checker.reddit_checker(handle)
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

    if social_network == 'tiktok':
        response = social_media_checker.tiktok_checker(handle)
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

    if social_network == 'twitch':
        response = social_media_checker.twitch_checker(handle)
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

    if social_network == "youtube":
        try:
            response = social_media_checker.youtube_checker(handle)
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
            return {'success': False, 'error': str(e)}

    if social_network == "facebook":
        try:
            response = social_media_checker.facebook_checker(handle)
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
            return {'success': False, 'error': str(e)}

    if social_network == "instagram":
        response = social_media_checker.instagram_checker(handle)
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
            return jsonify({"available": "true", "success": "true"})
    else:
        return jsonify({"success": False,"error": "Social Network not available"}), 404


@app.route('/checkall_handle', methods=['GET'])
def checkall_handle():
    handle = request.args.get('handle')
    social_media_checker = SocialMediaChecker()
    results = check_single_handle(handle, social_media_checker)
    return jsonify(results), 200

def check_single_handle(handle, social_media_checker):
    results = {
        'success': True,
        'data': {
            ##True if available, False if not available
            'twitter': False if social_media_checker.twitter_checker(handle) else True,
            'facebook': False if social_media_checker.facebook_checker(handle) or len(handle) < 5 else True,
            'reddit': False if social_media_checker.reddit_checker(handle) else True,
            'tiktok': False if social_media_checker.tiktok_checker(handle) else True,
            'youtube': False if social_media_checker.youtube_checker(handle) else True,
            'instagram': False if social_media_checker.instagram_checker(handle) else True,
            'twitch': False if social_media_checker.twitch_checker(handle) else True
        }
    }
    return results



if __name__ == '__main__':
    app.run(debug=True)


