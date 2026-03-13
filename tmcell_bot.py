import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import time
import os
import re
import json
import asyncio
from datetime import datetime

# ===== ВАШИ ДАННЫЕ ДЛЯ 3 НОМЕРОВ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', "7635918525:AAFp6g0sna1Mq59NiaWVk_tdHq8O5P9_3HY")

# Номер 1
LOGIN1 = "62489636"
PASSWORD1 = "5873W295"

# Номер 2
LOGIN2 = "61416500"
PASSWORD2 = "W16G8SL1"

# Номер 3
LOGIN3 = "65136133"
PASSWORD3 = "L6GL4279"
# ======================================

# Файл для хранения предыдущих балансов
BALANCE_FILE = "balances.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_balances():
    """Загружает сохраненные балансы из файла"""
    try:
        if os.path.exists(BALANCE_FILE):
            with open(BALANCE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки балансов: {e}")
    return {}

def save_balances(balances):
    """Сохраняет балансы в файл"""
    try:
        with open(BALANCE_FILE, 'w', encoding='utf-8') as f:
            json.dump(balances, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения балансов: {e}")

def get_tmcell_balance(login, password):
    """Функция для получения баланса для конкретного номера"""
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
            'login': login,
            'password': password,
        }
        
        login_response = session.post(auth_url, data=login_data, headers=headers, allow_redirects=True)
        
        if login_response.status_code != 200:
            return None, None, f"Ошибка входа: код {login_response.status_code}"
        
        # Ищем баланс
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        for element in soup.find_all(['div', 'span', 'td', 'p', 'h3', 'label', 'strong']):
            if element.text and ('Баланс контракта' in element.text):
                balance_text = element.text.strip()
                
                # Извлекаем сумму
                amount_match = re.search(r'([\d]+,[\d]+)', balance_text)
                if amount_match:
                    amount_str = amount_match.group(1).replace(',', '.')
                    amount = float(amount_str)
                    return amount, balance_text, None
                return None, balance_text, None
        
        return None, None, "Не удалось найти баланс"
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return None, None, f"Ошибка: {str(e)}"

async def check_balances(context: ContextTypes.DEFAULT_TYPE):
    """Проверяет балансы всех номеров и отправляет уведомления о пополнениях"""
    chat_id = context.job.chat_id
    saved_balances = load_balances()
    
    numbers = [
        {"name": "Номер 1", "login": LOGIN1, "password": PASSWORD1, "full": f"993{LOGIN1}"},
        {"name": "Номер 2", "login": LOGIN2, "password": PASSWORD2, "full": f"993{LOGIN2}"},
        {"name": "Номер 3", "login": LOGIN3, "password": PASSWORD3, "full": f"993{LOGIN3}"},
    ]
    
    notifications = []
    
    for number in numbers:
        try:
            amount, full_text, error = get_tmcell_balance(number["login"], number["password"])
            
            if error or amount is None:
                logger.error(f"Ошибка для {number['name']}: {error}")
                continue
            
            # Получаем предыдущий баланс
            prev_amount = saved_balances.get(number["login"])
            
            # Сохраняем новый баланс
            saved_balances[number["login"]] = amount
            
            # Если есть предыдущий баланс и новый больше
            if prev_amount is not None:
                difference = amount - prev_amount
                
                # Если баланс увеличился на 20 или более манат
                if difference >= 20.0:
                    time_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                    notifications.append(
                        f"📈 <b>{number['name']} ({number['full']})</b>\n"
                        f"Пополнение: +{difference:.2f} manat\n"
                        f"Текущий баланс: {amount:.2f} manat\n"
                        f"🕐 {time_str}"
                    )
            
        except Exception as e:
            logger.error(f"Ошибка проверки {number['name']}: {e}")
    
    # Сохраняем обновленные балансы
    save_balances(saved_balances)
    
    # Отправляем уведомления, если есть
    if notifications:
        message = "🔔 <b>Обнаружены пополнения баланса!</b>\n\n" + "\n\n".join(notifications)
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

async def balance1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Баланс для номера 1"""
    await update.message.reply_text("🔍 Проверяю баланс для номера 1...")
    
    amount, full_text, error = get_tmcell_balance(LOGIN1, PASSWORD1)
    
    if error:
        await update.message.reply_text(f"❌ Номер 1: {error}")
    else:
        if amount:
            await update.message.reply_text(
                f"📱 <b>Номер 1: 993{LOGIN1}</b>\n"
                f"💰 {amount:.2f} manat",
                parse_mode="HTML"
            )
        else:
            clean_balance = full_text.replace("Баланс контракта:", "").strip()
            await update.message.reply_text(f"📱 Номер 1: 993{LOGIN1}\n💰 {clean_balance}")

async def balance2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Баланс для номера 2"""
    await update.message.reply_text("🔍 Проверяю баланс для номера 2...")
    
    amount, full_text, error = get_tmcell_balance(LOGIN2, PASSWORD2)
    
    if error:
        await update.message.reply_text(f"❌ Номер 2: {error}")
    else:
        if amount:
            await update.message.reply_text(
                f"📱 <b>Номер 2: 993{LOGIN2}</b>\n"
                f"💰 {amount:.2f} manat",
                parse_mode="HTML"
            )
        else:
            clean_balance = full_text.replace("Баланс контракта:", "").strip()
            await update.message.reply_text(f"📱 Номер 2: 993{LOGIN2}\n💰 {clean_balance}")

async def balance3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Баланс для номера 3"""
    await update.message.reply_text("🔍 Проверяю баланс для номера 3...")
    
    amount, full_text, error = get_tmcell_balance(LOGIN3, PASSWORD3)
    
    if error:
        await update.message.reply_text(f"❌ Номер 3: {error}")
    else:
        if amount:
            await update.message.reply_text(
                f"📱 <b>Номер 3: 993{LOGIN3}</b>\n"
                f"💰 {amount:.2f} manat",
                parse_mode="HTML"
            )
        else:
            clean_balance = full_text.replace("Баланс контракта:", "").strip()
            await update.message.reply_text(f"📱 Номер 3: 993{LOGIN3}\n💰 {clean_balance}")

async def balance_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверить баланс всех трёх номеров"""
    msg = await update.message.reply_text("🔄 Проверяю все номера...")
    
    results = []
    saved_balances = load_balances()
    
    # Номер 1
    amount1, _, error1 = get_tmcell_balance(LOGIN1, PASSWORD1)
    if error1:
        results.append(f"❌ Номер 1: {error1}")
    else:
        results.append(f"✅ Номер 1: {amount1:.2f} manat")
        saved_balances[LOGIN1] = amount1
    
    # Номер 2
    amount2, _, error2 = get_tmcell_balance(LOGIN2, PASSWORD2)
    if error2:
        results.append(f"❌ Номер 2: {error2}")
    else:
        results.append(f"✅ Номер 2: {amount2:.2f} manat")
        saved_balances[LOGIN2] = amount2
    
    # Номер 3
    amount3, _, error3 = get_tmcell_balance(LOGIN3, PASSWORD3)
    if error3:
        results.append(f"❌ Номер 3: {error3}")
    else:
        results.append(f"✅ Номер 3: {amount3:.2f} manat")
        saved_balances[LOGIN3] = amount3
    
    # Сохраняем балансы
    save_balances(saved_balances)
    
    # Отправляем общий результат
    final_message = "📊 <b>Балансы всех номеров</b>\n\n" + "\n".join(results)
    await msg.edit_text(final_message, parse_mode="HTML")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда старт с описанием"""
    await update.message.reply_text(
        "👋 <b>Бот баланса TMCell с отслеживанием пополнений</b>\n\n"
        "Команды:\n"
        "/balance1 - баланс номера 99362489636\n"
        "/balance2 - баланс номера 99361416500\n"
        "/balance3 - баланс номера 99365136133\n"
        "/all - баланс всех номеров сразу\n"
        "/track - включить отслеживание пополнений\n"
        "/stop - выключить отслеживание\n"
        "/status - проверить статус отслеживания",
        parse_mode="HTML"
    )

async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включает отслеживание пополнений"""
    chat_id = update.effective_chat.id
    
    # Удаляем старые задачи для этого чата
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    
    # Создаем новую задачу - проверка каждые 15 минут
    context.job_queue.run_repeating(
        check_balances,
        interval=900,  # 15 минут
        first=10,
        chat_id=chat_id,
        name=str(chat_id)
    )
    
    # Сразу проверим балансы для инициализации
    await check_balances(context.job_queue.jobs()[0] if context.job_queue.jobs() else None)
    
    await update.message.reply_text(
        "✅ <b>Отслеживание пополнений включено!</b>\n"
        "Я буду проверять баланс каждые 15 минут.\n"
        "Если баланс увеличится на 20+ manat - сразу сообщу.",
        parse_mode="HTML"
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выключает отслеживание пополнений"""
    chat_id = update.effective_chat.id
    
    # Удаляем задачи для этого чата
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    
    await update.message.reply_text("🔕 <b>Отслеживание пополнений выключено</b>", parse_mode="HTML")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверяет статус отслеживания"""
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    
    if current_jobs:
        await update.message.reply_text(
            "✅ <b>Отслеживание активно</b>\n"
            "Проверка каждые 15 минут",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            "❌ <b>Отслеживание не активно</b>\n"
            "Используй /track чтобы включить",
            parse_mode="HTML"
        )

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        print("❌ Ошибка: не указан токен бота!")
        return
    
    print("=" * 50)
    print("ЗАПУСК БОТА С ОТСЛЕЖИВАНИЕМ")
    print("=" * 50)
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balance1", balance1_command))
    app.add_handler(CommandHandler("balance2", balance2_command))
    app.add_handler(CommandHandler("balance3", balance3_command))
    app.add_handler(CommandHandler("all", balance_all_command))
    app.add_handler(CommandHandler("track", track_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("status", status_command))
    
    print("✅ Команды зарегистрированы")
    print("📋 Доступные команды: /balance1, /balance2, /balance3, /all, /track, /stop, /status")
    print("🔄 JobQueue активен и готов к работе")
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
