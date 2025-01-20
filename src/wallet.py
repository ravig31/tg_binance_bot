from typing import List, Dict
from decimal import Decimal

from models import UserAsset, Ticker24hrData, WalletItem
from utils import pair_ticker

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from binance_api import BinanceClient

USDT = "USDT"

wallet_router = Router()
bc = BinanceClient()


@wallet_router.message(Command("wallet"))
async def command_viewwallet(message: Message):
    user_assets: List[UserAsset] = bc.get_user_assets()
    
    filtered_symbols = [ua.symbol for ua in user_assets if ua.symbol != USDT]
    price_data: Dict[str, Ticker24hrData] = bc.get_24hr_price_data(
        [pair_ticker(symbol, USDT) for symbol in filtered_symbols]
    )
    wallet: List[WalletItem] = build_wallet(user_assets, price_data)
    
    # Sort wallet by balance
    sorted_wallet = sorted(wallet, key=lambda x: x.balance_usdt, reverse=True)

    total_balance = sum(asset.balance_usdt for asset in wallet)

    html_message = (
        f"<b>💼 Wallet Overview</b>\n"
        f"<code>Total: ${total_balance:.2f} USDT</code>\n\n"
    )

    for asset in sorted_wallet:
        # Skip small balances
        if asset.balance_usdt < 1.0:
            continue

        html_message += (
            f"<b>{asset.symbol}</b>\n"
            f"└ <code>${asset.balance_usdt:.2f}</code> "
            f"@ <code>${asset.last_price_usdt:.4f}</code>\n"
            f"└ 24h: {asset.formatted_pnl}\n\n"
        )

    # Summary footer
    displayed_assets = sum(1 for a in sorted_wallet if a.balance_usdt >= 1.0)
    total_assets = len(sorted_wallet)

    html_message += (
        f"\n<i>Showing {displayed_assets} of {total_assets} assets</i>\n"
        f"<i>Last updated: {bc.get_server_time()}</i>"
    )

    await message.answer(html_message, parse_mode="HTML")


def build_wallet(
    user_assets: List[UserAsset], 
    price_data: Dict[str, Ticker24hrData],
) -> List[WalletItem]:
    result = []
    for asset in user_assets:
        if asset.symbol != USDT:
            pd = price_data[pair_ticker(asset.symbol, USDT)]
            result.append(
                WalletItem(
                    symbol=asset.symbol,
                    free=asset.free,
                    last_price_usdt=pd.last_price,
                    available_liquidity=calculate_depth(
                        pd.bid_price, pd.bid_qty, pd.ask_price, pd.ask_qty
                    ),
                    market_cap=pd.last_price * pd.last_qty,
                    pnl_24hr_usdt=pd.price_change,
                    pnl_24hr_percentage=pd.price_change_percent,
                )
            )
        else:
            result.append(WalletItem.create_usdt_entry(asset.free))

    
    return sort_by_balance(result)


def sort_by_balance(wallet: List[WalletItem]):
    return sorted(wallet, key=lambda x: x.balance, reverse=True)


def calculate_depth(
    bid_price: Decimal, bid_qty: Decimal, ask_price: Decimal, ask_qty: Decimal
) -> Decimal:
    bid_value = bid_price * bid_qty
    ask_value = ask_price * ask_qty

    return bid_value + ask_value
