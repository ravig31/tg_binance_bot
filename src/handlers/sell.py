from decimal import Decimal

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from handlers import wallet
from binance_api import BinanceClient
import logging

logger = logging.getLogger(__name__)
sell_router = Router()

bc = BinanceClient()
sell_router = Router()

USDT = "USDT"
class OrderType:
    MARKET = "market"
    LIMIT = "limit"

class SellState(StatesGroup):
    SELECT_TYPE = State()
    AMOUNT = State()
    LIMIT_PRICE = State()

@sell_router.message(Command("sell"))
async def command_sell_handler(message: Message) -> None:
    """Display available assets for selling as interactive buttons.

    :param message: Incoming message from user
    :return: None
    """
    available_assets = wallet.build_wallet()

    builder = InlineKeyboardBuilder()
    for asset in available_assets:
        if asset.balance_usdt > 1.0 and asset.symbol != USDT:
            builder.add(
                InlineKeyboardButton(
                    text=f"{asset.symbol}", callback_data=f"sell_asset_{asset.symbol}"
                )
            )

    builder.adjust(3)
    builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data="show_start"))

    await message.answer(
        text="<b>Select asset to sell:</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )

@sell_router.callback_query(F.data.startswith("sell_asset_"))
async def show_order_type_selection(callback: CallbackQuery, state: FSMContext):
    """Show order type selection menu and asset details.

    :param callback: Callback query from the button press
    :param state: FSM context for state management
    :return: None
    """   
    symbol = callback.data.replace("sell_asset_", "")
    asset = wallet.build_wallet_item(symbol)

    # Store symbol for later use
    await state.update_data(symbol=symbol)
    await state.set_state(SellState.SELECT_TYPE)

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Market Order", callback_data=f"select_type_{symbol}_{OrderType.MARKET}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="Limit Order", callback_data=f"select_type_{symbol}_{OrderType.LIMIT}"
        )
    )
    builder.adjust(1,1,1)
    builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data="show_start"))

    await callback.message.edit_text(
        text=f"<b>🔸 Sell {asset.symbol}</b>\n\n"
        f"Available: <code>{asset.free:.8f}</code>\n"
        f"Value: <code>${asset.balance_usdt:.2f}</code>\n"
        f"Price: <code>${asset.last_price_usdt:.4f}</code>\n"
        f"LIQ: <code>${asset.available_liquidity:.4f}</code>\n"
        f"24h Change: {asset.formatted_pnl}\n\n"
        f"<b>Select order type:</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()

@sell_router.callback_query(F.data.startswith("select_type_"))
async def handle_order_type_selection(callback: CallbackQuery, state: FSMContext):
    """Process selected order type and prompt for amount input.

    :param callback: Callback query from the order type selection
    :param state: FSM context for state management
    :return: None
    """
    symbol, order_type = callback.data.replace("select_type_", "").split("_")
    
    await state.update_data(symbol=symbol, order_type=order_type)
    await state.set_state(SellState.AMOUNT)

    await callback.message.edit_text(
        text=f"<i>Enter amount of {symbol} to sell (e.g 0.0023)"
        f" or as a percentage (e.g. 20%):</i>",
        parse_mode="HTML",
    )
    await callback.answer()

@sell_router.message(SellState.AMOUNT)
async def handle_amount(message: Message, state: FSMContext):
    """Process entered amount and show appropriate order preview or prompt for limit price.

    :param message: Message containing amount input
    :param state: FSM context for state management
    :return: None
    """    
    data = await state.get_data()
    symbol = data["symbol"]
    order_type = data["order_type"]
    asset = wallet.build_wallet_item(symbol)

    try:
        if "%" in message.text:
            value = message.text[:-1]
            amount = Decimal(float(value)/100) * asset.free
        else:
            amount = float(message.text)
            if amount <= 0 or amount > asset.free:
                raise ValueError
    except ValueError:
        await message.answer("Invalid amount. Please try again.")
        return

    await state.update_data(amount=amount)

    if order_type == OrderType.MARKET:
        await show_market_order_preview(message, state, symbol, amount, asset)
    else:
        await state.set_state(SellState.LIMIT_PRICE)
        await message.answer(
            text=f"Enter limit price in USDT (current price: ${asset.last_price_usdt:.4f}):",
            parse_mode="HTML",
        )

async def show_market_order_preview(message, state, symbol, amount, asset):
    """Display market order preview with confirmation button.

    :param message: Original message for replying
    :param state: FSM context for state management
    :param symbol: Trading pair symbol
    :param amount: Order amount
    :param asset: Asset information object
    :return: None
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🔸 Sell at Market 🔸",
            callback_data=f"confirm_market_sell_{symbol}_{amount}",
        )
    )
    builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data=f"sell_asset_{symbol}"))

    await message.answer(
        text=f"<b>Market Order Preview:</b>\n\n"
        f"Sell {amount:.4f} {symbol}\n"
        f"at market price (${asset.last_price_usdt:.4f})\n"
        f"Value: ${Decimal(amount) * asset.last_price_usdt:.2f}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await state.clear()

@sell_router.message(SellState.LIMIT_PRICE)
async def handle_limit_price(message: Message, state: FSMContext):
    """Process limit price input and show limit order preview.

    :param message: Message containing limit price input
    :param state: FSM context for state management
    :return: None
    """    
    try:
        limit_price = float(message.text)
        if limit_price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Invalid price. Please enter a valid number.")
        return

    data = await state.get_data()
    symbol = data["symbol"]
    amount = data["amount"]
    asset = wallet.build_wallet_item(symbol)

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🔸 Place Limit Order 🔸",
            callback_data=f"confirm_limit_sell_{symbol}_{amount}_{limit_price}",
        )
    )
    builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data=f"sell_asset_{symbol}"))

    await message.answer(
        text=f"<b>Limit Order Preview:</b>\n\n"
        f"Sell {amount:.4f} {symbol}\n"
        f"at limit price: ${limit_price:.4f}\n"
        f"Current price: ${asset.last_price_usdt:.4f}\n"
        f"Value if filled: ${Decimal(amount) * Decimal(limit_price):.2f}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await state.clear()

@sell_router.callback_query(F.data.startswith("confirm_market_sell_"))
async def execute_market_sell(callback: CallbackQuery):
    """Execute market sell order and display confirmation.

    :param callback: Callback query from confirmation button
    :return: None
    :raises: Various exceptions from BinanceClient
    """
    symbol, amount = callback.data.replace("confirm_market_sell_", "").split("_")
    amount = float(amount)

    try:
        bc.create_sell_market_order(
            symbol=symbol,
            quantity=amount
        )
    except Exception as e:
        logger.info(e)

    await callback.message.edit_text(
        text=f"<b>Market Order Executed:</b>\n"
        f"Sold {amount:.8f} {symbol}",
        parse_mode="HTML",
    )
    await callback.answer("Order executed!")

@sell_router.callback_query(F.data.startswith("confirm_limit_sell_"))
async def execute_limit_sell(callback: CallbackQuery):
    """Execute limit sell order and display confirmation.

    :param callback: Callback query from confirmation button
    :return: None
    :raises: Various exceptions from BinanceClient
    """
    symbol, amount, price = callback.data.replace("confirm_limit_sell_", "").split("_")
    amount = float(amount)
    price = float(price)

    try:
        bc.create_sell_limit_order(
            symbol=symbol,
            quantity=amount,
            trigger_price=price
        )
    except Exception as e:
        logger.info(e)

    await callback.message.edit_text(
        text=f"<b>Limit Order Placed:</b>\n"
        f"Selling {amount:.8f} {symbol}\n"
        f"at ${price:.4f}",
        parse_mode="HTML",
    )
    await callback.answer("Limit order placed!")