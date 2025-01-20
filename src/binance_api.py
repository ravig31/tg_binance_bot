from typing import List
import datetime as dt

from binance.spot import Spot
from dotenv import load_dotenv
from os import getenv

from models import UserAsset, Ticker24hrData
import utils

load_dotenv()
API_KEY = getenv("BINANCE_TOKEN")
API_SECRET = getenv("BINANCE_SECRET")


class BinanceClient():
    def __init__(self):
        self.client = Spot(api_key=API_KEY, api_secret=API_SECRET) 

    def get_user_assets(self) -> List[UserAsset]:
        wallet_json =  self.client.user_asset()
        return [UserAsset(**x) for x in wallet_json]


    def get_24hr_price_data(self, pairs: List[str]) -> List[Ticker24hrData]:
        price_data_json = self.client.ticker_24hr(symbols=pairs)
        return {x['symbol'] : Ticker24hrData(**x) for x in price_data_json}


    def get_server_time(self):
        ts = self.client.time()['serverTime']
        return utils.unix_to_datetime(ts, True)