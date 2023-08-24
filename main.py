try:
    from dotenv import load_dotenv
    from ensta import Guest
    from flask import Flask, request, jsonify
    import argparse
    import json
    from selenium import webdriver
    import subprocess
    import praw
    import os
    import googleapiclient.discovery
    import googleapiclient.errors
    import prawcore
    from multiprocessing import Pool
    import requests
    import dotenv
    import requests
    from bs4 import BeautifulSoup

except ModuleNotFoundError:
    print("Please download dependencies from requirements.txt")
except Exception as ex:
    print(ex)

app = Flask(__name__)

class SocialMediaChecker:
    def __init__(self):
        load_dotenv("variables.env")

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
                return None

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")


    #TODO FIX YOUTUBE
    def youtube_checker(self, handle):
        pass
        # try:
        #     url = f'https://www.youtube.com/@{handle}'
        #
        #     driver = webdriver.Chrome()  # Replace with the appropriate WebDriver
        #     driver.get(url)
        #
        #     try:
        #         print("entered youtube")
        #         profile_name_element = driver.find_element_by_id('channel-handle')
        #         profile_name = profile_name_element.text
        #         print(f"Youtube profile name = {profile_name}")
        #         output = {
        #             'profile_name': profile_name
        #         }
        #         driver.quit()
        #         return output
        #     except Exception as e:
        #         driver.quit()
        #         return None
        #
        # except Exception as e:
        #     print(f"Unexpected error occurred : {str(e)}")

    def tiktok_checker(self, handle):
        try:
            url = f'https://www.tiktok.com/@{handle}'

            driver = webdriver.Chrome()  # Replace with the appropriate WebDriver
            driver.get(url)

            try:
                profile_name_element = driver.find_element('css selector', '.ekmpd5l3 .e1457k4r8')
                profile_name = profile_name_element.text
                output = {
                    'profile_name': profile_name
                }
                driver.quit()
                return output
            except Exception as e:
                driver.quit()
                return None

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")


    def twitter_checker(self, handle):
        try:
            url = f'https://twitter.com/{handle}'

            driver = webdriver.Chrome()  # Replace with the appropriate WebDriver
            driver.get(url)

            try:
                profile_name_element = driver.find_element('css selector', '.r-1w6e6rj')
                not_found = profile_name_element.text
                if not not_found:
                    return None
                output = {
                    'Handle': f"@{handle}"
                }
                driver.quit()
                return output
            except Exception as e:
                driver.quit()
                return None

        except Exception as e:
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

            driver = webdriver.Chrome()  # Replace with the appropriate WebDriver
            driver.get(url)

            try:
                profile_name_element = driver.find_element('css selector', '._391s')
                profile_name = profile_name_element.text
                output = {
                    'profile_name': profile_name
                }
                driver.quit()
                return output
            except Exception as e:
                driver.quit()
                return None

        except Exception as e:
            print(f"Unexpected error occurred : {str(e)}")


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

    if not handle:
        response_data = {"success": "false", "error": "Handle not provided"}
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

    pool = Pool(processes=7)  # Number of processes for parallel processing
    results = pool.starmap(check_single_handle, [(handle, social_media_checker)])
    pool.close()
    pool.join()

    return jsonify(results[0]), 200

def check_single_handle(handle, social_media_checker):
    results = {
        'success': True,
        'data': {
            ##True if available, False if not available
            'twitter': False if social_media_checker.twitter_checker(handle) else True,
            'facebook': False if social_media_checker.facebook_checker(handle) else True,
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


