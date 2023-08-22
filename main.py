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
            return None

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
                return jsonify({"available": True, "success": True})

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None



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


