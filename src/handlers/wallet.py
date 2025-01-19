from typing import List

from models import WalletAsset

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from binance_api import BinanceClient
import json

wallet_router = Router()
bc = BinanceClient()

@wallet_router.message(Command("wallet"))
async def command_viewwallet(message: Message):
    wallet: List[WalletAsset] = bc.get_user_assets()
     

    html_message = "<b>📊 Your Wallet Balance</b>\n\n"
    
    for asset in wallet:
        # Skip assets with 0 balance
        if  asset.free == 0 and asset.locked == 0:
            continue
            
        html_message += (
            f"<b>{asset}</b>\n"
            f"├ Free: <code>{asset.free}</code>\n"
            f"└ Locked: <code>{asset.free}</code>\n\n"
        )
    
    # Add timestamp
    html_message += f"\n<i>Last updated: {bc.get_server_time()}</i>"
    
    await message.answer(
        html_message,
        parse_mode="HTML"
    )

