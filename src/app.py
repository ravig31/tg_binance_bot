import asyncio
import logging
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.wallet import wallet_router
from handlers.start import start_router
from handlers.sell import sell_router
import bot_logger


load_dotenv()
TOKEN = getenv("BOT_TOKEN")

async def main() -> None:
    # Set up logging
    bot_logger.setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting bot...")
    
    # Dispatcher is a root router
    dp = Dispatcher()
    dp.include_routers(
        start_router,
        wallet_router,
        sell_router
    )
    
    bot = Bot(
        token=TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    logger.info("Bot initialized, starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())