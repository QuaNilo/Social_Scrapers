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

except ModuleNotFoundError:
    print("Please download dependencies from requirements.txt")
except Exception as ex:
    print(ex)

reddit = praw.Reddit(
    client_id='jscVQaT6to5MYlYkUQKMrw',
    client_secret='8gWhLHjPZrkPjhkMyc56ai_INra7MQ',
    user_agent='MyApp/1.0 by QuaNilo (geral@noop.pt)'
)
load_dotenv("variables.env")
app = Flask(__name__)


def check_if_reddit_user_exists(handle):
        redditor = reddit.redditor(handle)
        if redditor:
            print(redditor._fetch_data())
            user_data = {
                "available": "false",
                "success": "true",
                "result": {
                    "info": str(redditor._fetch_data())
                }
            }

            return jsonify(user_data)

        else:
            raise Exception(f"I fucked up : {handle}")

def check_instagram_profile_exists(handle):
    guest = Guest()
    profile = guest.profile(handle)
    print(profile)
    if profile is not None:
        json_data = {
            "available": "false",
            "success": "true",
            "result": {
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


@app.route('/check_handle', methods=['GET'])
def check_handle():
    social_network = request.args.get('social_network')
    handle = request.args.get('handle')

    if not handle:
        response_data = {"success": "false", "error": "Handle not provided"}
        return jsonify(response_data), 400

    if not social_network:
        response_data = {"success": "false", "error": "social_network not provided"}
        return jsonify(response_data), 400

    if social_network == "reddit":
        response = check_if_reddit_user_exists(handle)
        return response, 200

    if social_network == "youtube":
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=os.environ.get('API_KEY'))
            response = youtube.channels().list(
                forUsername=handle,
                part="id,snippet"
            ).execute()
            youtube.close()
            response['is_available'] = False
            # Check if any channels with the given name were found
            if response.get("items"):
                return jsonify(response)
            else:
                return jsonify({"available": "true", "success": "true"})

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None  # Error occurred

    if social_network == "instagram":
        in_use = check_instagram_profile_exists(handle)
        if in_use:
            return jsonify(in_use)
        else:
            return jsonify({"available": "true", "success": "true"})
    else:
        return jsonify({"error": "Social Network not available"}), 404

if __name__ == '__main__':
    app.run(debug=True)


