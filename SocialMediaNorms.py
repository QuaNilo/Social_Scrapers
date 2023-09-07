import re


class SocialMediaHandleValidator:

    def __init__(self, username):
        self.username = username

    def _is_valid_length(self, min_length, max_length):
        return min_length <= len(self.username) <= max_length

    def is_valid_twitter_handle(self):
        if not self._is_valid_length(4, 15):
            return False
        pattern = r"^[a-zA-Z0-9._]+$"
        return bool(re.match(pattern, self.username))

    def is_valid_instagram_handle(self):
        if not self._is_valid_length(4, 30):
            return False
        pattern = r"^[a-zA-Z0-9_.]+$"
        return bool(re.match(pattern, self.username))

    def is_valid_facebook_handle(self):
        if not self._is_valid_length(5, 50):
            return False
        # Updated pattern to allow alphanumeric characters and periods but not generic terms or extensions
        pattern = r"^(?!.*(?:\.com|\.net))[a-zA-Z0-9.]+$"
        return bool(re.match(pattern, self.username))

    def is_valid_reddit_handle(self):
        if not self._is_valid_length(2, 21):
            return False
        pattern = r"^[a-zA-Z0-9_-]+$"
        return bool(re.match(pattern, self.username))

    def is_valid_tiktok_handle(self):
        if not self._is_valid_length(4, 24):
            return False
        pattern = r"^[a-zA-Z0-9._]+$"
        return bool(re.match(pattern, self.username))
    def is_valid_twitch_handle(self):
        if not self._is_valid_length(4, 26):
            return False
        pattern = r"^[a-zA-Z0-9_]+$"
        return bool(re.match(pattern, self.username))

    def is_valid_youtube_handle(self):
        if not self._is_valid_length(4, 50):
            return False
        # Pattern allowing letters, numbers, spaces, and periods
        pattern = r"^[a-zA-Z0-9 .]+$"
        return bool(re.match(pattern, self.username))