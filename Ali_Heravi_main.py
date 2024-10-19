import telebot
import requests
import logging
import time
import mysql.connector
import re
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.util import antiflood


logging.basicConfig(filename="bot.log", filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = "API TOKEN"
bot = telebot.TeleBot(API_TOKEN)

db = mysql.connector.connect(user="root", password="password", host="localhost", database="register")
cursor = db.cursor()
hideboard = ReplyKeyboardRemove()
channel_id = -1002176384202
commands = {
    "start": "Start the bot",
    "help": "Show menu for user",
    "get_price_cryptos": "Get current price of cryptos",
    "register": "Register user",
    "create_wallet": "Create a wallet address",
    "check_balance": "Check your wallet balance",
    "buy_crypto": "Buy cryptocurrency",
    "sell_crypto": "Sell cryptocurrency",
    "transfer_crypto": "Transfer cryptocurrency to another wallet",
    "increase_balance": "Increase your wallet balance"
}

translations = {
    "en": {
        "start": "Welcome to the bot.",
        "help": "Use the following commands:\n",
        "get_price_cryptos": "CryptoCurrencies price by their rank",
        "choose_language": "Please choose your language: ",
        "en_selected": "Language set to English.",
        "fa_selected": "Language set to Persian.",
        "registration_success": "You have been successfully registered!",
        "wallet_created": "Your wallet address has been created: {}",
        "need_registration": "Please register to use this command.",
        "already_registered": "You are already registered.",
        "register": "Register user",
        "create_wallet": "Create a new wallet",
        "usd_balance": "Your wallet balance in USD: ${}",
        "crypto_balance": "Your wallet balance in crypto: {}",
        "buy_success": "You have successfully bought {} {}.",
        "sell_success": "You have successfully sold {} {}.",
        "transfer_success": "You have successfully transferred {} {} to wallet {}.",
        "not_enough_balance": "You do not have enough balance to complete this transaction."
    },
    "fa": {
        "start": "به ربات خوش آمدید.",
        "help": "از دستورات زیر استفاده کنید:\n",
        "get_price_cryptos": "قیمت ارزهای دیجیتال بر اساس رتبه:",
        "choose_language": "لطفاً زبان خود را انتخاب کنید: ",
        "en_selected": "زبان به انگلیسی تنظیم شد.",
        "fa_selected": "زبان به فارسی تنظیم شد.",
        "registration_success": "شما با موفقیت ثبت نام شدید!",
        "wallet_created": "آدرس ولت شما ایجاد شد: {}",
        "need_registration": "لطفاً برای استفاده از این دستور ثبت نام کنید.",
        "already_registered": "شما قبلاً ثبت نام کرده‌اید.",
        "register": "ثبت‌نام کاربر",
        "create_wallet": "ایجاد یک ولت جدید",
        "usd_balance": "موجودی ولت شما به دلار: ${}",
        "crypto_balance": "موجودی ولت شما به رمز ارز: {}",
        "buy_success": "شما با موفقیت {} {} خریداری کردید.",
        "sell_success": "شما با موفقیت {} {} فروختید.",
        "transfer_success": "شما با موفقیت {} {} به ولت {} انتقال دادید.",
        "not_enough_balance": "شما موجودی کافی برای انجام این معامله ندارید."
    }
}

user_languages = {}
registered_users = {}
user_wallets = {}

def listener(message):
    for m in message:
        if m.content_type == 'text':
            print(f"{m.chat.first_name} [{m.chat.id}] {m.text}")
            logging.info(f"{m.chat.first_name} [{m.chat.id}] {m.text}")
        else:
            print(f"other message type: {m.content_type}\n")

bot.set_update_listener(listener)

def get_all_crypto_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_translation(key, user_id):
    language = user_languages.get(user_id, 'en')
    return translations[language].get(key, key)

def save_user(telegram_id):
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='register')
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO user (telegram_id, usd_balance, btc_balance, eth_balance, usdt_balance)
        VALUES (%s, %s, %s, %s, %s)
        """, (telegram_id, 0.00, 0.00, 0.00, 0.00))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def create_wallet_for_user(telegram_id):
    wallet_address = f"Hero_{telegram_id}_Exchange"
    query = "INSERT INTO wallet (telegram_id, wallet_address) VALUES (%s, %s)"
    cursor.execute(query, (telegram_id, wallet_address))
    db.commit()
    user_wallets[telegram_id] = wallet_address
    return wallet_address

def is_registered(telegram_id):
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='register')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE telegram_id = %s", (telegram_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


def is_user_wallet_exists(telegram_id):
    return user_wallets.get(telegram_id) is not None


def get_user_wallet_balance(telegram_id, currency):
    if currency == 'usd':
        cursor.execute("SELECT usd_balance FROM user WHERE telegram_id = %s", (telegram_id,))
    elif currency == 'btc':
        cursor.execute("SELECT btc_balance FROM user WHERE telegram_id = %s", (telegram_id,))
    elif currency == 'eth':
        cursor.execute("SELECT eth_balance FROM user WHERE telegram_id = %s", (telegram_id,))
    elif currency == 'usdt':
        cursor.execute("SELECT usdt_balance FROM user WHERE telegram_id = %s", (telegram_id,))

    result = cursor.fetchone()
    return result[0] if result else None


def buy_crypto(telegram_id, amount, currency, current_price):
    wallet_balance = get_user_wallet_balance(telegram_id, currency='usd')
    if wallet_balance is not None and wallet_balance >= amount:
        crypto_amount = amount / current_price

        if currency == 'BTC':
            cursor.execute("UPDATE user SET usd_balance = usd_balance - %s, btc_balance = btc_balance + %s WHERE telegram_id = %s",
                           (amount, crypto_amount, telegram_id))
        elif currency == 'ETH':
            cursor.execute("UPDATE user SET usd_balance = usd_balance - %s, eth_balance = eth_balance + %s WHERE telegram_id = %s",
                           (amount, crypto_amount, telegram_id))
        elif currency == 'USDT':
            cursor.execute("UPDATE user SET usd_balance = usd_balance - %s, usdt_balance = usdt_balance + %s WHERE telegram_id = %s",
                           (amount, crypto_amount, telegram_id))

        db.commit()
        return crypto_amount
    return None


def sell_crypto(telegram_id, amount, currency, current_price):
    if currency == 'BTC':
        wallet_balance = get_user_wallet_balance(telegram_id, currency='btc')
    elif currency == 'ETH':
        wallet_balance = get_user_wallet_balance(telegram_id, currency='eth')
    elif currency == 'USDT':
        wallet_balance = get_user_wallet_balance(telegram_id, currency='usdt')

    if wallet_balance is not None and wallet_balance >= amount:
        usd_received = amount * current_price

        if currency == 'BTC':
            cursor.execute("UPDATE user SET usd_balance = usd_balance + %s, btc_balance = btc_balance - %s WHERE telegram_id = %s",
                           (usd_received, amount, telegram_id))
        elif currency == 'ETH':
            cursor.execute("UPDATE user SET usd_balance = usd_balance + %s, eth_balance = eth_balance - %s WHERE telegram_id = %s",
                           (usd_received, amount, telegram_id))
        elif currency == 'USDT':
            cursor.execute("UPDATE user SET usd_balance = usd_balance + %s, usdt_balance = usdt_balance - %s WHERE telegram_id = %s",
                           (usd_received, amount, telegram_id))

        db.commit()
        return True
    return False


def transfer_crypto(telegram_id, wallet_address, amount, currency):
    if currency == 'BTC':
        wallet_balance = get_user_wallet_balance(telegram_id, currency='btc')
    elif currency == 'ETH':
        wallet_balance = get_user_wallet_balance(telegram_id, currency='eth')
    elif currency == 'USDT':
        wallet_balance = get_user_wallet_balance(telegram_id, currency='usdt')

    if wallet_balance is not None and wallet_balance >= amount:
        if currency == 'BTC':
            cursor.execute("UPDATE user SET btc_balance = btc_balance - %s WHERE telegram_id = %s",
                           (amount, telegram_id))
        elif currency == 'ETH':
            cursor.execute("UPDATE user SET eth_balance = eth_balance - %s WHERE telegram_id = %s",
                           (amount, telegram_id))
        elif currency == 'USDT':
            cursor.execute("UPDATE user SET usdt_balance = usdt_balance - %s WHERE telegram_id = %s",
                           (amount, telegram_id))

        cursor.execute("""
        INSERT INTO transactions (telegram_id, currency, amount, transaction_type, new_balance, to_wallet_address) 
        VALUES (%s, %s, %s, 'transfer', 
        (SELECT CASE 
            WHEN %s = 'BTC' THEN btc_balance
            WHEN %s = 'ETH' THEN eth_balance
            WHEN %s = 'USDT' THEN usdt_balance
            END FROM user WHERE telegram_id = %s), %s)
        """, (telegram_id, currency, amount, currency, currency, currency, telegram_id, wallet_address))

        db.commit()
        return True
    return False

def is_valid_wallet_address(wallet_address, user_id):
    pattern = f"^Hero_{user_id}_Exchange$"
    return re.match(pattern, wallet_address) is not None


@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    user_languages[cid] = 'en'
    bot.copy_message(cid, channel_id, "2")
    time.sleep(1)
    sample = InlineKeyboardMarkup()
    sample.add(InlineKeyboardButton('EN', callback_data='en'))
    sample.add(InlineKeyboardButton('FA', callback_data='fa'))
    bot.send_message(cid, get_translation("choose_language", cid), reply_markup=sample)

@bot.message_handler(commands=['help'])
def help_command(message):
    cid = message.chat.id
    text = get_translation("help", cid)
    for key, value in commands.items():
        text += f"/{key} : {get_translation(key, cid)}\n"
    antiflood(bot.send_message, cid, text)

@bot.message_handler(commands=['get_price_cryptos'])
def get_price_crypto(message):
    cid = message.chat.id
    if not is_registered(cid):
        bot.send_message(cid, get_translation("need_registration", cid))
        return
    crypto_prices = get_all_crypto_prices()
    market = get_translation("get_price_cryptos", cid)
    number = 0
    for crypto in crypto_prices:
        number += 1
        market += f"{number}. {crypto['name']} ({crypto['symbol'].upper()}): ${crypto['current_price']}\n"
    antiflood(bot.send_message, cid, market)

@bot.message_handler(commands=['register'])
def register(message):
    cid = message.chat.id
    if is_registered(cid):
        bot.send_message(cid, get_translation("already_registered", cid))
    else:
        save_user(cid)
        bot.send_message(cid, get_translation("registration_success", cid))

@bot.message_handler(commands=['create_wallet'])
def create_wallet(message):
    cid = message.chat.id
    if is_registered(cid):
        if not is_user_wallet_exists(cid):
            wallet_address = create_wallet_for_user(cid)
            bot.send_message(cid, get_translation("wallet_created", cid).format(wallet_address))
        else:
            bot.send_message(cid, "You already have a wallet.\n ولت شما ساخته شده است.")
    else:
        bot.send_message(cid, get_translation("need_registration", cid))

@bot.message_handler(commands=['check_balance'])
def check_balance(message):
    cid = message.chat.id
    if is_registered(cid):
        usd_balance = get_user_wallet_balance(cid, 'usd')
        btc_balance = get_user_wallet_balance(cid, 'btc')
        eth_balance = get_user_wallet_balance(cid, 'eth')
        usdt_balance = get_user_wallet_balance(cid, 'usdt')

        bot.send_message(cid, get_translation("usd_balance", cid).format(usd_balance))
        bot.send_message(cid, f"BTC Balance: {btc_balance}, ETH Balance: {eth_balance}, USDT Balance: {usdt_balance}")
    else:
        bot.send_message(cid, get_translation("need_registration", cid))

@bot.message_handler(commands=['buy_crypto'])
def buy_crypto_command(message):
    cid = message.chat.id
    if not is_registered(cid):
        bot.send_message(cid, get_translation("need_registration", cid))
        return

    crypto_prices = get_all_crypto_prices()
    if not crypto_prices:
        bot.send_message(cid, "Failed to retrieve crypto prices. Please try again.")
        return

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('BTC', 'ETH', 'USDT')

    bot.send_message(cid, "Please choose the cryptocurrency you want to buy:", reply_markup=markup,)
    bot.register_next_step_handler(message, process_buy_crypto_step, crypto_prices)

def process_buy_crypto_step(message, crypto_prices):
    cid = message.chat.id
    crypto = message.text.upper()
    valid_cryptos = ["BTC", "ETH", "USDT"]
    if crypto not in valid_cryptos:
        bot.send_message(cid, "Invalid cryptocurrency selection. Please choose BTC, ETH, or USDT.")
        return

    bot.send_message(cid, "How much would you like to spend in USD?", reply_markup=hideboard)
    bot.register_next_step_handler(message, process_buy_amount_step, crypto, crypto_prices)

def process_buy_amount_step(message, crypto, crypto_prices):
    cid = message.chat.id
    try:
        amount = float(message.text)
    except ValueError:
        bot.send_message(cid, "Invalid amount. Please enter a valid number.")
        return

    crypto_price = next((c["current_price"] for c in crypto_prices if c["symbol"].upper() == crypto), None)
    if crypto_price is None:
        bot.send_message(cid, "Failed to retrieve the price of the selected cryptocurrency. Please try again.")
        return

    crypto_amount = buy_crypto(cid, amount, crypto, crypto_price)
    if crypto_amount is not None:
        bot.send_message(cid, get_translation("buy_success", cid).format(crypto_amount, crypto))
    else:
        bot.send_message(cid, get_translation("not_enough_balance", cid))

@bot.message_handler(commands=['sell_crypto'])
def sell_crypto_command(message):
    cid = message.chat.id
    if not is_registered(cid):
        bot.send_message(cid, get_translation("need_registration", cid))
        return

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('BTC', 'ETH', 'USDT')

    bot.send_message(cid, "Please choose the cryptocurrency you want to sell:", reply_markup=markup)
    bot.register_next_step_handler(message, process_sell_crypto_step)

def process_sell_crypto_step(message):
    cid = message.chat.id
    crypto = message.text.upper()
    valid_cryptos = ["BTC", "ETH", "USDT"]
    if crypto not in valid_cryptos:
        bot.send_message(cid, "Invalid cryptocurrency selection. Please choose BTC, ETH, or USDT.")
        return

    bot.send_message(cid, "How much would you like to sell?", reply_markup=hideboard)
    bot.register_next_step_handler(message, process_sell_amount_step, crypto)

def process_sell_amount_step(message, crypto):
    cid = message.chat.id
    try:
        amount = float(message.text)
    except ValueError:
        bot.send_message(cid, "Invalid amount. Please enter a valid number.")
        return

    crypto_prices = get_all_crypto_prices()
    crypto_price = next((c["current_price"] for c in crypto_prices if c["symbol"].upper() == crypto), None)
    if crypto_price is None:
        bot.send_message(cid, "Failed to retrieve the price of the selected cryptocurrency. Please try again.")
        return

    success = sell_crypto(cid, amount, crypto, crypto_price)
    if success:
        bot.send_message(cid, get_translation("sell_success", cid).format(amount, crypto))
    else:
        bot.send_message(cid, get_translation("not_enough_balance", cid))

@bot.message_handler(commands=['transfer_crypto'])
def transfer_crypto_command(message):
    cid = message.chat.id
    if not is_registered(cid):
        bot.send_message(cid, get_translation("need_registration", cid))
        return

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('BTC', 'ETH', 'USDT')

    bot.send_message(cid, "Please choose the cryptocurrency you want to transfer:\nلطفا ارز دیجیتالی که میخواهید انتقال دهید را انتخاب کنید:", reply_markup=markup)
    bot.register_next_step_handler(message, process_transfer_crypto_step)

def process_transfer_crypto_step(message):
    cid = message.chat.id
    crypto = message.text.upper()
    valid_cryptos = ["BTC", "ETH", "USDT"]
    if crypto not in valid_cryptos:
        bot.send_message(cid, "Invalid cryptocurrency selection. Please choose BTC, ETH, or USDT.\nانتخاب شما نادرست استو لطفا BTC, ETH, USDT را انتخاب کنید.")
        return

    bot.send_message(cid, "How much would you like to transfer?\nچه مقدار میخواهید انتقال دهید؟", reply_markup=hideboard)
    bot.register_next_step_handler(message, process_transfer_amount_step, crypto)

def process_transfer_amount_step(message, crypto):
    cid = message.chat.id
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        bot.send_message(cid, "Invalid amount. Please enter a valid number.\nمقدار ارز نامعتبر است. لطفا یک مقدار معتبر وارد کنید.")
        return

    bot.send_message(cid, "Please provide the recipient's wallet address in the format: Hero_{your_cid}_Exchange\nلطفا یک آدرس ولت با این فرمت ارسال کنید: Hero_{your_cid}_Exchange", reply_markup=hideboard)
    bot.register_next_step_handler(message, process_transfer_wallet_step, crypto, amount)

def process_transfer_wallet_step(message, crypto, amount):
    cid = message.chat.id
    to_wallet = message.text.strip()


    if not is_valid_wallet_address(to_wallet, cid):
        bot.send_message(cid, "Invalid wallet address format. Please provide a valid wallet address in the format: Hero_{your_cid}_Exchange.\nفرمت آدرس ولت وارد شده نامعتبر است. لطفا یک آدرس ولت با این فرمت ارسال کنید: Hero_{your_cid}_Exchange")
        return

    success = transfer_crypto(cid, to_wallet, amount, crypto)

    if success:
        bot.send_message(cid, "✅ Transfer successful! The transaction has been completed.\n✅انتقال با موفقیت انجام شد. ")
    else:
        bot.send_message(cid, "❌ Transfer failed due to insufficient balance or other issue.\n❌ به دلیل موجودی ناکافی یا مشکل دیگر، انتقال انجام نشد.")


@bot.message_handler(commands=['increase_balance'])
def increase_balance_command(message):
    cid = message.chat.id
    if not is_registered(cid):
        bot.send_message(cid, get_translation("need_registration", cid))
        return

    bot.send_message(cid, "How much would you like to add to your wallet balance in USD?\nچقدر می خواهید به موجودی کیف پول خود به دلار اضافه کنید؟")
    bot.register_next_step_handler(message, process_increase_balance_step)

def process_increase_balance_step(message):
    cid = message.chat.id
    try:
        amount = float(message.text)
    except ValueError:
        bot.send_message(cid, "Invalid amount. Please enter a valid number.")
        return

    cursor.execute("UPDATE user SET usd_balance = usd_balance + %s WHERE telegram_id = %s", (amount, cid))
    db.commit()
    bot.send_message(cid, f"Your wallet balance has been increased by ${amount}.\nموجودی کیف پول شما به مبلغ {amount}$ افزایش یافت.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cid = call.message.chat.id
    if call.data == 'en':
        user_languages[cid] = 'en'
        bot.send_message(cid, get_translation("en_selected", cid))
    elif call.data == 'fa':
        user_languages[cid] = 'fa'
        bot.send_message(cid, get_translation("fa_selected", cid))

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

while True:
    try:
        bot.polling(none_stop=True, skip_pending=True)
    except Exception as e:
        logging.error(f"Error in polling: {e}")
        time.sleep(15)
