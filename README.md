# Telegram Crypto Exchange Bot

A Telegram-based cryptocurrency exchange simulator built with Python and MySQL.
This bot allows users to register, create a personal wallet, track real-time
cryptocurrency prices, manage balances, and perform simulated buy, sell, and
transfer operations directly inside Telegram.

--------------------------------------------------

FEATURES

- User registration system with MySQL persistence
- Personal wallet creation for each registered user
- Real-time cryptocurrency prices using CoinGecko API
- Supported cryptocurrencies: BTC, ETH, USDT
- Wallet balance management (USD and crypto assets)
- Simulated trading operations:
  - Buy cryptocurrency
  - Sell cryptocurrency
  - Transfer cryptocurrency between wallets
  - Increase wallet USD balance
- Multi-step (stateful) user interaction
- Multi-language support (English / Persian)
- Transaction validation and balance checking
- Logging and error handling

--------------------------------------------------

TECHNOLOGIES USED

- Python
- Telebot (pyTelegramBotAPI)
- MySQL
- CoinGecko API
- Regular Expressions (wallet validation)
- Logging

--------------------------------------------------

PROJECT STRUCTURE

Telegram_Bot/
|
|-- Ali_Heravi_main.py      Main bot logic and command handlers
|-- Database.py             Database operations and queries
|-- How_to_use_bot.pdf      User guide and instructions
|-- EER_Database.pdf        Database design (EER diagram)
|-- bot.log                 Log file
|-- README.md

--------------------------------------------------

AVAILABLE COMMANDS

/start              Start the bot and choose language
/help               Show available commands
/register            Register a new user
/create_wallet       Create a personal wallet
/check_balance       Check wallet balances
/get_price_cryptos   Get real-time crypto prices
/buy_crypto          Buy cryptocurrency
/sell_crypto         Sell cryptocurrency
/transfer_crypto     Transfer crypto to another wallet
/increase_balance    Increase wallet USD balance

--------------------------------------------------

DATABASE OVERVIEW

The project uses MySQL to store and manage:
- User information
- Wallet addresses
- USD and cryptocurrency balances
- Transaction records

The database schema and relationships are documented in the EER_Database.pdf file.

--------------------------------------------------

SETUP AND INSTALLATION

1. Clone the repository:
   git clone https://github.com/Ali-hrv/Telegram_Bot.git
   cd Telegram_Bot

2. Install required dependencies:
   pip install pyTelegramBotAPI mysql-connector-python requests

3. Configure database credentials inside the project:
   user="root"
   password="password"
   host="localhost"
   database="register"

4. Set your Telegram Bot API token:
   API_TOKEN = "YOUR_BOT_TOKEN"

5. Run the bot:
   python Ali_Heravi_main.py

--------------------------------------------------

DISCLAIMER

This project is a simulation only and does NOT perform real cryptocurrency
transactions. It is intended for educational purposes and for demonstrating
Telegram bot development, database integration, and financial system logic.

--------------------------------------------------

LICENSE

This project is open-source and available for educational and personal use.
