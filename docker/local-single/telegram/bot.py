import os
import time

from utils import (
    get_cpu_temperature,
    get_battery,
    get_cpu_usage,
    get_ram_usage,
    get_system_uptime,
)
import telebot
from dotenv import load_dotenv

load_dotenv()


bot_token = os.getenv("BOT_TOKEN")
main_chat_id = os.getenv("MAIN_CHAT_ID")
bot = telebot.TeleBot(bot_token)


def send_on_startup():
    bot.send_message(main_chat_id, "Bot is running 🚀")


@bot.message_handler(func=lambda message: message.text == "stats")
def handle_message(message):
    stats = f"""
🌡️ CPU Temperature: {get_cpu_temperature()}°C
🔋 Battery: {get_battery()}%
📊 CPU Usage: {get_cpu_usage()}%
💾 RAM Usage: {get_ram_usage()}
⏳ System Uptime: {get_system_uptime()}
"""
    bot.reply_to(message, stats)


if __name__ == "__main__":
    time.sleep(30)
    send_on_startup()
    bot.polling()
