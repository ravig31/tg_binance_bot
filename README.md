# Crypto Trading Bot

A Telegram bot for managing your Binance crypto portfolio and executing trades.

## Setup Instructions

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- aiogram==3.3.0
- python-binance==1.0.19
- python-dotenv==1.0.0

### 2. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Save the bot token provided by BotFather

### 3. Get Binance API Keys

1. Log in to your [Binance Account](https://www.binance.com/en/my/settings/api-management)
2. Create a new API key
3. Enable following permissions:
   - Enable Reading
   - Enable Spot & Margin Trading
4. Save your API key and Secret key

### 4. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
# Telegram Bot Token
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Binance API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# Optional: Test Mode (set to True for testnet)
TEST_MODE=False
```

### 5. Run the Bot

```bash
python run_tg.py
```

## Usage

Once running, open your Telegram bot and send:
- `/start` - View main menu
- `/wallet` - Check portfolio balance
- `/sell` - Create sell orders
