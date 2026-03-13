import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import time

# ===== ВАШИ ДАННЫЕ (ЗАПОЛНИТЕ) =====
BOT_TOKEN = "8291780121:AAEF-b3stiBvPs2VjVHnaApV1VIpA_y5--0"  # Вставьте токен от @BotFather
TICELL_LOGIN = "99362489636"     # Ваш номер (как на скриншоте)
TICELL_PASSWORD = "5873W295"   # Ваш пароль от кабинета
# ====================================

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def get_tmcell_balance():
    """
    Функция для получения баланса с сайта hyzmat.tmcell.tm
    """
    session = requests.Session()
    
    try:
        # Точные адреса с официального сайта
        login_url = "https://hyzmat.tmcell.tm/"  # Страница входа
        auth_url = "https://hyzmat.tmcell.tm/index.php"  # Куда отправляется форма
        
        # Заголовки как у настоящего браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://hyzmat.tmcell.tm',
            'Referer': 'https://hyzmat.tmcell.tm/',
        }
        
        # Сначала заходим на страницу, получаем куки
        session.get(login_url, headers=headers)
        time.sleep(1)
        
        # Данные для входа (согласно официальной документации)
        # На сайте написано: вводите последние 8 цифр номера [citation:1]
        login_digits = TICELL_LOGIN[-8:]  # Берем последние 8 цифр (62489636)
        
        login_data = {
            'login': login_digits,        # Только последние 8 цифр!
            'password': TICELL_PASSWORD,
            'enter': 'Вход'               # Кнопка отправки
        }
        
        # Отправляем POST запрос на вход
        login_response = session.post(auth_url, data=login_data, headers=headers, allow_redirects=True)
        
        if login_response.status_code != 200:
            return None, f"Ошибка входа: код {login_response.status_code}"
        
        # После успешного входа мы на странице профиля
        # Ищем баланс
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # На скриншоте баланс в формате "Баланс контракта: 564,78 manat"
        balance_text = None
        
        # Ищем везде, где есть текст "Баланс контракта"
        for element in soup.find_all(['div', 'span', 'td', 'p', 'h3']):
            if element.text and ('Баланс контракта' in element.text or 'баланс' in element.text.lower()):
                balance_text = element.text.strip()
                break
        
        if balance_text:
            # Очищаем от лишнего и возвращаем
            return balance_text, None
        else:
            # Если не нашли, покажем весь текст страницы для отладки
            return None, "Не удалось найти баланс. Проверьте логин/пароль."
            
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /balance"""
    await update.message.reply_text("🔍 Проверяю баланс TMCell...")
    
    balance, error = get_tmcell_balance()
    
    if error:
        await update.message.reply_text(f"❌ {error}")
    else:
        await update.message.reply_text(f"💰 {balance}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "👋 Привет! Я бот для проверки баланса TMCell.\n"
        "Просто отправь команду /balance и я покажу текущий баланс."
    )

def main():
    """Запуск бота"""
    # Проверяем, что токен введен
    if BOT_TOKEN == "ТОКЕН_ВАШЕГО_БОТА":
        print("❌ ОШИБКА: Вставьте свой токен бота в переменную BOT_TOKEN!")
        return
    
    # Создаем бота
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balance", balance_command))
    
    print("✅ Бот запущен! Напиши своему боту: /balance")
    app.run_polling()

if __name__ == "__main__":
    main()
