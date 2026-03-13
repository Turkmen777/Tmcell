import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import time
import os
import re

# ===== ВАШИ ДАННЫЕ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8291780121:AAEF-b3stiBvPs2VjVHnaApV1VIpA_y5--0")
TICELL_LOGIN = os.environ.get('TICELL_LOGIN', "62489636")
TICELL_PASSWORD = os.environ.get('TICELL_PASSWORD', "5873W295")
# =======================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_tmcell_balance():
    """Функция для получения баланса с сайта"""
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
        
        # Вход
        login_digits = TICELL_LOGIN[-8:]
        login_data = {
            '__RequestVerificationToken': verification_token,
            'login': login_digits,
            'password': TICELL_PASSWORD,
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

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет красиво отформатированный баланс"""
    await update.message.reply_text("🔍 Проверяю баланс TMCell...")
    
    balance, error = get_tmcell_balance()
    
    if error:
        await update.message.reply_text(f"❌ {error}")
    else:
        try:
            # Пример: "Баланс контракта: 614,78 manat на 13.03.2026 12:05:31"
            
            # Ищем сумму (цифры с запятой)
            amount_match = re.search(r'([\d]+,[\d]+)', balance)
            amount = amount_match.group(1) if amount_match else "?"
            
            # Ищем дату и время
            date_match = re.search(r'на ([\d\.]+ [\d:]+)', balance)
            date_time = date_match.group(1) if date_match else "?"
            
            # Отправляем красиво
            await update.message.reply_text(
                f"💰 <b>Баланс контракта</b>\n"
                f"{amount} manat\n\n"
                f"📅 {date_time}",
                parse_mode="HTML"
            )
        except:
            # Если не получилось разобрать, отправляем как есть
            clean_balance = balance.replace("Баланс контракта:", "").strip()
            await update.message.reply_text(f"💰 {clean_balance}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда старт"""
    await update.message.reply_text(
        "👋 <b>Бот баланса TMCell</b>\n\n"
        "Команды:\n"
        "/balance - показать текущий баланс",
        parse_mode="HTML"
    )

def main():
    """Запуск бота"""
    if not BOT_TOKEN or BOT_TOKEN == "ваш_токен_здесь":
        print("❌ Ошибка: не указан токен бота!")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balance", balance_command))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
