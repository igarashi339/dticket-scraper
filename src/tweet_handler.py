import tweepy
import os


class TweetHandler:
    def __init__(self):
        # 土日陸海
        api_key = os.environ["TWITTER_API_KEY"]
        api_secret = os.environ["TWITTER_API_SECRET"]
        access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
        self.client = tweepy.Client(None, api_key, api_secret, access_token, access_token_secret)

        # 平日海陸
        api_key_weekday = os.environ["TWITTER_API_KEY_WEEKDAY"]
        api_secret_weekday = os.environ["TWITTER_API_SECRET_WEEKDAY"]
        access_token_weekday = os.environ["TWITTER_ACCESS_TOKEN_WEEKDAY"]
        access_token_secret_weekday = os.environ["TWITTER_ACCESS_TOKEN_SECRET_WEEKDAY"]
        self.client_weekday = tweepy.Client(None,
                                            api_key_weekday,
                                            api_secret_weekday,
                                            access_token_weekday,
                                            access_token_secret_weekday)

    def post_tweet(self, text):
        self.client.create_tweet(text=text)

    def post_tweet_weekday(self, text):
        self.client_weekday.create_tweet(text=text)