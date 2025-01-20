from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers import wallet

start_router = Router()

@start_router.message(CommandStart())
async def command_start_handler(message: Message, is_new: bool = True) -> None:
    """
    Handles /start command and displays command buttons
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        *[
            InlineKeyboardButton(text="💳 Wallet", callback_data="cmd_view_wallet"),
            InlineKeyboardButton(text="📊 Limit Orders", callback_data="cmd_open_orders"),
            InlineKeyboardButton(text="📈 Buy", callback_data="cmd_buy"),
            InlineKeyboardButton(text="📈 Sell", callback_data="cmd_sell"),
            InlineKeyboardButton(text="🔄 Refresh", callback_data="cmd_refresh"),
        ]
    )
    builder.adjust(2)

    await (message.answer if is_new else message.edit_text)(
        text=f"Hello, <b>{message.from_user.full_name}</b>!\nChoose a command:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )    

@start_router.callback_query(F.data[:4] == 'cmd_')
async def process_callback(callback: CallbackQuery):
    """Handle button presses by calling appropriate handlers"""
    command = callback.data.replace('cmd_', '')
    
    match command:
        case "view_wallet":
            await wallet.command_view_wallet(callback.message, is_new=True)
        case "open_orders":
            pass
        case "buy":
            pass
        case "sell":
            pass
        case "refresh":
            pass

    await callback.answer()  # Remove loading state