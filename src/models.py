from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field, validate_call

class UserAsset(BaseModel):
    symbol: str = Field(alias="asset")
    free: Decimal
    locked: Decimal = Field(default=Decimal('0'))
    freeze: Decimal = Field(default=Decimal('0'))
    withdrawing: Decimal = Field(default=Decimal('0'))
    btc_valuation: Decimal = Field(alias="btcValuation", default=Decimal('0'))

class Ticker24hrData(BaseModel):
    symbol: str
    price_change: Decimal = Field(alias="priceChange")
    price_change_percent: Decimal = Field(alias="priceChangePercent")
    weighted_avg_price: Decimal = Field(alias="weightedAvgPrice")
    prev_close_price: Decimal = Field(alias="prevClosePrice")
    last_price: Decimal = Field(alias="lastPrice")
    last_qty: Decimal = Field(alias="lastQty")
    bid_price: Decimal = Field(alias="bidPrice")
    bid_qty: Decimal = Field(alias="bidQty")
    ask_price: Decimal = Field(alias="askPrice")
    ask_qty: Decimal = Field(alias="askQty")
    open_price: Decimal = Field(alias="openPrice")
    high_price: Decimal = Field(alias="highPrice")
    low_price: Decimal = Field(alias="lowPrice")
    volume: Decimal
    quote_volume: Decimal = Field(alias="quoteVolume")
    open_time: datetime = Field(alias="openTime")
    close_time: datetime = Field(alias="closeTime")
    first_id: int = Field(alias="firstId")
    last_id: int = Field(alias="lastId")
    count: int


    @validate_call
    def convert_timestamp(cls, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value / 1000)
        return value
    
class WalletItem(BaseModel):
    symbol: str
    free: Decimal
    last_price_usdt: Decimal
    available_liquidity: Decimal
    pnl_24hr_usdt: Decimal
    pnl_24hr_percentage: Decimal

    @property
    def balance_usdt(self) -> Decimal:
        """Balance in USDT terms"""
        return self.free * self.last_price_usdt
    
    @property
    def personal_pnl_usdt(self) -> Decimal:
        """Calculate PnL in USDT relative to user's balance"""
        return self.balance_usdt * (self.pnl_24hr_percentage / 100)
    
    @property
    def formatted_pnl(self) -> str:
        """Returns formatted PnL with color indicator"""
        color = "🟢" if self.pnl_24hr_percentage > 0 else "🔴"
        return (
            f"{color} {self.pnl_24hr_percentage:+.2f}% "
            f"(${self.personal_pnl_usdt:+.2f})"
        )
    @classmethod
    def create_usdt_entry(cls, free: float) -> 'WalletItem':
        """
        Create a WalletItem for USDT (quote currency).
        """
        return cls(
            symbol="USDT",
            free=free,
            last_price_usdt=Decimal('1'),
            available_liquidity=Decimal('999999999'),
            pnl_24hr_usdt=Decimal('0'),
            pnl_24hr_percentage=Decimal('0')
        )

class Order(BaseModel):
    symbol: str
    order_id: int = Field(alias="orderId")
    order_list_id: int = Field(alias="orderListId")
    client_order_id: str = Field(alias="clientOrderId")
    trans_time: datetime = Field(alias="transactTime")
    price: Decimal = Field(alias="price")
    orig_qty: Decimal = Field(alias="origQty")
    executed_qty: Decimal = Field(alias="executedQty")
    orig_quote_order_qty: Decimal = Field(alias="origQuoteOrderQty")
    cummulative_quote_qty: Decimal = Field(alias="cummulativeQuoteQty")
    status: str
    time_in_force: str = Field(alias="timeInForce")
    type: str
    side: str
    working_time: datetime = Field(alias="workingTime")
    self_trade_prevention_mode: str = Field(alias="selfTradePreventionMode")

    class Config:
        populate_by_name = True  # Allows populating by aliased or non-aliased names
        json_encoders = {
            Decimal: str  # Ensures Decimals are serialized as strings
        }