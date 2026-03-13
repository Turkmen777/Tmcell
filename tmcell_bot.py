import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import time
import os
import re

# ===== ВАШИ ДАННЫЕ ДЛЯ 3 НОМЕРОВ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', "7635918525:AAFp6g0sna1Mq59NiaWVk_tdHq8O5P9_3HY")

# Номер 1 (ваш основной)
LOGIN1 = "62489636"
PASSWORD1 = "5873W295"

# Номер 2
LOGIN2 = "61416500"
PASSWORD2 = "W16G8SL1"

# Номер 3
LOGIN3 = "65136133"
PASSWORD3 = "L6GL4279"
# ======================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_tmcell_balance(login, password):
    """
    Функция для получения баланса для конкретного номера
    """
    session = requests.Session()
    
    try:
        login_url = "https://hyzmat.tmcell.tm/"
        auth_url = "https://hyzmat.tmcell.tm/User"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://hyzmat.tmcell.tm',
            'Referer': 'https://hyzmat.tmcell.tm/',
        }
        
        # Получаем токен
        main_page = session.get(login_url, headers=headers)
        time.sleep(1)
        
        soup = BeautifulSoup(main_page.text, 'html.parser')
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        verification_token = token_input.get('value', '') if token_input else ""
        
        # Вход с конкретным логином/паролем
        login_data = {
            '__RequestVerificationToken': verification_token,
            'login': login,  # Используем переданный логин
            'password': password,  # Используем переданный пароль
        }
        
        login_response = session.post(auth_url, data=login_data, headers=headers, allow_redirects=True)
        
        if login_response.status_code != 200:
            return None, f"Ошибка входа: код {login_response.status_code}"
        
        # Ищем баланс
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        for element in soup.find_all(['div', 'span', 'td', 'p', 'h3', 'label', 'strong']):
            if element.text and ('Баланс контракта' in element.text):
                return element.text.strip(), None
        
        return None, "Не удалось найти баланс"
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return None, f"Ошибка: {str(e)}"

async def balance1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Баланс для номера 1 (62489636)"""
    await update.message.reply_text("🔍 Проверяю баланс для номера 1...")
    
    balance, error = get_tmcell_balance(LOGIN1, PASSWORD1)
    
    if error:
        await update.message.reply_text(f"❌ Номер 1: {error}")
    else:
        try:
            amount_match = re.search(r'([\d]+,[\d]+)', balance)
            amount = amount_match.group(1) if amount_match else "?"
            date_match = re.search(r'на ([\d\.]+ [\d:]+)', balance)
            date_time = date_match.group(1) if date_match else "?"
            
            await update.message.reply_text(
                f"📱 <b>Номер 1: 993{LOGIN1}</b>\n"
                f"💰 {amount} manat\n"
                f"📅 {date_time}",
                parse_mode="HTML"
            )
        except:
            clean_balance = balance.replace("Баланс контракта:", "").strip()
            await update.message.reply_text(f"📱 Номер 1: 993{LOGIN1}\n💰 {clean_balance}")

async def balance2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Баланс для номера 2 (61416500)"""
    await update.message.reply_text("🔍 Проверяю баланс для номера 2...")
    
    balance, error = get_tmcell_balance(LOGIN2, PASSWORD2)
    
    if error:
        await update.message.reply_text(f"❌ Номер 2: {error}")
    else:
        try:
            amount_match = re.search(r'([\d]+,[\d]+)', balance)
            amount = amount_match.group(1) if amount_match else "?"
            date_match = re.search(r'на ([\d\.]+ [\d:]+)', balance)
            date_time = date_match.group(1) if date_match else "?"
            
            await update.message.reply_text(
                f"📱 <b>Номер 2: 993{LOGIN2}</b>\n"
                f"💰 {amount} manat\n"
                f"📅 {date_time}",
                parse_mode="HTML"
            )
        except:
            clean_balance = balance.replace("Баланс контракта:", "").strip()
            await update.message.reply_text(f"📱 Номер 2: 993{LOGIN2}\n💰 {clean_balance}")

async def balance3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Баланс для номера 3 (65136133)"""
    await update.message.reply_text("🔍 Проверяю баланс для номера 3...")
    
    balance, error = get_tmcell_balance(LOGIN3, PASSWORD3)
    
    if error:
        await update.message.reply_text(f"❌ Номер 3: {error}")
    else:
        try:
            amount_match = re.search(r'([\d]+,[\d]+)', balance)
            amount = amount_match.group(1) if amount_match else "?"
            date_match = re.search(r'на ([\d\.]+ [\d:]+)', balance)
            date_time = date_match.group(1) if date_match else "?"
            
            await update.message.reply_text(
                f"📱 <b>Номер 3: 993{LOGIN3}</b>\n"
                f"💰 {amount} manat\n"
                f"📅 {date_time}",
                parse_mode="HTML"
            )
        except:
            clean_balance = balance.replace("Баланс контракта:", "").strip()
            await update.message.reply_text(f"📱 Номер 3: 993{LOGIN3}\n💰 {clean_balance}")

async def balance_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверить баланс всех трёх номеров"""
    msg = await update.message.reply_text("🔄 Проверяю все номера...")
    
    results = []
    
    # Номер 1
    balance1, error1 = get_tmcell_balance(LOGIN1, PASSWORD1)
    if error1:
        results.append(f"❌ Номер 1: {error1}")
    else:
        amount1 = re.search(r'([\d]+,[\d]+)', balance1)
        results.append(f"✅ Номер 1: {amount1.group(1) if amount1 else '?'} manat")
    
    # Номер 2
    balance2, error2 = get_tmcell_balance(LOGIN2, PASSWORD2)
    if error2:
        results.append(f"❌ Номер 2: {error2}")
    else:
        amount2 = re.search(r'([\d]+,[\d]+)', balance2)
        results.append(f"✅ Номер 2: {amount2.group(1) if amount2 else '?'} manat")
    
    # Номер 3
    balance3, error3 = get_tmcell_balance(LOGIN3, PASSWORD3)
    if error3:
        results.append(f"❌ Номер 3: {error3}")
    else:
        amount3 = re.search(r'([\d]+,[\d]+)', balance3)
        results.append(f"✅ Номер 3: {amount3.group(1) if amount3 else '?'} manat")
    
    # Отправляем общий результат
    final_message = "📊 <b>Балансы всех номеров</b>\n\n" + "\n".join(results)
    await msg.edit_text(final_message, parse_mode="HTML")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда старт с описанием"""
    await update.message.reply_text(
        "👋 <b>Бот баланса TMCell для 3 номеров</b>\n\n"
        "Команды:\n"
        "/balance1 - баланс номера 99362489636\n"
        "/balance2 - баланс номера 99361416500\n"
        "/balance3 - баланс номера 99365136133\n"
        "/all - баланс всех номеров сразу\n"
        "/start - показать это сообщение",
        parse_mode="HTML"
    )

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        print("❌ Ошибка: не указан токен бота!")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balance1", balance1_command))
    app.add_handler(CommandHandler("balance2", balance2_command))
    app.add_handler(CommandHandler("balance3", balance3_command))
    app.add_handler(CommandHandler("all", balance_all_command))
    
    print("✅ Бот для 3 номеров запущен!")
    print("Команды: /balance1, /balance2, /balance3, /all")
    
    app.run_polling()

if __name__ == "__main__":
    main()
