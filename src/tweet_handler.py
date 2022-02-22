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

        # 土日陸
        api_key_holiday_land = os.environ["TWITTER_API_KEY_HOLIDAY_LAND"]
        api_secret_holiday_land = os.environ["TWITTER_API_SECRET_HOLIDAY_LAND"]
        access_token_holiday_land = os.environ["TWITTER_ACCESS_TOKEN_HOLIDAY_LAND"]
        access_token_secret_holiday_land = os.environ["TWITTER_ACCESS_TOKEN_SECRET_HOLIDAY_LAND"]
        self.client_holiday_land = tweepy.Client(None,
                                                 api_key_holiday_land,
                                                 api_secret_holiday_land,
                                                 access_token_holiday_land,
                                                 access_token_secret_holiday_land)

    def post_tweet(self, text):
        self.client.create_tweet(text=text)

    def post_tweet_holiday_land(self, text):
        self.client_holiday_land.create_tweet(text=text)