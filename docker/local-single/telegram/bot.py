import os
import time
import telebot
from dotenv import load_dotenv

load_dotenv()


bot_token = os.getenv("BOT_TOKEN")
main_chat_id = os.getenv("MAIN_CHAT_ID")
bot = telebot.TeleBot(bot_token)


def send_on_startup():
    bot.send_message(main_chat_id, "Bot is running 🚀")


if __name__ == "__main__":
    time.sleep(30)
    send_on_startup()
    bot.polling()
