from typing import List, Dict
from decimal import Decimal

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from models import UserAsset, Ticker24hrData, WalletItem
from binance_api import BinanceClient
from handlers import start
import utils


USDT = "USDT"

wallet_router = Router()
bc = BinanceClient()


@wallet_router.message(Command("wallet"))
async def command_show_wallet(message: Message, is_new: bool = False):
    wallet: List[WalletItem] = build_wallet()
    total_balance = sum(asset.balance_usdt for asset in wallet)
    html_message = (
        f"<b>💼 Wallet Overview</b>\n"
        f"<code>Total: ${total_balance:.2f} USDT</code>\n\n"
    )

    for asset in wallet:
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
    displayed_assets = sum(1 for a in wallet if a.balance_usdt >= 1.0)
    total_assets = len(wallet)

    html_message += (
        f"\n<i>Showing {displayed_assets} of {total_assets} assets</i>\n"
        f"<i>Last updated: {bc.get_server_time()}</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        *[
            InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_wallet"),
            InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_start"),
        ]
    )

    await (message.answer if is_new else message.edit_text)(
        html_message, parse_mode="HTML", reply_markup=builder.as_markup()
    )


@wallet_router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await start.command_start_handler(callback.message, is_new=False)
    await callback.answer()


@wallet_router.callback_query(F.data == "refresh_wallet")
async def refresh_wallet(callback: CallbackQuery):
    await command_show_wallet(callback.message, is_new=False)
    await callback.answer()


def build_wallet() -> List[WalletItem]:
    user_assets: List[UserAsset] = bc.get_user_assets()
    filtered_symbols = [ua.symbol for ua in user_assets if ua.symbol != USDT]
    price_data: Dict[str, Ticker24hrData] = bc.get_24hr_price_data(
        [utils.pair_ticker(symbol, USDT) for symbol in filtered_symbols]
    )
    result = []
    for asset in user_assets:
        if asset.symbol != USDT:
            pd = price_data[utils.pair_ticker(asset.symbol, USDT)]
            result.append(
                WalletItem(
                    symbol=asset.symbol,
                    free=asset.free,
                    last_price_usdt=pd.last_price,
                    available_liquidity=calculate_depth(
                        pd.bid_price, pd.bid_qty, pd.ask_price, pd.ask_qty
                    ),
                    pnl_24hr_usdt=pd.price_change,
                    pnl_24hr_percentage=pd.price_change_percent,
                )
            )
        else:
            result.append(WalletItem.create_usdt_entry(asset.free))

    return sorted(result, key=lambda x: x.balance_usdt, reverse=True)


def build_wallet_item(symbol: str) -> WalletItem:
    asset: UserAsset = bc.get_user_asset(symbol)
    pd: Ticker24hrData = bc.get_24hr_price_data_single(utils.pair_ticker(symbol, USDT))

    return WalletItem(
        symbol=asset.symbol,
        free=asset.free,
        last_price_usdt=pd.last_price,
        available_liquidity=calculate_depth(
            pd.bid_price, pd.bid_qty, pd.ask_price, pd.ask_qty
        ),
        pnl_24hr_usdt=pd.price_change,
        pnl_24hr_percentage=pd.price_change_percent,
    )

def calculate_depth(
    bid_price: Decimal, bid_qty: Decimal, ask_price: Decimal, ask_qty: Decimal
) -> Decimal:
    bid_value = bid_price * bid_qty
    ask_value = ask_price * ask_qty

    return bid_value + ask_value
