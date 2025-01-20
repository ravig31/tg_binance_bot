from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from handlers import wallet, trade

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
            InlineKeyboardButton(text="📈 Sell", callback_data="cmd_sell"),
        ]
    )
    builder.adjust(1,1,1)
    await (message.answer if is_new else message.edit_text)(
        text=f"Hello, <b>{message.from_user.full_name}</b>!\nChoose a command:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )

@start_router.callback_query(F.data[:4] == 'cmd_')
async def process_callback(callback: CallbackQuery, state: FSMContext):
    """Handle button presses by calling appropriate handlers"""
    command = callback.data.replace('cmd_', '')
    
    match command:
        case "view_wallet":
            await wallet.command_show_wallet(callback.message, is_new=True)
        case "sell":
            await trade.command_sell_handler(callback.message)
            
    await callback.answer()