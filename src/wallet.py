from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from binance_api import BinanceClient

import json
wallet_router = Router()

bc = BinanceClient()

@wallet_router.message(Command("wallet"))
async def command_viewwallet(message: Message):
    await message.answer(json.dumps(bc.get_wallet()))