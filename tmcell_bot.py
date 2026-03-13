import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import time
import os

# ===== ВАШИ ДАННЫЕ =====
# Токен лучше брать из переменных окружения Bothost
BOT_TOKEN = os.environ.get('BOT_TOKEN', "ВАШ_ТОКЕН_БОТА_ОТ_BOTFATHER")
TICELL_LOGIN = os.environ.get('TICELL_LOGIN', "99362489636")  # Ваш номер
TICELL_PASSWORD = os.environ.get('TICELL_PASSWORD', "ВАШ_ПАРОЛЬ_ОТ_TMCELL")
# =======================

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_tmcell_balance():
    """
    Функция для получения баланса с сайта hyzmat.tmcell.tm
    """
    session = requests.Session()
    
    try:
        # Точные адреса с сайта
        login_url = "https://hyzmat.tmcell.tm/"
        auth_url = "https://hyzmat.tmcell.tm/User"
        
        # Заголовки как у браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://hyzmat.tmcell.tm',
            'Referer': 'https://hyzmat.tmcell.tm/',
        }
        
        # ШАГ 1: Заходим на главную страницу, чтобы получить токен
        logger.info("Заходим на главную страницу...")
        main_page = session.get(login_url, headers=headers)
        time.sleep(1)
        
        # Ищем токен в HTML
        soup = BeautifulSoup(main_page.text, 'html.parser')
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        
        if token_input:
            verification_token = token_input.get('value', '')
            logger.info(f"Токен получен: {verification_token[:20]}...")
        else:
            verification_token = ""
            logger.warning("Токен не найден, пробуем без токена")
        
        # ШАГ 2: Подготавливаем данные для входа
        # Берем последние 8 цифр номера (как требует сайт)
        login_digits = TICELL_LOGIN[-8:]
        logger.info(f"Логин для входа (последние 8 цифр): {login_digits}")
        
        # Данные для входа (точно как в форме)
        login_data = {
            '__RequestVerificationToken': verification_token,
            'login': login_digits,
            'password': TICELL_PASSWORD,
        }
        
        # ШАГ 3: Отправляем POST запрос на вход
        logger.info("Отправляем POST запрос на /User...")
        login_response = session.post(auth_url, data=login_data, headers=headers, allow_redirects=True)
        
        logger.info(f"Статус ответа: {login_response.status_code}")
        
        if login_response.status_code != 200:
            return None, f"Ошибка входа: код {login_response.status_code}"
        
        # ШАГ 4: Ищем баланс на странице
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Ищем элемент с балансом (по тексту "Баланс контракта")
        balance_text = None
        for element in soup.find_all(['div', 'span', 'td', 'p', 'h3', 'label', 'strong']):
            if element.text and ('Баланс контракта' in element.text):
                balance_text = element.text.strip()
                logger.info(f"Найден баланс: {balance_text}")
                break
        
        # Если не нашли по первому способу, ищем просто слово "баланс"
        if not balance_text:
            for element in soup.find_all(['div', 'span', 'td', 'p']):
                if element.text and 'баланс' in element.text.lower():
                    balance_text = element.text.strip()
                    logger.info(f"Найден баланс (по слову баланс): {balance_text}")
                    break
        
        if balance_text:
            return balance_text, None
        else:
            # Если совсем не нашли, сохраняем страницу для отладки
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(login_response.text)
            logger.info("Страница сохранена в debug_page.html")
            
            return None, "Не удалось найти баланс на странице. Проверьте логин/пароль."
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return None, f"Ошибка при проверке: {str(e)}"

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /balance"""
    await update.message.reply_text("🔍 Проверяю баланс TMCell, подождите...")
    
    balance, error = get_tmcell_balance()
    
    if error:
        await update.message.reply_text(f"❌ {error}")
    else:
        await update.message.reply_text(f"💰 {balance}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "👋 Привет! Я бот для проверки баланса TMCell.\n\n"
        "Команды:\n"
        "/balance - проверить текущий баланс\n"
        "/start - показать это сообщение"
    )

def main():
    """Запуск бота"""
    # Проверяем, что токен введен
    if BOT_TOKEN == "ВАШ_ТОКЕН_БОТА_ОТ_BOTFATHER":
        logger.error("ОШИБКА: Вставьте свой токен бота в переменную BOT_TOKEN!")
        print("❌ ОШИБКА: Вставьте свой токен бота в переменную BOT_TOKEN!")
        return
    
    # Проверяем пароль
    if TICELL_PASSWORD == "ВАШ_ПАРОЛЬ_ОТ_TMCELL":
        logger.error("ОШИБКА: Вставьте свой пароль от TMcell!")
        print("❌ ОШИБКА: Вставьте свой пароль от TMcell!")
        return
    
    # Создаем бота
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balance", balance_command))
    
    logger.info("✅ Бот запущен!")
    print("✅ Бот запущен! Нажми Ctrl+C для остановки")
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
