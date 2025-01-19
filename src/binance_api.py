from binance.spot import Spot
from dotenv import load_dotenv
from os import getenv
import datetime as dt

load_dotenv()
API_KEY = getenv("BINANCE_TOKEN")
API_SECRET = getenv("BINANCE_SECRET")


class BinanceClient():
    def __init__(self):
        self.client = Spot(api_key=API_KEY, api_secret=API_SECRET) 

    def get_wallet(self):
        return self.client.user_asset()



