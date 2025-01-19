from typing import List
import datetime as dt

from binance.spot import Spot
from dotenv import load_dotenv
from os import getenv

from models import UserAsset
import utils

load_dotenv()
API_KEY = getenv("BINANCE_TOKEN")
API_SECRET = getenv("BINANCE_SECRET")


class BinanceClient():
    def __init__(self):
        self.client = Spot(api_key=API_KEY, api_secret=API_SECRET) 

    def get_user_assets(self) -> List[UserAsset]:
        wallet_json =  self.client.user_asset()

        result = []
        for asset in wallet_json:
            result.append(UserAsset.from_dict(asset))
    
        return result


    def get_(self, symbols: str | List[str]):
        return self.client.ticker_24hr(symbols)


    def get_server_time(self):
        ts = self.client.time()['serverTime']
        return utils.unix_to_datetime(ts, True)