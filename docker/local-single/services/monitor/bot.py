import os
import telebot
from dotenv import load_dotenv
from aws import get_tg_bot_key, get_main_chat_id

load_dotenv()


bot_token = os.getenv("BOT_TOKEN", get_tg_bot_key())
main_chat_id = os.getenv("MAIN_CHAT_ID", int(get_main_chat_id()))
bot = telebot.TeleBot(bot_token)


def send_audio_message(audio):
    bot.send_audio(main_chat_id, audio, "Loud noise")
