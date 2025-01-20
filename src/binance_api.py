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


class BinanceClient:
    def __init__(self):
        self.client = Spot(api_key=API_KEY, api_secret=API_SECRET)

    def create_sell_limit_order(
        self,
        symbol: str,
        quantity: float,
        trigger_price: float,
        time_in_force: str = "GTC",
    ):
        return self.client.new_order(
            symbol=symbol,
            side="SELL",
            type="LIMIT",
            quantity=quantity,
            price=trigger_price,
            timeInForce=time_in_force,
            newOrderRespType="RESULT"
        )

    def create_sell_market_order(
        self,
        symbol: str,
        quantity: float,
    ):
        return self.client.new_order(
            symbol=symbol,
            side="SELL",
            type="MARKET",
            quantity=quantity,
            newOrderRespType="RESULT"
        )


    def get_user_asset(self, symbol: str) -> UserAsset:
        single_asset_json = self.client.user_asset(asset=symbol)[0]
        return UserAsset(**single_asset_json)

    def get_user_assets(self) -> List[UserAsset]:
        wallet_json = self.client.user_asset()
        return [UserAsset(**x) for x in wallet_json]

    def get_24hr_price_data_single(self, pair: str) -> Ticker24hrData:
        price_data_json = self.client.ticker_24hr(symbol=pair)
        return Ticker24hrData(**price_data_json)

    def get_24hr_price_data(self, pairs: List[str] | str) -> List[Ticker24hrData]:
        if isinstance(pairs, str):
            pairs = [pairs]
        price_data_json = self.client.ticker_24hr(symbols=pairs)
        return {x["symbol"]: Ticker24hrData(**x) for x in price_data_json}

    def get_server_time(self):
        ts = self.client.time()["serverTime"]
        return utils.unix_to_datetime(ts, True)
