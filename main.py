try:
    from dotenv import load_dotenv
    from ensta import Guest
    from flask import Flask, request, jsonify
    import snscrape.modules.twitter as twitter
    import pandas as pd
    import argparse
    import json
    import selenium
    import subprocess
    import praw
    import os
    import googleapiclient.discovery
    import googleapiclient.errors
    import prawcore
    import requests
    from bs4 import BeautifulSoup

except ModuleNotFoundError:
    print("Please download dependencies from requirements.txt")
except Exception as ex:
    print(ex)

app = Flask(__name__)

class SocialMediaChecker:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id='jscVQaT6to5MYlYkUQKMrw',
            client_secret='8gWhLHjPZrkPjhkMyc56ai_INra7MQ',
            user_agent='MyApp/1.0 by QuaNilo (geral@noop.pt)'
        )
        load_dotenv("variables.env")
        self.guest = Guest()

    def reddit_checker(self, handle):
        try:
            redditor = self.reddit.redditor(handle)
            if redditor:
                user_data = {
                    "is_available": False,
                    "success": True,
                    "data": {
                        "response": str(redditor._fetch_data())
                    }
                }
                return jsonify(user_data)
        except prawcore.exceptions.NotFound:
            return False

    def instagram_checker(self, handle):
        profile = self.guest.profile(handle)
        if profile is not None:
            json_data = {
                "is_available": False,
                "success": True,
                "response": {
                    "handle": handle,
                    "full_name": profile.full_name,
                    "biography": profile.biography,
                    "followers": profile.follower_count,
                    "following": profile.following_count
                }
            }
            return json_data
        else:
            return False

    def youtube_checker(self, handle):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=os.environ.get('yt_API_KEY'))
            response = youtube.channels().list(
                forUsername=handle,
                part="id,statistics,status,snippet"
            ).execute()
            youtube.close()

            if response.get("items"):
                output = {
                    'success': True,
                    'is_available': False,
                    'data': {
                        'response': response
                    }
                }
                return output
            else:
                return False

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def tiktok_checker(self, handle):
        pass
        """session = requests.Session()
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US",
            "content-type": "application/json"
        }
        c = session.get(f'https://www.tiktok.com/@{handle}', headers=headers, timeout=60)
        check = c.status_code
        if c.status_code == 200:
            soup = BeautifulSoup(c.content, "html.parser")
            # Look for elements that indicate the existence of the account
            account_not_found = soup.find("h1", text="This page isn't available.")
            print(soup.text)
            if account_not_found:
                output = {
                    'success': True,
                    'is_available': True,
                }
                return output
            else:
                return False
        else:
            raise Exception("Unexpected error")"""

    def twitch_checker(self,handle):
        twitch = TwitchAPI(client_id='dd4yshe8vdg2j78mk6wqf3896ggn75', client_secret='qjm1y37x6840c60y3fb4qk1rf2sg9d')
        response = twitch.check_user(handle)
        if response.status_code:
            output = {
                'success': True,
                'is_available': False,
                'response': response.json()
            }
            return output
        else:
            return False

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


    if social_network == "reddit":
        response = social_media_checker.reddit_checker(handle)
        if response:
            return response, 200
        else:
            return jsonify({"available": "true", "success": "true"})


    if social_network == 'tiktok':
        response = social_media_checker.tiktok_checker(handle)
        if response:
            return response, 200
        else:
            return jsonify({'success': False, 'error': "Unexpected error occurred"})

    if social_network == 'twitch':
        response = social_media_checker.twitch_checker(handle)
        if response:
            return response, 200
        else:
            return jsonify({'success': False, 'error': "Unexpected error occurred"})


    if social_network == "youtube":
        try:
            response = social_media_checker.youtube_checker(handle)
            if response:
                return response, 200
            else:
                return jsonify({"available": "true", "success": "true"})
        except Exception as e:
            return {'success': False, 'error': str(e)}

    if social_network == "instagram":
        in_use = social_media_checker.instagram_checker(handle)
        if in_use:
            return jsonify(in_use)
        else:
            return jsonify({"available": "true", "success": "true"})
    else:
        return jsonify({"error": "Social Network not available"}), 404

if __name__ == '__main__':
    app.run(debug=True)


