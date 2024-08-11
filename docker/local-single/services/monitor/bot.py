import json
import os

import redis
import telebot
from dotenv import load_dotenv
from aws import get_tg_bot_key, get_main_chat_id

load_dotenv()


bot_token = os.getenv("BOT_TOKEN", get_tg_bot_key())
main_chat_id = os.getenv("MAIN_CHAT_ID", int(get_main_chat_id()))
bot = telebot.TeleBot(bot_token)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")
REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")
REDIS_SYSTEM_Q_NAME = os.getenv("REDIS_SYSTEM_Q_NAME")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def send_plot(plot_file):
    print("Sending plot", plot_file)
    bot.send_photo(main_chat_id, plot_file)


def send_audio_message(audio, message="Loud noise"):
    bot.send_audio(main_chat_id, audio, message)


@bot.message_handler(func=lambda message: message.text == "listen")
def handle_message(message):
    from celeryapps import record_audio
    record_audio.delay()


@bot.message_handler(func=lambda message: message.text == "stats")
def handle_message(message):
    stats = r.lpop(REDIS_SYSTEM_Q_NAME)
    bot.reply_to(message, json.loads(stats))


if __name__ == "__main__":
    print("Bot is running")
    print("System queue name: ", REDIS_SYSTEM_Q_NAME)
    bot.polling()
